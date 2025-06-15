# BSPSSEPy load Functions
# This Python module contains all 'load' related functions for the BSPSSEPy framework:
#
# 1. get_load_info: Retrieves specific information about loads based on user-specified keys, either from PSSE or bspssepy_load DataFrame.
#    - Handles cases for single/multiple keys and specific/all loads.
#
# 2. get_load_info_psse: Fetches load-related data directly from PSSE using the PSSE library.
#
# 3. LoadDisable: Disables a load (sets its status in PSSE to 0) and updates the bspssepy_load DataFrame.
#
# 4. loadEnable: Enables a load (sets its status in PSSE to 1) and updates the bspssepy_load DataFrame.
#
# 5. Newload: Adds a new load entry to the PSSE system and updates the bspssepy_load DataFrame.
#
#
# This module ensures dynamic interaction with PSSE for real-time data, while allowing extended tracking and simulation-specific metadata updates through the bspssepy_load DataFrame.
#
#    Last Update for this file was on BSPSSEPy Ver 0.2 (27 Dec. 2024)
#
#       BSPSSEPy Application
#       Copyright (c) 2024, Ilyas Farhat
#       by Ilyas Farhat
#
#       This file is part of BSPSSEPy Application.
#       Contact the developer at ilyas.farhat@outlook.com

# pyright: reportMissingImports=false
import psspy  # noqa: F401 pylint: disable=import-error
import pandas as pd
from textual.app import App
import asyncio
from fun.bspssepy.bspssepy_dict import *

from .bspssepy_brn_funs import get_brn_info
from .bspssepy_gen_funs import GetGenInfo
from .bspssepy_trn_funs import GetTrnInfo
from .bspssepy_bus_funs import get_bus_info
from fun.bspssepy.app.app_helper_funs import bp
from .bspssepy_default_vars import bspssepy_default_vars_fun


