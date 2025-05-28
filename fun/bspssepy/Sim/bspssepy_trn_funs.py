# BSPSSEPy Two-Winding Transformer (bspssepy_trn) Functions
# This Python module contains all 'Two-Winding Transformer' related functions for the BSPSSEPy framework:
#
# 1. GetTrnInfo: Retrieves specific information about Two-Winding Transformers based on user-specified keys, either from PSSE or bspssepy_trn DataFrame.
#    - Handles cases for single/multiple keys and specific/all Two-Winding Transformers.
#
# 2. GetTrnInfoPSSE: Fetches Two-Winding Transformer-related data directly from PSSE using the PSSE library.
#
# 3. TrnTrip: Trips a Two-Winding Transformer based on its ID, name, or bus connections and updates the bspssepy_trn DataFrame.
#
# 4. TrnClose: Closes a Two-Winding Transformer based on its ID, name, or bus connections and updates the bspssepy_trn DataFrame.
#
# This module ensures dynamic interaction with PSSE for real-time data, while allowing extended tracking and simulation-specific metadata updates through the bspssepy_trn DataFrame.
#
# Key Features:
# - Integrates real-time data retrieval from PSSE and local metadata updates.
# - Supports flexible query formats including Two-Winding Tranformers names, IDs, or bus connections.
# - Logs detailed debug information for easy troubleshooting.
#
#    Last Update for this file was on BSPSSEPy Ver 0.2 (28 Dec. 2024)
#
#       BSPSSEPy Application
#       Copyright (c) 2024, Ilyas Farhat
#       by Ilyas Farhat
#
#       This file is part of BSPSSEPy Application.
#       Contact the developer at ilyas.farhat@outlook.com


import psspy
import dyntools
import pandas as pd
from .bspssepy_bus_funs import *
from fun.bspssepy.bspssepy_dict import *
# from fun.bspssepy.bspssepy_funs_dict import *
from fun.bspssepy.app.app_helper_funs import bp
import asyncio


