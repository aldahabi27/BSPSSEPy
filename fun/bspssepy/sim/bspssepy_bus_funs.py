# BSPSSEPy Bus Functions
# This Python module contains all 'Bus' related functions for the BSPSSEPy framework:
#
# 1. get_bus_info: Retrieves specific information about buses based on user-specified keys, either from PSSE or bspssepy_bus dataFrame.
#    - Handles cases for single/multiple keys and specific/all buses.
#
# 2. get_bus_infoPSSE: Fetches bus-related data directly from PSSE using the PSSE library.
#
# 3. BusTrip: Trips a bus (sets its status in PSSE to 4) and updates the bspssepy_bus dataFrame.
#
# 4. BusClose: Resets a bus to its original type (restores the type from BSPSSEPyType in bspssepy_bus) and updates the bspssepy_bus dataFrame.
#
# This module ensures dynamic interaction with PSSE for real-time data, while allowing extended tracking and simulation-specific metadata updates through the bspssepy_bus dataFrame.
#
# Key Features:
# - Integrates real-time data retrieval from PSSE and local metadata updates.
# - Supports flexible query formats including bus names or numbers.
# - Logs detailed debug information for easy troubleshooting.
#
#    Last Update for this file was on BSPSSEPy Ver 0.2 (26 Dec. 2024)
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
import numbers
import asyncio
from fun.bspssepy.bspssepy_dict import *
from fun.bspssepy.sim.bspssepy_default_vars import *
from fun.bspssepy.app.bspssepy_print import bspssepy_print as bp

