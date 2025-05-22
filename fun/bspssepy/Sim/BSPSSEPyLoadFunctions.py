# BSPSSEPy Load Functions
# This Python module contains all 'Load' related functions for the BSPSSEPy framework:
#
# 1. GetLoadInfo: Retrieves specific information about loads based on user-specified keys, either from PSSE or BSPSSEPyLoad DataFrame.
#    - Handles cases for single/multiple keys and specific/all loads.
#
# 2. GetLoadInfoPSSE: Fetches load-related data directly from PSSE using the PSSE library.
#
# 3. LoadDisable: Disables a load (sets its status in PSSE to 0) and updates the BSPSSEPyLoad DataFrame.
#
# 4. LoadEnable: Enables a load (sets its status in PSSE to 1) and updates the BSPSSEPyLoad DataFrame.
#
# 5. NewLoad: Adds a new load entry to the PSSE system and updates the BSPSSEPyLoad DataFrame.
#
#
# This module ensures dynamic interaction with PSSE for real-time data, while allowing extended tracking and simulation-specific metadata updates through the BSPSSEPyLoad DataFrame.
#
#    Last Update for this file was on BSPSSEPy Ver 0.2 (27 Dec. 2024)
#
#       BSPSSEPy Application
#       Copyright (c) 2024, Ilyas Farhat
#       by Ilyas Farhat
#
#       This file is part of BSPSSEPy Application.
#       Contact the developer at ilyas.farhat@outlook.com

import psspy
import pandas as pd
from .BSPSSEPyDefaultVariables import *
from Functions.BSPSSEPy.BSPSSEPyDictionary import *
from .BSPSSEPyBrnFunctions import GetBrnInfo
from .BSPSSEPyGenFunctions import GetGenInfo
from .BSPSSEPyTrnFunctions import GetTrnInfo
from .BSPSSEPyBusFunctions import GetBusInfo
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint
import asyncio
from textual.app import App

