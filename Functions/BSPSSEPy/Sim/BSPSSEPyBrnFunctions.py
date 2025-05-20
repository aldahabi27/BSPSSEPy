# BSPSSEPy Branch Functions
# This Python module contains all 'Branch' related functions for the BSPSSEPy framework:
#
# 1. GetBranchInfo: Retrieves specific information about branches based on user-specified keys, either from PSSE or BSPSSEPyBrn DataFrame.
#    - Handles cases for single/multiple keys and specific/all branches.
#
# 2. GetBranchInfoPSSE: Fetches branch-related data directly from PSSE using the PSSE library. This function is called by GetBranchInfo.
#
# 3. BranchTrip: Trips a branch based on its ID, name, or bus connections and updates the BSPSSEPyBrn DataFrame.
#
# 4. BranchClose: Closes a branch based on its ID, name, or bus connections and updates the BSPSSEPyBrn DataFrame.
#
# This module ensures dynamic interaction with PSSE for real-time data, while allowing extended tracking and simulation-specific metadata updates through the BSPSSEPyBrn DataFrame.
#
# Key Features:
# - Integrates real-time data retrieval from PSSE and local metadata updates.
# - Supports flexible query formats including branch names, IDs, or bus connections.
# - Logs detailed debug information for easy troubleshooting.
#
#    Last Update for this file was on BSPSSEPy Ver 0.2 (25 Dec. 2024)
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
from .BSPSSEPyBusFunctions import *
from Functions.BSPSSEPy.BSPSSEPyDictionary import *
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint
import asyncio

# from Functions.BSPSSEPy.BSPSSEPyFunctionsDictionary import *