async def get_bus_info(
    BusKeys, # The key(s) for the required information of the bus
    Bus=None,    # Bus identifier --> could be BusName or bus_num (optional)
    BusName=None,    # Bus Name (optional)
    bus_num=None,  # Bus Number (optional)
    bspssepy_bus=None,    # bspssepy_bus dataFrane containing BSPSSEPy extra
                         # information associated with the Bus (optional) 
    debug_print=False,    # Enable detailed debug output
    app=None,
):
    """
    Retrieves information about buses based on the specified keys.

    This function fetches the request data from both PSSE and the bspssepy_bus
    dataFrame, providing flexibility for dynamic and pre-stored data retrieval.
    Handles multiple cases based on the input parameters:
    Case 1: Single key for a specific bus -> Returns a single value
            (str, int, float, or list).
    Case 2: Multiple keys for a specific bus -> Returns a pandas Series with
            the requested keys.
    Case 3: Single key for all buses -> Returns a pandas Series containing
            values for all buses.
    Case 4: Multiple keys for all buses -> Returns a pandas Series for all
            buses with the requested keys.

    Arguments:
        BusKeys (str or list of str): The key(s) for the required information.
        Valid keys include PSSE keys and bspssepy_bus columns.
        Bus (str or int, optional): Bus name or number.
        BusName (str, optional): Bus Name.
        bus_num (int, optional): Bus Number.
        bspssepy_bus (pd.dataFrame, optional): dataFrame containing BSPSSEPy
        Bus data.
        debug_print (bool, optional): Enable detailed debug output. Default
        is False.

    Returns:
        Varies based on input cases:
            - Case 1: Single value corresponding to the requested key for a
            specific Bus.
            - Case 2: pandas Series with the requested keys for a specific Bus.
            - Case 3: pandas Series with values for all Buses for the
            requested key.
            - Case 4: pandas Series for all Buses with the requested keys.

    Notes:
        - Input strings (e.g., BusKeys, Bus, BusName) are normalized by
        stripping extra spaces.
        - The function combines PSSE and bspssepy_bus data if both are
        available for comprehensive results.
        # - Filtering logic is applied based on BusName, bus_num, and
        # Bus.
    """
    if debug_print:
        bp(f"[DEBUG] Retrieving bus info for BusKeys: {BusKeys}, Bus: {Bus},"
           f"BusName: {BusName}, bus_num: {bus_num}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure BusKeys is a list
    if isinstance(BusKeys, str):
        BusKeys = [BusKeys]

    # Normalize strings to remove extra spaces
    BusKeys = [key.strip() for key in BusKeys]
    if isinstance(Bus, str) and Bus:
        BusName = Bus
    elif Bus:
        bus_num = Bus


    
    if BusName is not None and BusName:
        BusName = BusName.strip()



    # Separate PSSE and bspssepy_bus keys
    ValidPSSEKeys = bus_info_dict.keys()
    ValidBSPSSEPyKeys = [] if bspssepy_bus is None else bspssepy_bus.columns


    # Add PSSE Keys needed for basic Bus operations
    _BusKeys = ["NAME", "NUMBER"]
    _BusKeysPSSE = list(_BusKeys)
    for key in BusKeys:
        if key in ValidPSSEKeys and key not in _BusKeysPSSE:
            _BusKeysPSSE.append(key)

    if debug_print:
        bp(f"[DEBUG] Fetching PSSE data for keys: {_BusKeysPSSE}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)


    # Ensure no duplicate columns are fetched from PSSE if bspssepy_brn is provided
    if bspssepy_bus is not None and not bspssepy_bus.empty:
        # Remove overlapping keys from the PSSE fetch list
        ValidBSPSSEPyKeys = [key for key in ValidBSPSSEPyKeys if key not in _BusKeysPSSE]

    if debug_print:
        bp(f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {ValidBSPSSEPyKeys}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)


    # Fetch PSSE data for the required keys
    PSSEdata = {}
    for PSSEKey in _BusKeysPSSE:
        PSSEdata[PSSEKey] = await get_bus_infoPSSE(PSSEKey, debug_print=debug_print,app=app)


    # Combine PSSEdata and bspssepy_trn (if provided) into a single dataFrame
    if bspssepy_bus is not None and not bspssepy_bus.empty:
        ValidBSPSSEPyTrn = bspssepy_bus[ValidBSPSSEPyKeys]
        PSSEdataDF = pd.DataFrame(PSSEdata)
        Combineddata = pd.concat([PSSEdataDF, ValidBSPSSEPyTrn], axis=1)
    else:
        Combineddata = pd.DataFrame(PSSEdata)

    if debug_print:
        bp(f"[DEBUG] Combined data:\n{Combineddata}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)


    # Filter Combineddata based on TrnName, FromBus, and ToBus
    if BusName:
        Combineddata = Combineddata[Combineddata["NAME"].str.strip() == BusName]
    elif bus_num:
        Combineddata = Combineddata[(Combineddata["NUMBER"] == bus_num)]
    
    if debug_print:
        bp(f"[DEBUG] Filtered data:\n{Combineddata}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)


    # Handle cases based on the number of BrnKeys
    if len(BusKeys) == 1:
        Key = BusKeys[0]
        return Combineddata[Key].iloc[0] if len(Combineddata) == 1 else Combineddata[Key]
    else:
        return Combineddata[BusKeys]



async def get_bus_infoPSSE(abusString,  # Requested info string - Check available strings in bus_info_dict
                   debug_print=False,    # Print debug information
                   app=None):
    """
    Retrieves specific bus information from PSSE.

    Parameters:
        abusString (str): Requested information key.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        list or None: A list of the requested information if found, otherwise None.
    """
    if debug_print:
        bp(f"[DEBUG] Requested bus information for abusString: '{abusString}'",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Validate abusString
    if abusString not in bus_info_dict:
        bp(f"[ERROR] Invalid abusString '{abusString}'. Check bus_info_dict for valid options.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    try:
        # Fetch data type for the key
        ierr, datatype = psspy.abustypes([abusString])
        if ierr != 0:
            bp(f"[ERROR] Failed to fetch data type for abusString '{abusString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        # Retrieve data based on type
        if datatype[0] == 'I':
            ierr, data = psspy.abusint(-1, 2, [abusString])
        elif datatype[0] == 'R':
            ierr, data = psspy.abusreal(-1, 2, [abusString])
        elif datatype[0] == 'C':
            ierr, data = psspy.abuschar(-1, 2, [abusString])
        elif datatype[0] == 'X':
            ierr, data = psspy.abuscplx(-1, 2, [abusString])
        else:
            bp(f"[ERROR] Unsupported data type '{datatype[0]}' for abusString '{abusString}'.",app=app)
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


        if ierr != 0:
            bp(f"[ERROR] Failed to retrieve data for abusString '{abusString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if debug_print:
            bp(f"[DEBUG] Successfully retrieved data for '{abusString}': {data}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        return data

    except Exception as e:
        bp(f"[ERROR] Exception occurred while retrieving data: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def BusTrip(t, bspssepy_bus=None, Bus = None, bus_num=None, BusName=None, debug_print=False,app=None):
    """
    Trips a bus (sets its status to 4) and updates the bspssepy_bus dataFrame.

    Parameters:
        t (float): Current simulation time.
        bspssepy_bus (pd.dataFrame): dataFrame containing bus data.
        Bus (int or str, optional): could be Bus Number of Bus Name.
        bus_num (int, optional): Bus Number.
        BusName (str, optional): Bus Name.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """

    default_int, default_real, default_char = bspssepy_default_vars_fun()


    # Initial debug message
    if debug_print:
        bp(f"[DEBUG] BusTrip called with inputs:\n"
              f"  Bus: {Bus}\n"
              f"  BusName: {BusName}\n"
              f"  bus_num: {bus_num}\n"
              f"  Simulation Time: {t}s\n",
              app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        

    # Identify the bus row based on name or number
    if isinstance(Bus, numbers.Number):
        bus_num = Bus
    else:
        BusName = Bus


    # Resolve bus_num if BusName is given
    if BusName:
        bus_num = await get_bus_info("NUMBER", Bus = BusName, bspssepy_bus=bspssepy_bus, debug_print=debug_print, app=app)
    elif not bus_num:
        bp("[ERROR] Either BusName or bus_num must be provided.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    
    BusRow = await get_bus_info(
        BusKeys=["NAME", "NUMBER", "TYPE"],
        Bus = bus_num,
        bspssepy_bus=bspssepy_bus,
        debug_print=debug_print,
        app=app
    )

    # Ensure the bus exists in the dataFrame
    if BusRow.empty:
        bp(f"[ERROR] Bus with Name '{BusName}' or Number '{bus_num}' not found.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    
    bus_num = BusRow["NUMBER"].iloc[0]
    BusName = BusRow["NAME"].iloc[0]
    BusType = BusRow["TYPE"].iloc[0]

    # Debug message with resolved values
    if debug_print:
        bp(f"[DEBUG] Resolved Bus details:\n"
              f"  BusName: {BusName}\n"
              f"  bus_num: {bus_num}\n"
              f"  BusType: {BusType}\n",
              app=app
             )
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    
    # Change bus status in PSSE to 4 (tripped)
    ierr = psspy.bus_chng_4(bus_num, 0,
            [4, default_int, default_int, default_int],
            [default_real, default_real, default_real, default_real, default_real, default_real, default_real],
            default_char)

    if ierr != 0:
        bp(f"[ERROR] Failed to trip bus with Number '{bus_num}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return ierr

    NewType = await get_bus_info("TYPE", Bus = bus_num, debug_print=debug_print,app=app)

    if not(bspssepy_bus is None or bspssepy_bus.empty):
        # Update the bspssepy_bus dataFrame to reflect the action
        bspssepy_bus.loc[(bspssepy_bus["NUMBER"] == bus_num) & (bspssepy_bus["NAME"] == BusName), [
            "BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "TYPE"
        ]] = ["Tripped", "Trip", t, "Bus successfully tripped.", NewType]

    if debug_print:
        bp(f"[SUCCESS] Bus with Number '{bus_num}', Name '{BusName}' successfully tripped.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    return ierr


async def BusClose(t, bspssepy_bus=None, Bus = None, bus_num=None, BusName=None, debug_print=False, app=None):
    """
    Resets a bus to its original type and updates the bspssepy_bus dataFrame.

    Parameters:
        t (float): Current simulation time.
        bspssepy_bus (pd.dataFrame): dataFrame containing bus data.
        Bus (int or str, optional): could be Bus Number of Bus Name.
        bus_num (int, optional): Bus Number.
        BusName (str, optional): Bus Name.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """
    default_int, default_real, default_char = bspssepy_default_vars_fun()


    # Initial debug message
    if debug_print:
        bp(f"[DEBUG] BusClose called with inputs:\n"
              f"  Bus: {Bus}\n"
              f"  BusName: {BusName}\n"
              f"  bus_num: {bus_num}\n"
              f"  Simulation Time: {t}s\n",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        

    # Identify the bus row based on name or number
    if isinstance(Bus, numbers.Number):
        bus_num = Bus
    else:
        BusName = Bus


    # Resolve bus_num if BusName is given
    if BusName:
        bus_num = await get_bus_info("NUMBER", Bus = BusName, bspssepy_bus=bspssepy_bus, debug_print=debug_print,app=app)
    elif not bus_num:
        bp("[ERROR] Either BusName or bus_num must be provided.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    
    BusRow = await get_bus_info(
        BusKeys=["NAME", "NUMBER", "TYPE", "BSPSSEPyType_0"],
        Bus = bus_num,
        bspssepy_bus=bspssepy_bus,
        debug_print=debug_print,
        app=app
    )

    # Ensure the bus exists in the dataFrame
    if BusRow.empty:
        bp(f"[ERROR] Bus with Name '{BusName}' or Number '{bus_num}' not found.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    
    bus_num = BusRow["NUMBER"].iloc[0]
    # bus_num = BusRow["NUMBER"].values[0]
    BusName = BusRow["NAME"].iloc[0]
    BusType = BusRow["TYPE"].iloc[0]
    BusType_0 = BusRow["BSPSSEPyType_0"].iloc[0]

    # Debug message with resolved values
    if debug_print:
        bp(f"[DEBUG] Resolved Bus details:\n"
              f"  BusName: {BusName}\n"
              f"  bus_num: {bus_num}\n"
              f"  BusType: {BusType}\n"
              f"  BusType_0: {BusType_0}\n",
              app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    
    # Change bus status in PSSE to 4 (tripped)
    ierr = psspy.bus_chng_4(bus_num, 0,
            [BusType_0, default_int, default_int, default_int],
            [default_real, default_real, default_real, default_real, default_real, default_real, default_real],
            default_char)
    
    NewType = await get_bus_info("TYPE", Bus=bus_num, debug_print=debug_print,app=app)

    if ierr != 0:
        bp(f"[ERROR] Failed to close bus with Number '{bus_num}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return ierr

    if not(bspssepy_bus is None or bspssepy_bus.empty):
        # Update the bspssepy_bus dataFrame to reflect the action
        bspssepy_bus.loc[(bspssepy_bus["NUMBER"] == bus_num) & (bspssepy_bus["NAME"] == BusName), [
            "BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "TYPE"
        ]] = ["Closed", "Close", t, "Bus successfully Closed.", NewType]

    if debug_print:
        bp(f"[SUCCESS] Bus with Number '{bus_num}', Name '{BusName}' successfully closed.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    return ierr




async def ChangeBusType(t, NewBusType, bspssepy_bus=None, Bus = None, bus_num=None, BusName=None, debug_print=False, app=None):
    """
    This function allows for changing bus types manually during the simulation.

    Parameters:
        t (float): Current simulation time.
        NewBusType (int): 1,2,3,4
        bspssepy_bus (pd.dataFrame): dataFrame containing bus data.
        Bus (int or str, optional): could be Bus Number of Bus Name.
        bus_num (int, optional): Bus Number.
        BusName (str, optional): Bus Name.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """
    default_int, default_real, default_char = bspssepy_default_vars_fun()


    # Initial debug message
    if debug_print:
        bp(f"[DEBUG] BusClose called with inputs:\n"
              f"  BusType: {NewBusType}\n"
              f"  Bus: {Bus}\n"
              f"  BusName: {BusName}\n"
              f"  bus_num: {bus_num}\n"
              f"  Simulation Time: {t}s\n",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        

    # Identify the bus row based on name or number
    if isinstance(Bus, numbers.Number):
        bus_num = Bus
    else:
        BusName = Bus


    # Resolve bus_num if BusName is given
    if BusName:
        bus_num = await get_bus_info("NUMBER", Bus = BusName, bspssepy_bus=bspssepy_bus, debug_print=debug_print,app=app)
    elif not bus_num:
        bp("[ERROR] Either BusName or bus_num must be provided.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    
    BusRow = await get_bus_info(
        BusKeys=["NAME", "NUMBER", "TYPE", "BSPSSEPyType_0"],
        Bus = bus_num,
        bspssepy_bus=bspssepy_bus,
        debug_print=debug_print,
        app=app
    )

    # Ensure the bus exists in the dataFrame
    if BusRow.empty:
        bp(f"[ERROR] Bus with Name '{BusName}' or Number '{bus_num}' not found.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    
    bus_num = BusRow["NUMBER"].iloc[0]
    # bus_num = BusRow["NUMBER"].values[0]
    BusName = BusRow["NAME"].iloc[0]
    BusType = BusRow["TYPE"].iloc[0]
    BusType_0 = BusRow["BSPSSEPyType_0"].iloc[0]

    # Debug message with resolved values
    if debug_print:
        bp(f"[DEBUG] Resolved Bus details:\n"
              f"  BusName: {BusName}\n"
              f"  bus_num: {bus_num}\n"
              f"  BusType: {BusType}\n"
              f"  BusType_0: {BusType_0}\n"
             ,app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    
    # Change bus status in PSSE to 4 (tripped)
    ierr = psspy.bus_chng_4(bus_num, 0,
            [NewBusType, default_int, default_int, default_int],
            [default_real, default_real, default_real, default_real, default_real, default_real, default_real],
            default_char)
    
    NewType = await get_bus_info("TYPE", Bus=bus_num, debug_print=debug_print,app=app)

    if ierr != 0:
        bp(f"[ERROR] Failed to close bus with Number '{bus_num}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return ierr

    if not(bspssepy_bus is None or bspssepy_bus.empty):
        # Update the bspssepy_bus dataFrame to reflect the action
        bspssepy_bus.loc[(bspssepy_bus["NUMBER"] == bus_num) & (bspssepy_bus["NAME"] == BusName), [
            "BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "TYPE"
        ]] = ["Closed", "ModifyType", t, "BusType modified successfully.", NewType] if NewType != 4 else ["Tripped", "ModifyType", t, "BusType modified successfully.", NewType]

    if debug_print:
        bp(f"[SUCCESS] Bus with Number '{bus_num}', Name '{BusName}' successfully modified.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    return ierr