async def GetTrnInfo(TrnKeys,  # The key(s) for the required information of the Trn
                  TrnName=None,  # Trn Name (optional)
                  FromBus=None,  # From Bus Number or Name (optional)
                  ToBus=None,  # To Bus Number or Name (optional)
                  bspssepy_trn=None,  # bspssepy_trn DataFrame containing BSPSSEBy extra information associated with the Trn (optional)
                  debug_print=False,  # Enable detailed debug output
                  app=None):
    """
    Retrieves information about Two-Winding Transformers based on the specified keys.

    This function fetches the requested data from both PSSE and the bspssepy_trn DataFrame, providing flexibility
    for dynamic and pre-stored data retrieval. Handles multiple cases based on the input parameters:

    Case 1: Single key for a specific Two-Winding Tranformer -> Returns a single value (str, int, float, or list).
    Case 2: Multiple keys for a specific Two-Winding Tranformer -> Returns a pandas Series with the requested keys.
    Case 3: Single key for all Two-Winding Transformers -> Returns a pandas Series containing values for all Two-Winding Transformers.
    Case 4: Multiple keys for all Two-Winding Transformers -> Returns a pandas Series for all Two-Winding Transformers with the requested keys.

    Arguments:
        TrnKeys: str or list of str
            The key(s) for the required information. Check trn_info_dict for valid PSSE keys, or bspssepy_trn columns.
        TrnName: str
            Trn Name (optional).
        FromBus: str or int
            From Bus Number or Name (optional).
        ToBus: str or int
            To Bus Number or Name (optional).
        bspssepy_trn: pd.DataFrame
            The bspssepy_trn DataFrame containing BSPSSEPy Trn data (optional).
        debug_print: bool
            Enable detailed debug output (default = False).

    Returns:
        Depending on the input case:
            - Case 1: Single value corresponding to the requested key for a specific Two-Winding Transformer.
            - Case 2: pandas Series with the requested keys for a specific Two-Winding Transformer.
            - Case 3: pandas Series with values for all Two-Winding Transformers for the requested key.
            - Case 4: pandas Series for all Two-Winding Transformers with the requested keys.


    Notes:
        - Input strings (e.g., TrnKeys, TrnName, FromBus, ToBus) are normalized by stripping extra spaces.
        - The function combines PSSE and bspssepy_trn data if both are available for comprehensive results.
        - Filtering logic is applied based on TrnName, FromBus, and ToBus.
    """

    if debug_print:
        bp(f"[DEBUG] Retrieving Two-Winding Transformer info for TrnKeys: {TrnKeys}, TrnName: {TrnName}, FromBus: {FromBus}, ToBus: {ToBus}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure TrnKeys is a list
    if isinstance(TrnKeys, str):
        TrnKeys = [TrnKeys]


    # Normalize strings to remove extra spaces
    TrnKeys = [key.strip() for key in TrnKeys]
    if TrnName:
        TrnName = TrnName.strip()
    if not isinstance(FromBus, (int, float)) and FromBus:
        FromBus = FromBus.strip()
        FromBusKey = "FROMNAME"
    elif isinstance(FromBus, (int, float)) and FromBus:
        FromBusKey = "FROMNUMBER"
        
    if not isinstance(ToBus, (int, float)) and ToBus:
        ToBus = ToBus.strip()
        ToBusKey = "TONAME"
    elif isinstance(ToBus, (int, float)) and ToBus:
        ToBusKey = "TONUMBER"


    # Separate PSSE and bspssepy_trn keys
    ValidPSSEKeys = trn_info_dict.keys()
    ValidBSPSSEPyKeys = [] if bspssepy_trn is None else bspssepy_trn.columns


    # Add PSSE Keys needed for basic branch operations
    _TrnKeys = ["XFRNAME", "FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"]
    _TrnKeysPSSE = list(_TrnKeys)
    for key in TrnKeys:
        if key in ValidPSSEKeys and key not in _TrnKeysPSSE:
            _TrnKeysPSSE.append(key)

    if debug_print:
        bp(f"[DEBUG] Fetching PSSE data for keys: {_TrnKeysPSSE}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)


    # Ensure no duplicate columns are fetched from PSSE if bspssepy_brn is provided
    if bspssepy_trn is not None and not bspssepy_trn.empty:
        # Remove overlapping keys from the PSSE fetch list
        ValidBSPSSEPyKeys = [key for key in ValidBSPSSEPyKeys if key not in _TrnKeysPSSE]

    if debug_print:
        bp(f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {ValidBSPSSEPyKeys}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)


    # Fetch PSSE data for the required keys
    PSSEData = {}
    for PSSEKey in _TrnKeysPSSE:
        PSSEData[PSSEKey] = await GetTrnInfoPSSE(PSSEKey, debug_print=debug_print,app=app)

    # Combine PSSEData and bspssepy_trn (if provided) into a single DataFrame
    if bspssepy_trn is not None and not bspssepy_trn.empty:
        ValidBSPSSEPyTrn = bspssepy_trn[ValidBSPSSEPyKeys]
        PSSEDataDF = pd.DataFrame(PSSEData)
        CombinedData = pd.concat([PSSEDataDF, ValidBSPSSEPyTrn], axis=1)
    else:
        CombinedData = pd.DataFrame(PSSEData)

    if debug_print:
        bp(f"[DEBUG] Combined Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    

    # Filter CombinedData based on TrnName, FromBus, and ToBus
    if TrnName:
        CombinedData = CombinedData[CombinedData["XFRNAME"].str.strip() == TrnName]
    elif FromBus and ToBus:
        if isinstance(FromBus, (int, float)):
            FromBusKey = "FROMNUMBER"
        else:
            FromBusKey = "FROMNAME"
        if isinstance(ToBus, (int, float)):
            ToBusKey = "TONUMBER"
        else:
            ToBusKey = "TONAME"

        CombinedData = CombinedData[
            (CombinedData[FromBusKey] == FromBus) & 
            (CombinedData[ToBusKey] == ToBus)
        ]

    if debug_print:
        bp(f"[DEBUG] Filtered Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Handle cases based on the number of BrnKeys
    if len(TrnKeys) == 1:
        Key = TrnKeys[0]
        return CombinedData[Key].iloc[0] if len(CombinedData) == 1 else CombinedData[Key]
    else:
        return CombinedData[TrnKeys]



async def GetTrnInfoPSSE(atrnString,  # Requested Info string - Check available strings in trn_info_dict
                  TrnEntry=1,  # 1 entry for each Trn, 2 --> two-way entry (each Trn in both directions)
                  debug_print=False,  # Print debug information
                  app=None,
                  ):
    """
    This function returns the requested information about the Trn of interest.
    If no Trn is specified, it will return the information about all Two-Winding Transformers.

    Arguments:
        atrnString: str
            Requested Info string - Check available strings in trn_info_dict.
        TrnEntry: int
            1 entry for each Trn, 2 --> two-way entry (each Trn in both directions).
        TrnName: str
            Trn Name (optional).
        FromBus: str or int
            From Bus Number or Name (optional).
        ToBus: str or int
            To Bus Number or Name (optional).
        debug_print: bool
            Print debug information (default = False).

    Returns:
        list or None:
            A list of the requested information if found, otherwise None.

    Notes:
        - If no Trn is specified, information about all Two-Winding Transformers is returned.
        - To select a Trn, use either TrnName or (FromBus and ToBus). If multiple Two-Winding Transformers
          connect the two buses, use the Trn name.
    """

    if debug_print:
        bp(f"[DEBUG] Requested Trn information for atrnString: '{atrnString}'",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        bp(f"[DEBUG] TrnEntry: {TrnEntry}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Check if atrnString exists in trn_info_dict
    if atrnString not in trn_info_dict:
        bp(f"[ERROR] Invalid atrnString '{atrnString}'. Check trn_info_dict for valid options.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Determine subsystem and entry flag
    atrnSID = -1  # Assume entire system unless specified
    atrnFlag = 2  # Default flag for all Two-Winding Transformers

    # Set up the query parameters
    parameters = {
        'sid': atrnSID,
        'flag': atrnFlag,
        'entry': TrnEntry,
        'string': [atrnString]
    }

    # Filter Two-Winding Transformers based on provided parameters
    # if TrnName:
    #     parameters['trnname'] = TrnName
    #     if debug_print:
    #         bp(f"[DEBUG] Filtering Two-Winding Transformers by TrnName: {TrnName}",app=app)
    # elif FromBus and ToBus:
    #     parameters['frombus'] = FromBus
    #     parameters['tobus'] = ToBus
    #     if debug_print:
    #         bp(f"[DEBUG] Filtering Two-Winding Transformers by FromBus: {FromBus} and ToBus: {ToBus}", app=app)

    # Fetch the data type for the requested string
    ierr, dataType = psspy.atrntypes([atrnString])
    if ierr != 0:
        bp(f"[ERROR] Failed to fetch data type for atrnString '{atrnString}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Retrieve data based on the type
    try:
        if dataType[0] == 'I':  # Integer data
            ierr, data = psspy.atrnint(**parameters)
        elif dataType[0] == 'R':  # Real data
            ierr, data = psspy.atrnreal(**parameters)
        elif dataType[0] == 'C':  # Character data
            ierr, data = psspy.atrnchar(**parameters)
        elif dataType[0] == 'X':  # Complex data
            ierr, data = psspy.atrncplx(**parameters)
        else:
            bp(f"[ERROR] Unsupported data type '{dataType[0]}' for atrnString '{atrnString}'.",app=app)
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
            bp(f"[ERROR] Failed to retrieve data for atrnString '{atrnString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if debug_print:
            bp(f"[DEBUG] Successfully retrieved data for '{atrnString}': {data}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        return data

    except Exception as e:
        bp(f"[ERROR] Exception occurred while retrieving TW-trn data: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    



async def TrnTrip(t, bspssepy_trn=None, TrnID=None, TrnName=None, TrnFromBus=None, TrnToBus=None, debug_print=False, app=None):
    """
    Trips a Trn based on its ID, name, or bus connection and updates extended info columns.

    Arguments:
        t: float
            Current simulation time.
        bspssepy_trn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy Trn data.
        TrnID: str or int
            The unique ID of the Trn (optional).
        TrnName: str
            The name of the Trn (optional).
        TrnFromBus: int or str
            The "from" bus number or name (optional).
        TrnToBus: int or str
            The "to" bus number or name (optional).
        debug_print: bool
            Enable detailed debug output (default = False).

    Returns:
        int:
            ierr: The status of the action applied (ierr = 0 --> success!).
    """
    # Initial debug message
    if debug_print:
        bp(f"[DEBUG] TrnTrip called with inputs:\n"
              f"  TrnID: {TrnID}\n"
              f"  TrnName: {TrnName}\n"
              f"  FromBus: {TrnFromBus}\n"
              f"  ToBus: {TrnToBus}\n"
              f"  Simulation Time: {t}s\n",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Resolve TrnName if only bus info is provided
    if not TrnName and (TrnFromBus and TrnToBus):
        TrnName = await GetTrnInfo(
            TrnKeys=["XFRNAME"],
            FromBus=TrnFromBus,
            ToBus=TrnToBus,
            bspssepy_trn=bspssepy_trn,
            debug_print=debug_print,
            app=app
        )
        if not TrnName:
            bp(f"[ERROR] Could not identify Trn between buses {TrnFromBus} and {TrnToBus}.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

    # Fetch Trn details
    TrnRow = await GetTrnInfo(
        TrnKeys=["FROMNUMBER", "TONUMBER", "ID", "STATUS", "XFRNAME"],
        TrnName=TrnName,
        bspssepy_trn=bspssepy_trn,
        debug_print=debug_print,
        app=app
    )

    if TrnRow is None or len(TrnRow) == 0:
        bp(f"[ERROR] Trn not found for ID={TrnID}, Name={TrnName}, "
              f"FromBus={TrnFromBus}, ToBus={TrnToBus}.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Extract Trn information
    TrnFromBus = TrnRow["FROMNUMBER"].iloc[0]
    TrnToBus = TrnRow["TONUMBER"].iloc[0]
    TrnID = TrnRow["ID"].iloc[0]
    TrnName = TrnRow["XFRNAME"].iloc[0]
    TrnStatus = TrnRow["STATUS"].iloc[0]

    # Debug message with resolved values
    if debug_print:
        bp(f"[DEBUG] Resolved Trn details:\n"
              f"  TrnID: {TrnID}\n"
              f"  TrnName: {TrnName}\n"
              f"  FromBus: {TrnFromBus}\n"
              f"  ToBus: {TrnToBus}\n"
              f"  Status: {'Closed' if TrnStatus == 1 else 'Tripped'}\n",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Check if the Trn is already tripped
    if TrnStatus != 1:
        bp(f"[INFO] Trn '{TrnName}' is already tripped.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0

    # Attempt to trip the Trn
    try:
        if debug_print:
            bp(f"[DEBUG] Attempting to trip Two-Winding Transformer '{TrnName}' between buses {TrnFromBus} and {TrnToBus}.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        ierr = psspy.dist_branch_trip(TrnFromBus, TrnToBus, TrnID)

        if ierr != 0:
            bp(f"[ERROR] Failed to trip Trn '{TrnName}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return ierr

        # Ensure proper matching for FromBus and ToBus in bspssepy_trn
        FromBusCondition = bspssepy_trn["FROMNUMBER"].apply(str) == str(TrnFromBus)
        ToBusCondition = bspssepy_trn["TONUMBER"].apply(str) == str(TrnToBus)
        IDCondition = bspssepy_trn["ID"] == TrnID

        NewStatus = await GetTrnInfo("STATUS", TrnName=TrnName, debug_print=debug_print, app=app)

        if not(bspssepy_trn is None or bspssepy_trn.empty):
            # Update the bspssepy_trn DataFrame
            bspssepy_trn.loc[
                FromBusCondition & ToBusCondition & IDCondition,
                ["BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "STATUS"]
            ] = ["Tripped", "Trip", t, "TW-Trn successfully tripped.", NewStatus]

        if debug_print:
            bp(f"[SUCCESS] Successfully tripped Two-Winding Transformer '{TrnName}'. Updated bspssepy_trn DataFrame.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        return ierr

    except KeyError as e:
        bp(f"[ERROR] Missing key during TrnTrip operation: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    except Exception as e:
        bp(f"[ERROR] Unexpected error during TrnTrip: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def TrnClose(t, bspssepy_trn=None, bspssepy_bus=None, TrnID=None, TrnName=None, TrnFromBus=None, TrnToBus=None, CalledByGen = False, debug_print=False, app=None):
    """
    Closes a Trn based on its ID, name, or bus connection and updates extended info columns.

    Arguments:
        t: float
            Current simulation time.
        bspssepy_trn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy Trn data.
        TrnID: str or int
            The unique ID of the Trn (optional).
        TrnName: str
            The name of the Trn (optional).
        TrnFromBus: int or str
            The "from" bus number or name (optional).
        TrnToBus: int or str
            The "to" bus number or name (optional).
        debug_print: bool
            Enable detailed debug output (default = False).

    Returns:
        int:
            ierr: The status of the action applied (ierr = 0 --> success!).
    """
    if debug_print:
        bp(f"[DEBUG] TrnClose called with inputs:\n"
              f"  TrnID: {TrnID}\n"
              f"  TrnName: {TrnName}\n"
              f"  FromBus: {TrnFromBus}\n"
              f"  ToBus: {TrnToBus}\n"
              f"  Simulation Time: {t}s\n",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Resolve TrnName if only bus info is provided
    if not TrnName and (TrnFromBus and TrnToBus):
        TrnName = await GetTrnInfo(
            TrnKeys=["XFRNAME"],
            FromBus=TrnFromBus,
            ToBus=TrnToBus,
            bspssepy_trn=bspssepy_trn,
            debug_print=debug_print,
            app=app
        )
        if not TrnName:
            bp(f"[ERROR] Could not identify Trn between buses {TrnFromBus} and {TrnToBus}.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

    # Fetch Trn details
    TrnRow = await GetTrnInfo(
        TrnKeys=["FROMNUMBER", "TONUMBER", "ID", "STATUS", "XFRNAME", "GenControlled"],
        TrnName=TrnName,
        bspssepy_trn=bspssepy_trn,
        debug_print=debug_print,
        app=app
    )

    if TrnRow is None or len(TrnRow) == 0:
        bp(f"[ERROR] Trn not found for ID={TrnID}, Name={TrnName}, FromBus={TrnFromBus}, ToBus={TrnToBus}.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Extract Trn information
    TrnFromBus = TrnRow["FROMNUMBER"].iloc[0]
    TrnToBus = TrnRow["TONUMBER"].iloc[0]
    TrnID = TrnRow["ID"].iloc[0]
    TrnName = TrnRow["XFRNAME"].iloc[0]
    TrnStatus = TrnRow["STATUS"].iloc[0]
    TrnGenControlled = TrnRow["GenControlled"].values[0]

    if debug_print:
        bp(f"[DEBUG] Resolved Trn details:\n"
              f"  TrnID: {TrnID}\n"
              f"  TrnName: {TrnName}\n"
              f"  FromBus: {TrnFromBus}\n"
              f"  ToBus: {TrnToBus}\n"
              f"  Status: {'Closed' if TrnStatus == 1 else 'Tripped'}\n"
              f"  GenControlled: {TrnGenControlled}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Check if the Trn is already closed
    if TrnStatus == 1:
        bp(f"[INFO] Trn '{TrnName}' is already closed.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0

    # Ensure both buses are operational
    if (CalledByGen & TrnGenControlled) or not TrnGenControlled:
        try:
            
            FromBusType = await get_bus_info(BusKeys="TYPE", bus_num=TrnFromBus, debug_print=debug_print, app=app)
            ToBusType = await get_bus_info(BusKeys="TYPE", bus_num=TrnToBus, debug_print=debug_print, app=app)

            if FromBusType == 4:  # Tripped
                if debug_print:
                    bp(f"[DEBUG] FromBus {TrnFromBus} is tripped. Attempting to close it.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = await BusClose(t, bspssepy_bus=bspssepy_bus, bus_num=TrnFromBus, debug_print=debug_print,app=app)
                if ierr != 0:
                    bp(f"[ERROR] Failed to close FromBus {TrnFromBus}. Aborting Trn close.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    return ierr

            if ToBusType == 4:  # Tripped
                if debug_print:
                    bp(f"[DEBUG] ToBus {TrnToBus} is tripped. Attempting to close it.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = await BusClose(t, bspssepy_bus=bspssepy_bus, bus_num=TrnToBus, debug_print=debug_print,app=app)
                if ierr != 0:
                    bp(f"[ERROR] Failed to close ToBus {TrnToBus}. Aborting Trn close.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    return ierr

            if debug_print:
                bp(f"[DEBUG] Attempting to close Two-Winding Transformer '{TrnName}' between buses {TrnFromBus} and {TrnToBus}.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            # Attempt to close the Trn
            ierr = psspy.dist_branch_close(TrnFromBus, TrnToBus, TrnID)
            if ierr != 0:
                bp(f"[ERROR] Failed to close Trn '{TrnName}'. PSSE error code: {ierr}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                return ierr

            # Update the bspssepy_trn DataFrame
            FromBusCondition = bspssepy_trn["FROMNUMBER"].apply(str) == str(TrnFromBus)
            ToBusCondition = bspssepy_trn["TONUMBER"].apply(str) == str(TrnToBus)
            IDCondition = bspssepy_trn["ID"] == TrnID

            
            NewStatus = await GetTrnInfo("STATUS", TrnName=TrnName, debug_print=debug_print, app=app)
            
            if not(bspssepy_trn is None or bspssepy_trn.empty):
                bspssepy_trn.loc[
                    FromBusCondition & ToBusCondition & IDCondition,
                    ["BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "STATUS"]
                ] = ["Closed", "Close", t, "Trn successfully closed.", NewStatus]

            if debug_print:
                bp(f"[SUCCESS] Successfully closed Trn '{TrnName}'. Updated bspssepy_trn DataFrame.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            return ierr

        except Exception as e:
            bp(f"[ERROR] Unexpected error during TrnClose: {e}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    
    else:
        bp(f"[ERROR] This transformer is tied to a generator. Don't attempt to close it manually. It can be controlled through GenEnable function to model generator phases.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return -999