async def GetBrnInfo(BrnKeys,  # The key(s) for the required information of the Branch
               BranchName=None,  # Branch Name (optional)
               FromBus=None,  # From Bus Number or Name (optional)
               ToBus=None,  # To Bus Number or Name (optional)
               BSPSSEPyBrn=None,  # BSPSSEPyBrn DataFrame containing BSPSSEPy extra information associated with the branch (optional)
               DebugPrint=False,
               app=None):  # Enable detailed debug output
    """
    Retrieves information about branches based on the specified keys.

    This function fetches the requested data from both PSSE and the BSPSSEPyBrn DataFrame, providing flexibility
    for dynamic and pre-stored data retrieval. Handles multiple cases based on the input parameters:

    Case 1: Single key for a specific branch -> Returns a single value (str, int, float, or list).
    Case 2: Multiple keys for a specific branch -> Returns a pandas Series with the requested keys.
    Case 3: Single key for all branches -> Returns a pandas Series containing values for all branches.
    Case 4: Multiple keys for all branches -> Returns a pandas Series for all branches with the requested keys.

    Arguments:
        BrnKeys (str or list of str): The key(s) for the required information. Valid keys include PSSE keys and 
                                         BSPSSEPyBrn columns.
        BranchName (str, optional): Name of the branch to filter. Defaults to None.
        FromBus (str or int, optional): "From Bus" Number or Name. Defaults to None.
        ToBus (str or int, optional): "To Bus" Number or Name. Defaults to None.
        BSPSSEPyBrn (pd.DataFrame, optional): The BSPSSEPyBrn DataFrame containing branch data. Defaults to None.
        DebugPrint (bool, optional): Enable detailed debug output. Defaults to False.

    Returns:
        Depending on the input case:
            - Case 1: Single value corresponding to the requested key for a specific branch.
            - Case 2: pandas Series with the requested keys for a specific branch.
            - Case 3: pandas Series with values for all branches for the requested key.
            - Case 4: pandas Series for all branches with the requested keys.

    Notes:
        - Input strings (e.g., BrnKeys, BranchName, FromBus, ToBus) are normalized by stripping extra spaces.
        - The function combines PSSE and BSPSSEPyBrn data if both are available for comprehensive results.
        - Filtering logic is applied based on BranchName, FromBus, and ToBus.
    """
    # Debug logging
    if DebugPrint:
        bsprint(f"[DEBUG] Retrieving branch info for BrnKeys: {BrnKeys}, BranchName: {BranchName}, FromBus: {FromBus}, ToBus: {ToBus}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Ensure BrnKeys is a list
    if isinstance(BrnKeys, str):
        BrnKeys = [BrnKeys]

    # Normalize strings to remove extra spaces
    BrnKeys = [key.strip() for key in BrnKeys]
    if BranchName:
        BranchName = BranchName.strip()
    if isinstance(FromBus, str) and FromBus:
        FromBus = FromBus.strip()
        FromBusKey = "FROMNAME"
    else:
        FromBusKey = "FROMNUMBER"
        
    if isinstance(ToBus, str) and ToBus:
        ToBus = ToBus.strip()
        ToBusKey = "TONAME"
    else:
        ToBusKey = "TONUMBER"
    

    # Separate PSSE and BSPSSEPyBrn keys
    ValidPSSEKeys = BrnInfoDic.keys()
    ValidBSPSSEPyKeys = [] if BSPSSEPyBrn is None else BSPSSEPyBrn.columns

    # Add PSSE Keys needed for basic branch operations
    _BrnKeys = ["BRANCHNAME", "FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"]
    _BrnKeysPSSE = list(_BrnKeys)
    for key in BrnKeys:
        if key in ValidPSSEKeys and key not in _BrnKeysPSSE:
            _BrnKeysPSSE.append(key)
    


    if DebugPrint:
        bsprint(f"[DEBUG] Fetching PSSE data for keys: {_BrnKeysPSSE}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)


    # Ensure no duplicate columns are fetched from PSSE if BSPSSEPyBrn is provided
    if BSPSSEPyBrn is not None and not BSPSSEPyBrn.empty:
        # Remove overlapping keys from the PSSE fetch list
        ValidBSPSSEPyKeys = [key for key in ValidBSPSSEPyKeys if key not in _BrnKeysPSSE]

    if DebugPrint:
        bsprint(f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {ValidBSPSSEPyKeys}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Fetch PSSE data for the required keys
    PSSEData = {}
    for PSSEKey in _BrnKeysPSSE:
        PSSEData[PSSEKey] = await GetBrnInfoPSSE(PSSEKey, DebugPrint=DebugPrint,app=app)

    # Combine PSSEData and BSPSSEPyBrn (if provided) into a single DataFrame
    if BSPSSEPyBrn is not None and not BSPSSEPyBrn.empty:
        ValidBSPSSEPyBrn = BSPSSEPyBrn[ValidBSPSSEPyKeys]
        PSSEDataDF = pd.DataFrame(PSSEData)
        CombinedData = pd.concat([PSSEDataDF, ValidBSPSSEPyBrn], axis=1)
    else:
        CombinedData = pd.DataFrame(PSSEData)

    if DebugPrint:
        bsprint(f"[DEBUG] Combined Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    

    # Filter CombinedData based on BranchName, FromBus, and ToBus
    if BranchName:
        CombinedData = CombinedData[CombinedData["BRANCHNAME"].str.strip() == BranchName]
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

    if DebugPrint:
        bsprint(f"[DEBUG] Filtered Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Handle cases based on the number of BrnKeys
    if len(BrnKeys) == 1:
        Key = BrnKeys[0]
        return CombinedData[Key].iloc[0] if len(CombinedData) == 1 else CombinedData[Key]
    else:
        return CombinedData[BrnKeys]



async def GetBrnInfoPSSE(abrnString,  # Requested Info string - Check available strings in BrnInfoDic
                  BranchEntry=1,  # 1 entry for each branch, 2 --> two-way entry (each branch in both directions)
                  DebugPrint=False,  # Print debug information
                  app=None):
    """
    This function returns the requested information about the branch of interest.
    If no branch is specified, it will return the information about all branches.

    Arguments:
        abrnString: str
            Requested Info string - Check available strings in BrnInfoDic.
        BranchEntry: int
            1 entry for each branch, 2 --> two-way entry (each branch in both directions).
        # BranchName: str
        #     Branch Name (optional).
        # FromBus: str or int
        #     From Bus Number or Name (optional).
        # ToBus: str or int
        #     To Bus Number or Name (optional).
        DebugPrint: bool
            Print debug information (default = False).

    Returns:
        list or None:
            A list of the requested information if found, otherwise None.

    Notes:
        # - If no branch is specified, information about all branches is returned.
        # - To select a branch, use either BranchName or (FromBus and ToBus). If multiple branches
        #   connect the two buses, use the branch name.
    """

    if DebugPrint:
        bsprint(f"[DEBUG] Requested branch information for abrnString: '{abrnString}'",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        bsprint(f"[DEBUG] BranchEntry: {BranchEntry}",app=app) #, BranchName: {BranchName}, FromBus: {FromBus}, ToBus: {ToBus}")
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Check if abrnString exists in BrnInfoDic
    if abrnString not in BrnInfoDic:
        bsprint(f"[ERROR] Invalid abrnString '{abrnString}'. Check BrnInfoDic for valid options.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    # Determine subsystem and entry flag
    abrnSID = -1  # Assume entire system unless specified
    abrnFlag = 2  # Default flag for all branches

    # Set up the query parameters
    parameters = {
        'sid': abrnSID,
        'flag': abrnFlag,
        'entry': BranchEntry,
        'string': [abrnString]
    }

    # # Filter branches based on provided parameters
    # if BranchName:
    #     parameters['BRANCHNAME'] = BranchName
    #     if DebugPrint:
    #         bsprint(f"[DEBUG] Filtering branches by BranchName: {BranchName}")
    # elif FromBus and ToBus:
    #     parameters['FROMBUS'] = FromBus
    #     parameters['TO'] = ToBus
    #     if DebugPrint:
    #         bsprint(f"[DEBUG] Filtering branches by FromBus: {FromBus} and ToBus: {ToBus}")

    # Fetch the data type for the requested string
    ierr, dataType = psspy.abrntypes([abrnString])
    if ierr != 0:
        bsprint(f"[ERROR] Failed to fetch data type for abrnString '{abrnString}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    # Retrieve data based on the type
    try:
        if dataType[0] == 'I':  # Integer data
            ierr, data = psspy.abrnint(**parameters)
        elif dataType[0] == 'R':  # Real data
            ierr, data = psspy.abrnreal(**parameters)
        elif dataType[0] == 'C':  # Character data
            ierr, data = psspy.abrnchar(**parameters)
        elif dataType[0] == 'X':  # Complex data
            ierr, data = psspy.abrncplx(**parameters)
        else:
            bsprint(f"[ERROR] Unsupported data type '{dataType[0]}' for abrnString '{abrnString}'.",app=app)
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


        if ierr != 0:
            bsprint(f"[ERROR] Failed to retrieve data for abrnString '{abrnString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None

        if DebugPrint:
            bsprint(f"[DEBUG] Successfully retrieved data for '{abrnString}': {data[0]}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return data

    except Exception as e:
        bsprint(f"[ERROR] Exception occurred while retrieving data: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    



async def BrnTrip(t, BSPSSEPyBrn, BranchID=None, BranchName=None, BranchFromBus=None, BranchToBus=None, DebugPrint=False,app=None):
    """
    Trips a branch based on its ID, name, or bus connection and updates extended info columns.

    Arguments:
        t: float
            Current simulation time.
        BSPSSEPyBrn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy branch data.
        BranchID: str or int
            The unique ID of the branch (optional).
        BranchName: str
            The name of the branch (optional).
        BranchFromBus: int or str
            The "from" bus number or name (optional).
        BranchToBus: int or str
            The "to" bus number or name (optional).
        DebugPrint: bool
            Enable detailed debug output (default = False).

    Returns:
        int:
            ierr: The status of the action applied (ierr = 0 --> success!).
    """
    # Initial debug message
    if DebugPrint:
        bsprint(f"[DEBUG] BranchTrip called with inputs:\n"
              f"  BranchID: {BranchID}\n"
              f"  BranchName: {BranchName}\n"
              f"  FromBus: {BranchFromBus}\n"
              f"  ToBus: {BranchToBus}\n"
              f"  Simulation Time: {t}s\n",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Resolve BranchName if only bus info is provided
    if not BranchName and (BranchFromBus and BranchToBus):
        BranchName = await GetBrnInfo(
            BrnKeys=["BRANCHNAME"],
            FromBus=BranchFromBus,
            ToBus=BranchToBus,
            BSPSSEPyBrn=BSPSSEPyBrn,
            DebugPrint=DebugPrint,
            app=app,
        )
        if not BranchName:
            bsprint(f"[ERROR] Could not identify branch between buses {BranchFromBus} and {BranchToBus}.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None
    # Fetch branch details
    BranchRow = await GetBrnInfo(
        BrnKeys=["FROMNUMBER", "TONUMBER", "ID", "STATUS", "BRANCHNAME"],
        BranchName=BranchName,
        BSPSSEPyBrn=BSPSSEPyBrn,
        DebugPrint=DebugPrint,
        app=app,
    )
    
    if BranchRow is None or len(BranchRow) == 0:
        bsprint(f"[ERROR] Branch not found for ID={BranchID}, Name={BranchName}, "
              f"FromBus={BranchFromBus}, ToBus={BranchToBus}.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    # Extract branch information
    BranchFromBus = BranchRow["FROMNUMBER"].iloc[0]
    BranchToBus = BranchRow["TONUMBER"].iloc[0]
    BranchID = BranchRow["ID"].iloc[0]
    BranchName = BranchRow["BRANCHNAME"].iloc[0]
    BranchStatus = int(BranchRow["STATUS"].iloc[0])

    # Debug message with resolved values
    if DebugPrint:
        bsprint(f"[DEBUG] Resolved branch details:\n"
              f"  BranchID: {BranchID}\n"
              f"  BranchName: {BranchName}\n"
              f"  FromBus: {BranchFromBus}\n"
              f"  ToBus: {BranchToBus}\n"
              f"  Status: {'Closed' if BranchStatus == 1 else 'Tripped'}\n",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Check if the branch is already tripped
    if BranchStatus != 1:
        bsprint(f"[INFO] Branch '{BranchName}' is already tripped.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return 0

    # Attempt to trip the branch
    try:
        if DebugPrint:
            bsprint(f"[DEBUG] Attempting to trip branch '{BranchName}' between buses {BranchFromBus} and {BranchToBus}.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        ierr = psspy.dist_branch_trip(BranchFromBus, BranchToBus, BranchID)

        if ierr != 0:
            bsprint(f"[ERROR] Failed to trip branch '{BranchName}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return ierr

        # Ensure proper matching for FromBus and ToBus in BSPSSEPyBrn
        FromBusCondition = BSPSSEPyBrn["FROMNUMBER"].apply(str) == str(BranchFromBus)
        ToBusCondition = BSPSSEPyBrn["TONUMBER"].apply(str) == str(BranchToBus)
        IDCondition = BSPSSEPyBrn["ID"] == BranchID

        NewStatus = await GetBrnInfo("STATUS", BranchName=BranchName, DebugPrint=DebugPrint, app=app)

        if not(BSPSSEPyBrn is None or BSPSSEPyBrn.empty):
            # Update the BSPSSEPyBrn DataFrame
            BSPSSEPyBrn.loc[
                FromBusCondition & ToBusCondition & IDCondition,
                ["BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "STATUS"]
            ] = ["Tripped", "Trip", t, "Branch successfully tripped.", NewStatus]

        if DebugPrint:
            bsprint(f"[SUCCESS] Successfully tripped branch '{BranchName}'. Updated BSPSSEPyBrn DataFrame.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        return ierr

    except KeyError as e:
        bsprint(f"[ERROR] Missing key during BranchTrip operation: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    except Exception as e:
        bsprint(f"[ERROR] Unexpected error during BranchTrip: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None


async def BrnClose(t, BSPSSEPyBrn=None, BSPSSEPyBus=None, BranchID=None, BranchName=None, BranchFromBus=None, BranchToBus=None, CalledByGen = False, DebugPrint=False, app=None):
    """
    Closes a branch based on its ID, name, or bus connection and updates extended info columns.

    Arguments:
        t: float
            Current simulation time.
        BSPSSEPyBrn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy branch data.
        BranchID: str or int
            The unique ID of the branch (optional).
        BranchName: str
            The name of the branch (optional).
        BranchFromBus: int or str
            The "from" bus number or name (optional).
        BranchToBus: int or str
            The "to" bus number or name (optional).
        DebugPrint: bool
            Enable detailed debug output (default = False).

    Returns:
        int:
            ierr: The status of the action applied (ierr = 0 --> success!).
    """
    if DebugPrint:
        bsprint(f"[DEBUG] BranchClose called with inputs:\n"
              f"  BranchID: {BranchID}\n"
              f"  BranchName: {BranchName}\n"
              f"  FromBus: {BranchFromBus}\n"
              f"  ToBus: {BranchToBus}\n"
              f"  Simulation Time: {t}s\n",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Resolve BranchName if only bus info is provided
    if not BranchName and (BranchFromBus and BranchToBus):
        BranchName = await GetBrnInfo(
            BrnKeys=["BRANCHNAME"],
            FromBus=BranchFromBus,
            ToBus=BranchToBus,
            BSPSSEPyBrn=BSPSSEPyBrn,
            DebugPrint=DebugPrint,
            app=app,
        )
        if not BranchName:
            bsprint(f"[ERROR] Could not identify branch between buses {BranchFromBus} and {BranchToBus}.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None

    # Fetch branch details
    BranchRow = await GetBrnInfo(
        BrnKeys=["FROMNUMBER", "TONUMBER", "ID", "STATUS", "BRANCHNAME", "GenControlled"],
        BranchName=BranchName,
        BSPSSEPyBrn=BSPSSEPyBrn,
        DebugPrint=DebugPrint,
        app=app,
    )

    if BranchRow is None or len(BranchRow) == 0:
        bsprint(f"[ERROR] Branch not found for ID={BranchID}, Name={BranchName}, "
              f"FromBus={BranchFromBus}, ToBus={BranchToBus}.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    # Extract branch information
    BranchFromBus = int(BranchRow["FROMNUMBER"].iloc[0])
    BranchToBus = int(BranchRow["TONUMBER"].iloc[0])
    BranchID = BranchRow["ID"].iloc[0]
    BranchName = BranchRow["BRANCHNAME"].iloc[0]
    BranchStatus = int(BranchRow["STATUS"].iloc[0])
    BrnGenControlled = BranchRow["GenControlled"].values[0]


    if DebugPrint:
        bsprint(f"[DEBUG] Resolved branch details:\n"
              f"  BranchID: {BranchID}\n"
              f"  BranchName: {BranchName}\n"
              f"  FromBus: {BranchFromBus}\n"
              f"  ToBus: {BranchToBus}\n"
              f"  Status: {'Closed' if BranchStatus == 1 else 'Tripped'}\n"
              f"  GenControlled: {BrnGenControlled}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Check if the branch is already closed
    if BranchStatus == 1:
        bsprint(f"[INFO] Branch '{BranchName}' is already closed.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return 0

    # Ensure both buses are operational
    if (CalledByGen & BrnGenControlled) or not BrnGenControlled:
        try:
            FromBusTYPE = await GetBusInfo(BusKeys="TYPE", BusNumber=BranchFromBus, DebugPrint=DebugPrint,app=app)
            ToBusTYPE = await GetBusInfo(BusKeys="TYPE", BusNumber=BranchToBus, DebugPrint=DebugPrint,app=app)

            if FromBusTYPE == 4:  # Tripped
                if DebugPrint:
                    bsprint(f"[DEBUG] FromBus {BranchFromBus} is tripped. Attempting to close it.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                ierr = await BusClose(t, BusNumber=BranchFromBus, BSPSSEPyBus=BSPSSEPyBus, DebugPrint=DebugPrint,app=app)
                if ierr != 0:
                    bsprint(f"[ERROR] Failed to close FromBus {BranchToBus}. Aborting Trn close.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                    return ierr

            if ToBusTYPE == 4:  # Tripped
                if DebugPrint:
                    bsprint(f"[DEBUG] ToBus {BranchToBus} is tripped. Attempting to close it.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                ierr = await BusClose(t, BusNumber=BranchToBus, BSPSSEPyBus = BSPSSEPyBus, DebugPrint=DebugPrint,app=app)
                if ierr != 0:
                    bsprint(f"[ERROR] Failed to close ToBus {BranchToBus}. Aborting Trn close.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                    return ierr


            if DebugPrint:
                bsprint(f"[DEBUG] Attempting to close branch '{BranchName}' between buses {BranchFromBus} and {BranchToBus}.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            ierr = psspy.dist_branch_close(BranchFromBus, BranchToBus, BranchID)

            if ierr != 0:
                bsprint(f"[ERROR] Failed to close branch '{BranchName}'. PSSE error code: {ierr}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                return ierr

            NewStatus = await GetBrnInfo("STATUS", BranchName=BranchName, DebugPrint=DebugPrint,app=app)


            # Ensure proper matching for FromBus and ToBus in BSPSSEPyBrn
            FromBusCondition = BSPSSEPyBrn["FROMNUMBER"].apply(str) == str(BranchFromBus)
            ToBusCondition = BSPSSEPyBrn["TONUMBER"].apply(str) == str(BranchToBus)
            IDCondition = BSPSSEPyBrn["ID"] == BranchID
            
            if not(BSPSSEPyBrn is None or BSPSSEPyBrn.empty):
                # Update the BSPSSEPyBrn DataFrame
                BSPSSEPyBrn.loc[
                    FromBusCondition & ToBusCondition & IDCondition,
                    ["BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "STATUS"]
                ] = ["Closed", "Close", t, "Branch successfully closed.", NewStatus]

            if DebugPrint:
                bsprint(f"[SUCCESS] Successfully closed branch '{BranchName}'. Updated BSPSSEPyBrn DataFrame.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return ierr


        except KeyError as e:
            bsprint(f"[ERROR] Missing key during BranchClose operation: {e}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None
        except Exception as e:
            bsprint(f"[ERROR] Unexpected error during BranchClose: {e}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None
        
    else:
        bsprint(f"[ERROR] This branch is tied to a generator. Don't attempt to close it manually. It can be controlled through GenEnable function to model generator phases.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return -999