async def get_load_info(
    load_keys: str | list[str],
    load: str | None = None,
    LOADNAME: str | None = None,
    load_id: str | None = None,
    bspssepy_load: pd.DataFrame | None = None,
    debug_print: bool = False,
    app: App | None = None
):
    """
    Retrieves information about loads based on the specified keys.

    Handles various cases for single/multiple keys and specific/all loads:

    Case 1: Single key for a specific load:
        If a single key is requested and a specific load is identified by either LOADNAME or load_id,
        this function will return the value associated with the key for that load.

    Case 2: Multiple keys for a specific load:
        If multiple keys are requested and a specific load is identified by either LOADNAME or load_id,
        this function will return a pandas dataframe series of values corresponding to the requested keys for that load.

    Case 3: Single key for all loads:
        If a single key is requested and no specific load is identified, the function will return a
        pandas dataframe series of values for the requested key across all loads in the system.

    Case 4: Multiple keys for all loads:
        If multiple keys are requested and no specific load is identified, the function will return
        a pandas dataframe series for all loads with the valeus corresponding to all requested keys.

    Parameters:
        load_keys (str or list of str): The key(s) for the required information. Valid keys include PSSE keys and bspssepy_load columns.
        load (str, optional): Alternative to LOADNAME for simplicity.
        LOADNAME (str, optional): load Name.
        load_id (str, optional): load ID.
        bspssepy_load (pd.DataFrame, optional): DataFrame containing extended information about loads.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        Depending on the input:
            - A single value (Case 1).
            - A list of values (Case 2 or 3).
            - A dictionary of lists (Case 4).

    Notes:
        - Input strings (e.g., load_keys, load, LOADNAME) are normalized by stripping extra spaces.
        - The function combines PSSE and bspssepy_load data if both are available for comprehensive results.
    """
    if debug_print:
        bp(f"[DEBUG] Retrieving load info for load_keys: {load_keys}, load: {load}, LOADNAME: {LOADNAME}, load_id: {load_id}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure load_keys is a list
    if isinstance(load_keys, str):
        load_keys = [load_keys]

    # Normalize strings to remove extra spaces
    load_keys = [key.strip() for key in load_keys]
    if isinstance(load, str) and load:
        LOADNAME = load
    

    
    if LOADNAME is not None and LOADNAME:
        LOADNAME = LOADNAME.strip()

    # Separate PSSE and bspssepy_load keys
    ValidPSSEKeys = load_info_dict.keys()
    ValidBSPSSEPyKeys = [] if bspssepy_load is None else bspssepy_load.columns


    # Add PSSE Keys needed for basic load operations
    _load_keys = ["ID", "LOADNAME"]
    _load_keysPSSE = list(_load_keys)
    for key in load_keys:
        if key in ValidPSSEKeys and key not in _load_keysPSSE:
            _load_keysPSSE.append(key)

    if debug_print:
        bp(f"[DEBUG] Fetching PSSE data for keys: {_load_keysPSSE}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure no duplicate columns are fetched from PSSE if bspssepy_load is provided
    if bspssepy_load is not None and not bspssepy_load.empty:
        # Remove overlapping keys from the PSSE fetch list
        ValidBSPSSEPyKeys = [key for key in ValidBSPSSEPyKeys if key not in _load_keysPSSE]

    if debug_print:
        bp(f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {ValidBSPSSEPyKeys}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)


    # Fetch PSSE data for the required keys
    PSSEData = {}
    for PSSEKey in _load_keysPSSE:
        PSSEData[PSSEKey] = await get_load_info_psse(PSSEKey, debug_print=debug_print,app=app)


    # Combine PSSEData and bspssepy_trn (if provided) into a single DataFrame
    if bspssepy_load is not None and not bspssepy_load.empty:
        Validbspssepy_load = bspssepy_load[ValidBSPSSEPyKeys]
        PSSEDataDF = pd.DataFrame(PSSEData)
        CombinedData = pd.concat([PSSEDataDF, Validbspssepy_load], axis=1)
    else:
        CombinedData = pd.DataFrame(PSSEData)

    if debug_print:
        bp(f"[DEBUG] Combined Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    

    # Filter CombinedData based on TrnName, FromBus, and ToBus
    if LOADNAME and load_id:
        CombinedData = CombinedData[(CombinedData["LOADNAME"].str.strip() == LOADNAME.strip()) & (CombinedData["ID"].str.strip() == load_id.strip())]
    elif LOADNAME or load_id:
        IdentifierKey = "LOADNAME" if LOADNAME else "ID"
        IdentifierValue = LOADNAME.strip() if LOADNAME else load_id.strip()
        
        CombinedData = CombinedData[CombinedData[IdentifierKey].str.strip() == IdentifierValue]

    if debug_print:
        bp(f"[DEBUG] Filtered Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Handle cases based on the number of BrnKeys
    if len(load_keys) == 1:
        Key = load_keys[0]
        return CombinedData[Key].iloc[0] if len(CombinedData) == 1 else CombinedData[Key]
    else:
        return CombinedData[load_keys]


    

async def get_load_info_psse(aloadString, debug_print=False, app=None):
    """
    Retrieves specific load information from PSSE.

    Parameters:
        aloadString (str): Requested information key.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        list or None: A list of the requested information if found, otherwise None.
    """
    if debug_print:
        bp(f"[DEBUG] Requested load information for aloadString: '{aloadString}'",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Validate aloadString
    if aloadString not in load_info_dict:
        bp(f"[ERROR] Invalid aloadString '{aloadString}'. Check load_info_dict for valid options.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    try:
        # Fetch data type for the key
        ierr, dataType = psspy.aloadtypes([aloadString])
        if ierr != 0:
            bp(f"[ERROR] Failed to fetch data type for aloadString '{aloadString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        # Retrieve data based on type
        if dataType[0] == 'I':
            ierr, data = psspy.aloadint(-1, 4, [aloadString])
        elif dataType[0] == 'R':
            ierr, data = psspy.aloadreal(-1, 4, [aloadString])
        elif dataType[0] == 'C':
            ierr, data = psspy.aloadchar(-1, 4, [aloadString])
        elif dataType[0] == 'X':
            ierr, data = psspy.aloadcplx(-1, 4, [aloadString])
        else:
            bp(f"[ERROR] Unsupported data type '{dataType[0]}' for aloadString '{aloadString}'.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if ierr != 0:
            bp(f"[ERROR] Failed to retrieve data for aloadString '{aloadString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        # Check if data is a list containing a single nested list
        if isinstance(data, list) and len(data) == 1 and isinstance(data[0], list):
            data = data[0]  # Flatten the list

        # Check if data is a list
        if isinstance(data, list):
            # Check if the list contains strings
            if all(isinstance(item, str) for item in data):
                # Strip whitespace from each string in the list
                data = [item.strip() for item in data]


        if debug_print:
            bp(f"[DEBUG] Successfully retrieved data for '{aloadString}': {data}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        return data

    except Exception as e:
        bp(f"[ERROR] Exception occurred while retrieving load data: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def LoadDisable(t, bspssepy_load, LOADNAME=None, load_id=None, debug_print=False, app=None):
    """
    Disables a load (sets its status to 0) and updates the bspssepy_load DataFrame.

    Parameters:
        t (float): Current simulation time.
        bspssepy_load (pd.DataFrame): DataFrame containing load data.
        LOADNAME (str, optional): load Name.
        load_id (str, optional): load ID.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """
    if debug_print:
        bp(f"[DEBUG] Starting loadDisable for LOADNAME: {LOADNAME}, load_id: {load_id}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    default_int, default_real, default_char = bspssepy_default_vars_fun()

    loadRow = await get_load_info(
        load_keys=["LOADNAME", "ID", "NUMBER", "STATUS"],
        load=LOADNAME,
        load_id=load_id,
        bspssepy_load=bspssepy_load,
        debug_print=debug_print,
        app=app)

    if loadRow is None or len(loadRow) == 0:
        bp(f"[ERROR] load with Name '{LOADNAME}' or ID '{load_id}' not found.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


    load_id = loadRow["ID"].iloc[0]
    loadBusNumber = int(loadRow["NUMBER"].iloc[0])
    LOADNAME = loadRow["LOADNAME"].iloc[0]
    loadStatus = loadRow["STATUS"].iloc[0]

    if debug_print:
        bp(f"[DEBUG] load_id: {load_id}, LOADNAME: {LOADNAME}, loadBusNumber: {loadBusNumber}, loadStatus: {loadStatus} extracted for disabling.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    if loadStatus != 1:
        bp(f"[INFO] load '{LOADNAME} at Bus '{loadBusNumber}' is already disabled.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0
    
    # Attempt to disable the load
    try:
        if debug_print:
            bp(f"[DEBUG] Attempting to disable load '{LOADNAME}' at bus '{loadBusNumber}'.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        ierr = psspy.load_chng_7(
                            loadBusNumber,
                            load_id,
                            [0] +[default_int]*6,  # load status (disabled)
                            [default_real]*8,
                            default_char,
                            LOADNAME)

        if ierr != 0:
            bp(f"[ERROR] Failed to disable load '{LOADNAME or load_id}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return ierr

        NewStatus = await get_load_info("STATUS", load=LOADNAME, load_id=load_id, debug_print=debug_print, app=app)
        if not(bspssepy_load is None or bspssepy_load.empty):
            bspssepy_load.loc[(bspssepy_load["LOADNAME"] == LOADNAME) & (bspssepy_load["ID"] == load_id), [
                "BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "STATUS"
            ]] = [
                "Disabled",
                "Disable",
                t,
                "load successfully disabled.",
                NewStatus]

        if debug_print:
            bp(f"[SUCCESS] load '{LOADNAME or load_id}' successfully disabled. DataFrame updated.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        return ierr
    
    except KeyError as e:
        bp(f"[ERROR] Key error while disabling load: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    except Exception as e:
        bp(f"[ERROR] Unexpected error while disabling load: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def LoadEnable(t: int,
                     bspssepy_load: pd.DataFrame,
                     LOADNAME: str | None=None,
                     load_id: str | None=None,
                     debug_print: bool | None=False,
                     app: App | None=None,
                     bspssepy_gen: pd.DataFrame | None = None,
                     bspssepy_agc: pd.DataFrame | None = None,
                     ):
    """
    Enables a load (sets its status to 1) and updates the bspssepy_load DataFrame.

    Parameters:
        t (float): Current simulation time.
        bspssepy_load (pd.DataFrame): DataFrame containing load data.
        LOADNAME (str, optional): load Name.
        load_id (str, optional): load ID.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """
    if debug_print:
        bp(f"[DEBUG] Starting loadEnable for LOADNAME: {LOADNAME}, load_id: {load_id}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    default_int, default_real, default_char = bspssepy_default_vars_fun()

    loadRow = await get_load_info(
        load_keys=["LOADNAME", "ID", "NUMBER", "STATUS"],
        load=LOADNAME,
        load_id=load_id,
        bspssepy_load=bspssepy_load,
        debug_print=debug_print,
        app=app
        )

    if loadRow is None or len(loadRow) == 0:
        bp(f"[ERROR] load with Name '{LOADNAME}' or ID '{load_id}' not found.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


    load_id = loadRow["ID"].iloc[0]
    loadBusNumber = int(loadRow["NUMBER"].iloc[0])
    LOADNAME = loadRow["LOADNAME"].iloc[0]
    loadStatus = int(loadRow["STATUS"].iloc[0])

    if debug_print:
        bp(f"[DEBUG] load_id: {load_id}, LOADNAME: {LOADNAME}, loadBusNumber: {loadBusNumber}, loadStatus: {loadStatus} extracted for enabling.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    if loadStatus != 0:
        bp(f"[INFO] load '{LOADNAME} at Bus '{loadBusNumber}' is already enabled.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0
    
    # Attempt to enable the load
    try:
        if debug_print:
            bp(f"[DEBUG] Attempting to enable load '{LOADNAME}' at bus '{loadBusNumber}'.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        ierr = psspy.load_chng_7(loadBusNumber, load_id, [
            1,  # load status (enabled)
            default_int, default_int, default_int, default_int, default_int, default_int
        ], [
            default_real, default_real, default_real, default_real, default_real, default_real, default_real, default_real
        ], default_char, default_char)

        if ierr != 0:
            bp(f"[ERROR] Failed to enable load '{LOADNAME or load_id}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return ierr
        

        NewStatus = await get_load_info("STATUS", load=LOADNAME, load_id=load_id, debug_print=debug_print,app=app)
        if not(bspssepy_load is None or bspssepy_load.empty):
            bspssepy_load.loc[(bspssepy_load["LOADNAME"] == LOADNAME) & (bspssepy_load["ID"] == load_id), [
                "BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "STATUS"
            ]] = ["Enabled", "Enable", t, "load successfully enabled.", NewStatus]

        if debug_print:
            bp(f"[SUCCESS] load '{LOADNAME or load_id}' successfully enabled. DataFrame updated.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        
        # Update online generators to compensate for the load
        for idx, BSPSSEPyGenRow in bspssepy_gen[bspssepy_gen["BSPSSEPyStatus"] == 3].iterrows():
            GenBusNum = BSPSSEPyGenRow["NUMBER"]
            GenName = BSPSSEPyGenRow["MCNAME"]
            GenID = BSPSSEPyGenRow["ID"]

            ierrGen, gen_mva_base = psspy.macdat(GenBusNum, GenID, 'MBASE')

            GenPOPF = BSPSSEPyGenRow["POPF"]
            LERPF = BSPSSEPyGenRow["LERPF"]

            # Fix: Extract a single value instead of a DataFrame
            EffectiveAGCAlpha = bspssepy_agc.loc[bspssepy_agc["Gen Name"] == GenName, "Alpha"].values[0]

            LERPF = EffectiveAGCAlpha if LERPF == -1 else LERPF

            if not BSPSSEPyGenRow["LoadEnabledResponse"]:
                continue

            # Fix: Await the coroutine to get the actual value
            Effectiveload = await get_load_info("TOTALACT", load=LOADNAME, debug_print=debug_print, app=app)

            await asyncio.sleep(app.async_print_delay if app else 0)

            GenPOPFpu = Effectiveload.real * LERPF / gen_mva_base  # ✅ Now works correctly

            from fun.bspssepy.sim.bspssepy_channels import FetchChannelValue

            # Fix: Remove .values[0] from PELECChannel access
            GenP = await FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"]), debug_print=debug_print, app=app) * gen_mva_base

            if debug_print:
                bp(f"[DEBUG] Using generator model ramp-rate for generator: {GenName} - Target Power: {GenPOPF} MW", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            # Apply the target output power
            ierrGen = psspy.increment_gref(GenBusNum, GenID, GenPOPFpu)

            if ierrGen != 0:
                bp(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierrGen}", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)

        
        return ierr
    
    except KeyError as e:
        bp(f"[ERROR] Key error while enabling load: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    except Exception as e:
        bp(f"[ERROR] Unexpected error while enabling load: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None






async def NewLoad(load_id="ZZ", LOADNAME=None, bspssepy_load=None, BusName=None, bus_num=None, ElementName=None, ElementType=None, PowerArray=[1], UseFromBus=True, t = 0, debug_print=False, app=None):
    """
    Creates a new load at a specified location. If an element is passed, the load will be created
    at the same bus where the element is connected.

    Parameters:
        load_id (str, optional): Unique identifier for the load (default: "ZZ").
        LOADNAME (str, optional): Name of the load (default: None).
        bspssepy_load (pd.DataFrame): DataFrame to store the load data.
        BusName (str, optional): Name of the bus where the load will be created.
        bus_num (int, optional): Number of the bus where the load will be created.
        ElementName (str, optional): Name of the element (e.g., generator) to locate the bus.
        ElementType (str, optional): Type of the element (e.g., "Gen", "TWTF", "load").
             PowerArray (list, optional): A list containing power-related parameters as follows:
            [PL, QL, IP, IQ, YP, YQ, Power Factor (optional)]
            - PL: Active power in MW (optional).
            - QL: Reactive power in MVar (optional).
            - IP: Constant current active load (optional).
            - IQ: Constant current reactive load (optional).
            - YP: Constant admittance active load (optional).
            - YQ: Constant admittance reactive load (optional).
            - Power Factor: The power factor to calculate missing PL or QL (optional).
            This defaults to 1.0 for P and 0 for L.

        UseFromBus (bool, optional): If True, use the "from bus" for branches/transformers; otherwise, use "to bus". Default is True.
        debug_print (bool, optional): Enable detailed debug output (default: False).

    Returns:
        int: ierr value returned by PSSE (0 for success).
    """
    if bspssepy_load is None:
        bp("[ERROR] bspssepy_load DataFrame must be provided.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    if debug_print:
        bp(f"[DEBUG] Starting Newload with load_id: {load_id}, LOADNAME: {LOADNAME}, BusName: {BusName}, bus_num: {bus_num}, ElementName: {ElementName}, ElementType: {ElementType}, PowerArray: {PowerArray}, UseFromBus: {UseFromBus}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Determine bus location if an element is provided
    if BusName:
        if debug_print:
            bp(f"[DEBUG] Resolving bus_num for BusName: {BusName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        bus_num = await get_bus_info(BusKeys="NUMBER", BusName=BusName, debug_print=debug_print,app=app)
        if bus_num is None or not bus_num:
            bp(f"[ERROR] Bus '{BusName}' must resolve to a bus_num.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    elif bus_num:
        if debug_print:
            bp(f"[DEBUG] Resolving BusName for bus_num: {bus_num}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        BusName = await get_bus_info(BusKeys="NAME", bus_num=bus_num, debug_print=debug_print,app=app)
        if BusName is None or not BusName:
            bp(f"[ERROR] Bus '{bus_num}' must resolve to a BusName.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    if ElementName and ElementType:
        if debug_print:
            bp(f"[DEBUG] Determining bus location for ElementName: {ElementName}, ElementType: {ElementType}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        if ElementType.lower() in ['gen', 'generator', 'g']:
            ElementRow = await GetGenInfo(["NUMBER", "NAME"], GenName=ElementName, debug_print=debug_print,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(ElementRow["NUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["NAME"].values[0]
                load_id = "GL"  # Generator load
        elif ElementType.lower() in ['twtf', 'twtransformer', 'twtran', 'twtrans', 'trn']:
            ElementRow = await GetTrnInfo(["FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"], TrnName=ElementName, debug_print=debug_print,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(ElementRow["FROMNUMBER"].values[0] if UseFromBus else ElementRow["TONUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["FROMNAME"].values[0] if UseFromBus else ElementRow["TONAME"].values[0]
                load_id = "TL"  # Transformer load
        elif ElementType.lower() in ['branch', 'line', 'brn']:
            ElementRow = await get_brn_info(["FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"], BranchName=ElementName, debug_print=debug_print,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(ElementRow["FROMNUMBER"].values[0] if UseFromBus else ElementRow["TONUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["FROMNAME"].values[0] if UseFromBus else ElementRow["TONAME"].values[0]
                load_id = "BL"  # Branch load
        elif ElementType.lower() in ['load']:
            ElementRow = await get_load_info(["NUMBER", "NAME"], LOADNAME=ElementName, debug_print=debug_print,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(ElementRow["NUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["NAME"].values[0]
                load_id = "LL"  # load tied to another load
        elif ElementType.lower() in ['bus']:
            ElementRow = await get_bus_info(["NUMBER", "NAME"], BusName=ElementName, debug_print=debug_print,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(ElementRow["NUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["NAME"].values[0]
                load_id = "UL"  # load tied to a bus
        else:
            bp(f"[ERROR] Unsupported ElementType specified: {ElementType}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if not bus_num or not BusName:
            bp(f"[ERROR] Element '{ElementName}' of type '{ElementType}' not found.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
        if debug_print:
            bp(f"[DEBUG] Resolved bus_num: {bus_num}, BusName: {BusName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
    elif BusName:
        if debug_print:
            bp(f"[DEBUG] Resolving bus_num for BusName: {BusName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        bus_num = await get_bus_info(BusKeys="NUMBER", BusName=BusName, debug_print=debug_print,app=app)
        if bus_num is None or not bus_num:
            bp(f"[ERROR] Bus '{BusName}' must resolve to a bus_num.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    elif bus_num:
        if debug_print:
            bp(f"[DEBUG] Resolving BusName for bus_num: {bus_num}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        BusName = await get_bus_info(BusKeys="NAME", bus_num=bus_num, debug_print=debug_print,app=app)
        if BusName is None or not BusName:
            bp(f"[ERROR] Bus '{bus_num}' must resolve to a BusName.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    else:
        bp("[ERROR] Insufficient data to determine bus location.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Generate default LOADNAME if not provided
    if not LOADNAME:
        LOADNAME = f"CL{ElementName or BusName}"  # Customload
        if debug_print:
            bp(f"[DEBUG] Generated default LOADNAME: {LOADNAME}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

    # Process PowerArray inputs
    default_int, default_real, default_char = bspssepy_default_vars_fun()
    PL, QL, IP, IQ, YP, YQ, PowerFactor = [default_real] * 6 + [None]

    if PowerArray:
        if len(PowerArray) >= 1: PL = PowerArray[0]
        if len(PowerArray) >= 2: QL = PowerArray[1]
        if len(PowerArray) >= 3: IP = PowerArray[2]
        if len(PowerArray) >= 4: IQ = PowerArray[3]
        if len(PowerArray) >= 5: YP = PowerArray[4]
        if len(PowerArray) >= 6: YQ = PowerArray[5]
        if len(PowerArray) >= 7: PowerFactor = PowerArray[6]
        if debug_print:
            bp(f"[DEBUG] Processed PowerArray: PL={PL}, QL={QL}, IP={IP}, IQ={IQ}, YP={YP}, YQ={YQ}, PowerFactor={PowerFactor}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

    ierr = psspy.load_data_7(
        int(bus_num),
        load_id,
        [0, default_int, default_int, default_int, 1, 0, 0],
        [PL, QL, IP, IQ, YP, YQ, default_real, default_real],
        default_char,
        LOADNAME
    )
    if ierr != 0:
        bp(f"[ERROR] Failed to create load '{LOADNAME}' at bus '{BusName}' (bus_num: {bus_num}).",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return ierr
    if debug_print:
        bp(f"[DEBUG] Successfully created load in PSSE: LOADNAME={LOADNAME}, bus_num={bus_num}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Update bspssepy_load DataFrame
    NewRow = {
        "ID": load_id,
        "LOADNAME": LOADNAME,
        "NUMBER": bus_num,
        "NAME": BusName,
        "STATUS": 1,
        "BSPSSEPyStatus_0": "Enabled",
        "BSPSSEPyStatus": "Enabled",
        "BSPSSEPyLastAction": "Newload",
        "BSPSSEPyLastActionTime": t,
        "BSPSSEPySimulationNotes": "New load added.",
        "BSPSSEPyTiedDeviceName": ElementName if ElementName else None,
        "BSPSSEPyTiedDeviceType": ElementType if ElementType else None
    }
    bspssepy_load = pd.concat([bspssepy_load, pd.DataFrame([NewRow])], axis=0, ignore_index=True)
    if debug_print:
        bp(f"[DEBUG] New load '{LOADNAME}' added successfully at bus '{BusName}' (bus_num: {bus_num}). DataFrame updated.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    return bspssepy_load, ierr