async def GetLoadInfo(LoadKeys, Load=None, LoadName=None, LoadID=None, BSPSSEPyLoad=None, DebugPrint=False, app=None):
    """
    Retrieves information about loads based on the specified keys.

    Handles various cases for single/multiple keys and specific/all loads:

    Case 1: Single key for a specific load:
        If a single key is requested and a specific load is identified by either LoadName or LoadID,
        this function will return the value associated with the key for that load.

    Case 2: Multiple keys for a specific load:
        If multiple keys are requested and a specific load is identified by either LoadName or LoadID,
        this function will return a pandas dataframe series of values corresponding to the requested keys for that load.

    Case 3: Single key for all loads:
        If a single key is requested and no specific load is identified, the function will return a
        pandas dataframe series of values for the requested key across all loads in the system.

    Case 4: Multiple keys for all loads:
        If multiple keys are requested and no specific load is identified, the function will return
        a pandas dataframe series for all loads with the valeus corresponding to all requested keys.

    Parameters:
        LoadKeys (str or list of str): The key(s) for the required information. Valid keys include PSSE keys and BSPSSEPyLoad columns.
        Load (str, optional): Alternative to LoadName for simplicity.
        LoadName (str, optional): Load Name.
        LoadID (str, optional): Load ID.
        BSPSSEPyLoad (pd.DataFrame, optional): DataFrame containing extended information about loads.
        DebugPrint (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        Depending on the input:
            - A single value (Case 1).
            - A list of values (Case 2 or 3).
            - A dictionary of lists (Case 4).

    Notes:
        - Input strings (e.g., LoadKeys, Load, LoadName) are normalized by stripping extra spaces.
        - The function combines PSSE and BSPSSEPyLoad data if both are available for comprehensive results.
    """
    if DebugPrint:
        bsprint(f"[DEBUG] Retrieving load info for LoadKeys: {LoadKeys}, Load: {Load}, LoadName: {LoadName}, LoadID: {LoadID}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Ensure LoadKeys is a list
    if isinstance(LoadKeys, str):
        LoadKeys = [LoadKeys]

    # Normalize strings to remove extra spaces
    LoadKeys = [key.strip() for key in LoadKeys]
    if isinstance(Load, str) and Load:
        LoadName = Load
    

    
    if LoadName is not None and LoadName:
        LoadName = LoadName.strip()

    # Separate PSSE and BSPSSEPyLoad keys
    ValidPSSEKeys = LoadInfoDic.keys()
    ValidBSPSSEPyKeys = [] if BSPSSEPyLoad is None else BSPSSEPyLoad.columns


    # Add PSSE Keys needed for basic Load operations
    _LoadKeys = ["ID", "LOADNAME"]
    _LoadKeysPSSE = list(_LoadKeys)
    for key in LoadKeys:
        if key in ValidPSSEKeys and key not in _LoadKeysPSSE:
            _LoadKeysPSSE.append(key)

    if DebugPrint:
        bsprint(f"[DEBUG] Fetching PSSE data for keys: {_LoadKeysPSSE}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Ensure no duplicate columns are fetched from PSSE if BSPSSEPyLoad is provided
    if BSPSSEPyLoad is not None and not BSPSSEPyLoad.empty:
        # Remove overlapping keys from the PSSE fetch list
        ValidBSPSSEPyKeys = [key for key in ValidBSPSSEPyKeys if key not in _LoadKeysPSSE]

    if DebugPrint:
        bsprint(f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {ValidBSPSSEPyKeys}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)


    # Fetch PSSE data for the required keys
    PSSEData = {}
    for PSSEKey in _LoadKeysPSSE:
        PSSEData[PSSEKey] = await GetLoadInfoPSSE(PSSEKey, DebugPrint=DebugPrint,app=app)


    # Combine PSSEData and BSPSSEPyTrn (if provided) into a single DataFrame
    if BSPSSEPyLoad is not None and not BSPSSEPyLoad.empty:
        ValidBSPSSEPyLoad = BSPSSEPyLoad[ValidBSPSSEPyKeys]
        PSSEDataDF = pd.DataFrame(PSSEData)
        CombinedData = pd.concat([PSSEDataDF, ValidBSPSSEPyLoad], axis=1)
    else:
        CombinedData = pd.DataFrame(PSSEData)

    if DebugPrint:
        bsprint(f"[DEBUG] Combined Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    

    # Filter CombinedData based on TrnName, FromBus, and ToBus
    if LoadName and LoadID:
        CombinedData = CombinedData[(CombinedData["LOADNAME"].str.strip() == LoadName.strip()) & (CombinedData["ID"].str.strip() == LoadID.strip())]
    elif LoadName or LoadID:
        IdentifierKey = "LOADNAME" if LoadName else "ID"
        IdentifierValue = LoadName.strip() if LoadName else LoadID.strip()
        
        CombinedData = CombinedData[CombinedData[IdentifierKey].str.strip() == IdentifierValue]

    if DebugPrint:
        bsprint(f"[DEBUG] Filtered Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Handle cases based on the number of BrnKeys
    if len(LoadKeys) == 1:
        Key = LoadKeys[0]
        return CombinedData[Key].iloc[0] if len(CombinedData) == 1 else CombinedData[Key]
    else:
        return CombinedData[LoadKeys]


    

async def GetLoadInfoPSSE(aloadString, DebugPrint=False, app=None):
    """
    Retrieves specific load information from PSSE.

    Parameters:
        aloadString (str): Requested information key.
        DebugPrint (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        list or None: A list of the requested information if found, otherwise None.
    """
    if DebugPrint:
        bsprint(f"[DEBUG] Requested load information for aloadString: '{aloadString}'",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Validate aloadString
    if aloadString not in LoadInfoDic:
        bsprint(f"[ERROR] Invalid aloadString '{aloadString}'. Check LoadInfoDic for valid options.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    try:
        # Fetch data type for the key
        ierr, dataType = psspy.aloadtypes([aloadString])
        if ierr != 0:
            bsprint(f"[ERROR] Failed to fetch data type for aloadString '{aloadString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
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
            bsprint(f"[ERROR] Unsupported data type '{dataType[0]}' for aloadString '{aloadString}'.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None

        if ierr != 0:
            bsprint(f"[ERROR] Failed to retrieve data for aloadString '{aloadString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
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


        if DebugPrint:
            bsprint(f"[DEBUG] Successfully retrieved data for '{aloadString}': {data}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return data

    except Exception as e:
        bsprint(f"[ERROR] Exception occurred while retrieving load data: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None


async def LoadDisable(t, BSPSSEPyLoad, LoadName=None, LoadID=None, DebugPrint=False, app=None):
    """
    Disables a load (sets its status to 0) and updates the BSPSSEPyLoad DataFrame.

    Parameters:
        t (float): Current simulation time.
        BSPSSEPyLoad (pd.DataFrame): DataFrame containing load data.
        LoadName (str, optional): Load Name.
        LoadID (str, optional): Load ID.
        DebugPrint (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """
    if DebugPrint:
        bsprint(f"[DEBUG] Starting LoadDisable for LoadName: {LoadName}, LoadID: {LoadID}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()

    LoadRow = await GetLoadInfo(
        LoadKeys=["LOADNAME", "ID", "NUMBER", "STATUS"],
        Load=LoadName,
        LoadID=LoadID,
        BSPSSEPyLoad=BSPSSEPyLoad,
        DebugPrint=DebugPrint,
        app=app)

    if LoadRow is None or len(LoadRow) == 0:
        bsprint(f"[ERROR] Load with Name '{LoadName}' or ID '{LoadID}' not found.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None


    LoadID = LoadRow["ID"].iloc[0]
    LoadBusNumber = int(LoadRow["NUMBER"].iloc[0])
    LoadName = LoadRow["LOADNAME"].iloc[0]
    LoadStatus = LoadRow["STATUS"].iloc[0]

    if DebugPrint:
        bsprint(f"[DEBUG] LoadID: {LoadID}, LoadName: {LoadName}, LoadBusNumber: {LoadBusNumber}, LoadStatus: {LoadStatus} extracted for disabling.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    if LoadStatus != 1:
        bsprint(f"[INFO] Load '{LoadName} at Bus '{LoadBusNumber}' is already disabled.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return 0
    
    # Attempt to disable the load
    try:
        if DebugPrint:
            bsprint(f"[DEBUG] Attempting to disable load '{LoadName}' at bus '{LoadBusNumber}'.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        ierr = psspy.load_chng_7(
                            LoadBusNumber,
                            LoadID,
                            [0] +[DefaultInt]*6,  # Load status (disabled)
                            [DefaultReal]*8,
                            DefaultChar,
                            LoadName)

        if ierr != 0:
            bsprint(f"[ERROR] Failed to disable load '{LoadName or LoadID}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return ierr

        NewStatus = await GetLoadInfo("STATUS", Load=LoadName, LoadID=LoadID, DebugPrint=DebugPrint, app=app)
        if not(BSPSSEPyLoad is None or BSPSSEPyLoad.empty):
            BSPSSEPyLoad.loc[(BSPSSEPyLoad["LOADNAME"] == LoadName) & (BSPSSEPyLoad["ID"] == LoadID), [
                "BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "STATUS"
            ]] = [
                "Disabled",
                "Disable",
                t,
                "Load successfully disabled.",
                NewStatus]

        if DebugPrint:
            bsprint(f"[SUCCESS] Load '{LoadName or LoadID}' successfully disabled. DataFrame updated.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        return ierr
    
    except KeyError as e:
        bsprint(f"[ERROR] Key error while disabling load: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    except Exception as e:
        bsprint(f"[ERROR] Unexpected error while disabling load: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None


async def LoadEnable(t: int,
                     BSPSSEPyLoad: pd.DataFrame,
                     LoadName: str | None=None,
                     LoadID: str | None=None,
                     DebugPrint: bool | None=False,
                     app: App | None=None,
                     BSPSSEPyGen: pd.DataFrame | None = None,
                     BSPSSEPyAGCDF: pd.DataFrame | None = None,
                     ):
    """
    Enables a load (sets its status to 1) and updates the BSPSSEPyLoad DataFrame.

    Parameters:
        t (float): Current simulation time.
        BSPSSEPyLoad (pd.DataFrame): DataFrame containing load data.
        LoadName (str, optional): Load Name.
        LoadID (str, optional): Load ID.
        DebugPrint (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """
    if DebugPrint:
        bsprint(f"[DEBUG] Starting LoadEnable for LoadName: {LoadName}, LoadID: {LoadID}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()

    LoadRow = await GetLoadInfo(
        LoadKeys=["LOADNAME", "ID", "NUMBER", "STATUS"],
        Load=LoadName,
        LoadID=LoadID,
        BSPSSEPyLoad=BSPSSEPyLoad,
        DebugPrint=DebugPrint,
        app=app
        )

    if LoadRow is None or len(LoadRow) == 0:
        bsprint(f"[ERROR] Load with Name '{LoadName}' or ID '{LoadID}' not found.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None


    LoadID = LoadRow["ID"].iloc[0]
    LoadBusNumber = int(LoadRow["NUMBER"].iloc[0])
    LoadName = LoadRow["LOADNAME"].iloc[0]
    LoadStatus = int(LoadRow["STATUS"].iloc[0])

    if DebugPrint:
        bsprint(f"[DEBUG] LoadID: {LoadID}, LoadName: {LoadName}, LoadBusNumber: {LoadBusNumber}, LoadStatus: {LoadStatus} extracted for enabling.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    if LoadStatus != 0:
        bsprint(f"[INFO] Load '{LoadName} at Bus '{LoadBusNumber}' is already enabled.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return 0
    
    # Attempt to disable the load
    try:
        if DebugPrint:
            bsprint(f"[DEBUG] Attempting to enable load '{LoadName}' at bus '{LoadBusNumber}'.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        ierr = psspy.load_chng_7(LoadBusNumber, LoadID, [
            1,  # Load status (enabled)
            DefaultInt, DefaultInt, DefaultInt, DefaultInt, DefaultInt, DefaultInt
        ], [
            DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal
        ], DefaultChar, DefaultChar)

        if ierr != 0:
            bsprint(f"[ERROR] Failed to enable load '{LoadName or LoadID}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return ierr
        

        NewStatus = await GetLoadInfo("STATUS", Load=LoadName, LoadID=LoadID, DebugPrint=DebugPrint,app=app)
        if not(BSPSSEPyLoad is None or BSPSSEPyLoad.empty):
            BSPSSEPyLoad.loc[(BSPSSEPyLoad["LOADNAME"] == LoadName) & (BSPSSEPyLoad["ID"] == LoadID), [
                "BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "STATUS"
            ]] = ["Enabled", "Enable", t, "Load successfully enabled.", NewStatus]

        if DebugPrint:
            bsprint(f"[SUCCESS] Load '{LoadName or LoadID}' successfully enabled. DataFrame updated.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        
        # Update online generators to compensate for the load
        for idx, BSPSSEPyGenRow in BSPSSEPyGen[BSPSSEPyGen["BSPSSEPyStatus"] == 3].iterrows():
            GenBusNum = BSPSSEPyGenRow["NUMBER"]
            GenName = BSPSSEPyGenRow["MCNAME"]
            GenID = BSPSSEPyGenRow["ID"]

            ierrGen, GeneratorMVA_Base = psspy.macdat(GenBusNum, GenID, 'MBASE')

            GenPOPF = BSPSSEPyGenRow["POPF"]
            LERPF = BSPSSEPyGenRow["LERPF"]

            # Fix: Extract a single value instead of a DataFrame
            EffectiveAGCAlpha = BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF["Gen Name"] == GenName, "Alpha"].values[0]

            LERPF = EffectiveAGCAlpha if LERPF == -1 else LERPF

            if not BSPSSEPyGenRow["LoadEnabledResponse"]:
                continue

            # Fix: Await the coroutine to get the actual value
            EffectiveLoad = await GetLoadInfo("TOTALACT", Load=LoadName, DebugPrint=DebugPrint, app=app)

            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            GenPOPFpu = EffectiveLoad.real * LERPF / GeneratorMVA_Base  # ✅ Now works correctly

            from Functions.BSPSSEPy.Sim.BSPSSEPyChannels import FetchChannelValue

            # Fix: Remove .values[0] from PELECChannel access
            GenP = await FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"]), DebugPrint=DebugPrint, app=app) * GeneratorMVA_Base

            if DebugPrint:
                bsprint(f"[DEBUG] Using generator model ramp-rate for generator: {GenName} - Target Power: {GenPOPF} MW", app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            # Apply the target output power
            ierrGen = psspy.increment_gref(GenBusNum, GenID, GenPOPFpu)

            if ierrGen != 0:
                bsprint(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierrGen}", app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)

        
        return ierr
    
    except KeyError as e:
        bsprint(f"[ERROR] Key error while enabling load: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    except Exception as e:
        bsprint(f"[ERROR] Unexpected error while enabling load: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None






async def NewLoad(LoadID="ZZ", LoadName=None, BSPSSEPyLoad=None, BusName=None, BusNumber=None, ElementName=None, ElementType=None, PowerArray=[1], UseFromBus=True, t = 0, DebugPrint=False, app=None):
    """
    Creates a new load at a specified location. If an element is passed, the load will be created
    at the same bus where the element is connected.

    Parameters:
        LoadID (str, optional): Unique identifier for the load (default: "ZZ").
        LoadName (str, optional): Name of the load (default: None).
        BSPSSEPyLoad (pd.DataFrame): DataFrame to store the load data.
        BusName (str, optional): Name of the bus where the load will be created.
        BusNumber (int, optional): Number of the bus where the load will be created.
        ElementName (str, optional): Name of the element (e.g., generator) to locate the bus.
        ElementType (str, optional): Type of the element (e.g., "Gen", "TWTF", "Load").
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
        DebugPrint (bool, optional): Enable detailed debug output (default: False).

    Returns:
        int: ierr value returned by PSSE (0 for success).
    """
    if BSPSSEPyLoad is None:
        bsprint("[ERROR] BSPSSEPyLoad DataFrame must be provided.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    if DebugPrint:
        bsprint(f"[DEBUG] Starting NewLoad with LoadID: {LoadID}, LoadName: {LoadName}, BusName: {BusName}, BusNumber: {BusNumber}, ElementName: {ElementName}, ElementType: {ElementType}, PowerArray: {PowerArray}, UseFromBus: {UseFromBus}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Determine bus location if an element is provided
    if BusName:
        if DebugPrint:
            bsprint(f"[DEBUG] Resolving BusNumber for BusName: {BusName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        BusNumber = await GetBusInfo(BusKeys="NUMBER", BusName=BusName, DebugPrint=DebugPrint,app=app)
        if BusNumber is None or not BusNumber:
            bsprint(f"[ERROR] Bus '{BusName}' must resolve to a BusNumber.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None
    elif BusNumber:
        if DebugPrint:
            bsprint(f"[DEBUG] Resolving BusName for BusNumber: {BusNumber}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        BusName = await GetBusInfo(BusKeys="NAME", BusNumber=BusNumber, DebugPrint=DebugPrint,app=app)
        if BusName is None or not BusName:
            bsprint(f"[ERROR] Bus '{BusNumber}' must resolve to a BusName.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None
    if ElementName and ElementType:
        if DebugPrint:
            bsprint(f"[DEBUG] Determining bus location for ElementName: {ElementName}, ElementType: {ElementType}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        if ElementType.lower() in ['gen', 'generator', 'g']:
            ElementRow = await GetGenInfo(["NUMBER", "NAME"], GenName=ElementName, DebugPrint=DebugPrint,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not BusNumber or BusNumber == None:
                    BusNumber = int(ElementRow["NUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["NAME"].values[0]
                LoadID = "GL"  # Generator Load
        elif ElementType.lower() in ['twtf', 'twtransformer', 'twtran', 'twtrans', 'trn']:
            ElementRow = await GetTrnInfo(["FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"], TrnName=ElementName, DebugPrint=DebugPrint,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not BusNumber or BusNumber == None:
                    BusNumber = int(ElementRow["FROMNUMBER"].values[0] if UseFromBus else ElementRow["TONUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["FROMNAME"].values[0] if UseFromBus else ElementRow["TONAME"].values[0]
                LoadID = "TL"  # Transformer Load
        elif ElementType.lower() in ['branch', 'line', 'brn']:
            ElementRow = await GetBrnInfo(["FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"], BranchName=ElementName, DebugPrint=DebugPrint,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not BusNumber or BusNumber == None:
                    BusNumber = int(ElementRow["FROMNUMBER"].values[0] if UseFromBus else ElementRow["TONUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["FROMNAME"].values[0] if UseFromBus else ElementRow["TONAME"].values[0]
                LoadID = "BL"  # Branch Load
        elif ElementType.lower() in ['load']:
            ElementRow = await GetLoadInfo(["NUMBER", "NAME"], LoadName=ElementName, DebugPrint=DebugPrint,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not BusNumber or BusNumber == None:
                    BusNumber = int(ElementRow["NUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["NAME"].values[0]
                LoadID = "LL"  # Load tied to another load
        elif ElementType.lower() in ['bus']:
            ElementRow = await GetBusInfo(["NUMBER", "NAME"], BusName=ElementName, DebugPrint=DebugPrint,app=app)
            if not ElementRow.empty and ElementRow is not None:
                if not BusNumber or BusNumber == None:
                    BusNumber = int(ElementRow["NUMBER"].values[0])
                if not BusName or BusName == None:
                    BusName = ElementRow["NAME"].values[0]
                LoadID = "UL"  # Load tied to a bus
        else:
            bsprint(f"[ERROR] Unsupported ElementType specified: {ElementType}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None

        if not BusNumber or not BusName:
            bsprint(f"[ERROR] Element '{ElementName}' of type '{ElementType}' not found.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None
        if DebugPrint:
            bsprint(f"[DEBUG] Resolved BusNumber: {BusNumber}, BusName: {BusName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
    elif BusName:
        if DebugPrint:
            bsprint(f"[DEBUG] Resolving BusNumber for BusName: {BusName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        BusNumber = await GetBusInfo(BusKeys="NUMBER", BusName=BusName, DebugPrint=DebugPrint,app=app)
        if BusNumber is None or not BusNumber:
            bsprint(f"[ERROR] Bus '{BusName}' must resolve to a BusNumber.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None
    elif BusNumber:
        if DebugPrint:
            bsprint(f"[DEBUG] Resolving BusName for BusNumber: {BusNumber}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        BusName = await GetBusInfo(BusKeys="NAME", BusNumber=BusNumber, DebugPrint=DebugPrint,app=app)
        if BusName is None or not BusName:
            bsprint(f"[ERROR] Bus '{BusNumber}' must resolve to a BusName.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None
    else:
        bsprint("[ERROR] Insufficient data to determine bus location.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    # Generate default LoadName if not provided
    if not LoadName:
        LoadName = f"CL{ElementName or BusName}"  # CustomLoad
        if DebugPrint:
            bsprint(f"[DEBUG] Generated default LoadName: {LoadName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Process PowerArray inputs
    DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()
    PL, QL, IP, IQ, YP, YQ, PowerFactor = [DefaultReal] * 6 + [None]

    if PowerArray:
        if len(PowerArray) >= 1: PL = PowerArray[0]
        if len(PowerArray) >= 2: QL = PowerArray[1]
        if len(PowerArray) >= 3: IP = PowerArray[2]
        if len(PowerArray) >= 4: IQ = PowerArray[3]
        if len(PowerArray) >= 5: YP = PowerArray[4]
        if len(PowerArray) >= 6: YQ = PowerArray[5]
        if len(PowerArray) >= 7: PowerFactor = PowerArray[6]
        if DebugPrint:
            bsprint(f"[DEBUG] Processed PowerArray: PL={PL}, QL={QL}, IP={IP}, IQ={IQ}, YP={YP}, YQ={YQ}, PowerFactor={PowerFactor}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

    ierr = psspy.load_data_7(
        int(BusNumber),
        LoadID,
        [0, DefaultInt, DefaultInt, DefaultInt, 1, 0, 0],
        [PL, QL, IP, IQ, YP, YQ, DefaultReal, DefaultReal],
        DefaultChar,
        LoadName
    )
    if ierr != 0:
        bsprint(f"[ERROR] Failed to create load '{LoadName}' at bus '{BusName}' (BusNumber: {BusNumber}).",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return ierr
    if DebugPrint:
        bsprint(f"[DEBUG] Successfully created load in PSSE: LoadName={LoadName}, BusNumber={BusNumber}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Update BSPSSEPyLoad DataFrame
    NewRow = {
        "ID": LoadID,
        "LOADNAME": LoadName,
        "NUMBER": BusNumber,
        "NAME": BusName,
        "STATUS": 1,
        "BSPSSEPyStatus_0": "Enabled",
        "BSPSSEPyStatus": "Enabled",
        "BSPSSEPyLastAction": "NewLoad",
        "BSPSSEPyLastActionTime": t,
        "BSPSSEPySimulationNotes": "New load added.",
        "BSPSSEPyTiedDeviceName": ElementName if ElementName else None,
        "BSPSSEPyTiedDeviceType": ElementType if ElementType else None
    }
    BSPSSEPyLoad = pd.concat([BSPSSEPyLoad, pd.DataFrame([NewRow])], axis=0, ignore_index=True)
    if DebugPrint:
        bsprint(f"[DEBUG] New load '{LoadName}' added successfully at bus '{BusName}' (BusNumber: {BusNumber}). DataFrame updated.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    return BSPSSEPyLoad, ierr