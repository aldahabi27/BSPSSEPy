# BSPSSEPy Bus Functions
# This Python module contains all 'Bus' related functions for the BSPSSEPy framework:
#
# 1. GetBusInfo: Retrieves specific information about buses based on user-specified keys, either from PSSE or BSPSSEPyBus dataFrame.
#    - Handles cases for single/multiple keys and specific/all buses.
#
# 2. GetBusInfoPSSE: Fetches bus-related data directly from PSSE using the PSSE library.
#
# 3. BusTrip: Trips a bus (sets its status in PSSE to 4) and updates the BSPSSEPyBus dataFrame.
#
# 4. BusClose: Resets a bus to its original type (restores the type from BSPSSEPyType in BSPSSEPyBus) and updates the BSPSSEPyBus dataFrame.
#
# This module ensures dynamic interaction with PSSE for real-time data, while allowing extended tracking and simulation-specific metadata updates through the BSPSSEPyBus dataFrame.
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

import psspy
import pandas as pd
from Functions.BSPSSEPy.BSPSSEPyDictionary import *
from .BSPSSEPyDefaultVariables import *
import numbers
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint
import asyncio


async def GetBusInfo(BusKeys, # The key(s) for the required information of the bus
               Bus=None,    # Bus identifier --> could be BusName or BusNumber (optional)
               BusName=None,    # Bus Name (optional)
               BusNumber=None,  # Bus Number (optional)
               BSPSSEPyBus=None,    # BSPSSEPyBus dataFrane containing BSPSSEPy extra information associated with the Bus (optional) 
               DebugPrint=False,    # Enable detailed debug output
               app=None,):
    """
    Retrieves information about buses based on the specified keys.

    This function fetches the request data from both PSSE and the BSPSSEPyBus dataFrame, providing flexibility for dynamic and pre-stored data retrieval. Handles nultiple cases based on the input parameters:
    Case 1: Single key for a specific bus -> Returns a single value (str, int, float, or list).
    Case 2: Multiple keys for a specific bus -> Returns a pandas Series with the requested keys.
    Case 3: Single key for all buses -> Returns a pandas Series containing values for all buses.
    Case 4: Multiple keys for all buses -> Returns a pandas Series for all buses with the requested keys.

    Arguments:
        BusKeys (str or list of str): The key(s) for the required information. Valid keys include PSSE keys and BSPSSEPyBus columns.
        Bus (str or int, optional): Bus name or number.
        BusName (str, optional): Bus Name.
        BusNumber (int, optional): Bus Number.
        BSPSSEPyBus (pd.dataFrame, optional): dataFrame containing BSPSSEPy Bus data.
        DebugPrint (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        Varies based on input cases:
            - Case 1: Single value corresponding to the requested key for a specific Bus.
            - Case 2: pandas Series with the requested keys for a specific Bus.
            - Case 3: pandas Series with values for all Buses for the requested key.
            - Case 4: pandas Series for all Buses with the requested keys.

    Notes:
        - Input strings (e.g., BusKeys, Bus, BusName) are normalized by stripping extra spaces.
        - The function combines PSSE and BSPSSEPyBus data if both are available for comprehensive results.
        # - Filtering logic is applied based on BusName, BusNumber, and Bus.
    """
    if DebugPrint:
        bsprint(f"[DEBUG] Retrieving bus info for BusKeys: {BusKeys}, Bus: {Bus}, BusName: {BusName}, BusNumber: {BusNumber}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

        
    # Ensure BusKeys is a list
    if isinstance(BusKeys, str):
        BusKeys = [BusKeys]

    # Normalize strings to remove extra spaces
    BusKeys = [key.strip() for key in BusKeys]
    if isinstance(Bus, str) and Bus:
        BusName = Bus
    elif Bus:
        BusNumber = Bus


    
    if BusName is not None and BusName:
        BusName = BusName.strip()



    # Separate PSSE and BSPSSEPyBus keys
    ValidPSSEKeys = BusInfoDic.keys()
    ValidBSPSSEPyKeys = [] if BSPSSEPyBus is None else BSPSSEPyBus.columns


    # Add PSSE Keys needed for basic Bus operations
    _BusKeys = ["NAME", "NUMBER"]
    _BusKeysPSSE = list(_BusKeys)
    for key in BusKeys:
        if key in ValidPSSEKeys and key not in _BusKeysPSSE:
            _BusKeysPSSE.append(key)

    if DebugPrint:
        bsprint(f"[DEBUG] Fetching PSSE data for keys: {_BusKeysPSSE}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)


    # Ensure no duplicate columns are fetched from PSSE if BSPSSEPyBrn is provided
    if BSPSSEPyBus is not None and not BSPSSEPyBus.empty:
        # Remove overlapping keys from the PSSE fetch list
        ValidBSPSSEPyKeys = [key for key in ValidBSPSSEPyKeys if key not in _BusKeysPSSE]

    if DebugPrint:
        bsprint(f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {ValidBSPSSEPyKeys}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)


    # Fetch PSSE data for the required keys
    PSSEdata = {}
    for PSSEKey in _BusKeysPSSE:
        PSSEdata[PSSEKey] = await GetBusInfoPSSE(PSSEKey, DebugPrint=DebugPrint,app=app)


    # Combine PSSEdata and BSPSSEPyTrn (if provided) into a single dataFrame
    if BSPSSEPyBus is not None and not BSPSSEPyBus.empty:
        ValidBSPSSEPyTrn = BSPSSEPyBus[ValidBSPSSEPyKeys]
        PSSEdataDF = pd.DataFrame(PSSEdata)
        Combineddata = pd.concat([PSSEdataDF, ValidBSPSSEPyTrn], axis=1)
    else:
        Combineddata = pd.DataFrame(PSSEdata)

    if DebugPrint:
        bsprint(f"[DEBUG] Combined data:\n{Combineddata}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)


    # Filter Combineddata based on TrnName, FromBus, and ToBus
    if BusName:
        Combineddata = Combineddata[Combineddata["NAME"].str.strip() == BusName]
    elif BusNumber:
        Combineddata = Combineddata[(Combineddata["NUMBER"] == BusNumber)]
    
    if DebugPrint:
        bsprint(f"[DEBUG] Filtered data:\n{Combineddata}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)


    # Handle cases based on the number of BrnKeys
    if len(BusKeys) == 1:
        Key = BusKeys[0]
        return Combineddata[Key].iloc[0] if len(Combineddata) == 1 else Combineddata[Key]
    else:
        return Combineddata[BusKeys]



async def GetBusInfoPSSE(abusString,  # Requested info string - Check available strings in BusInfoDic
                   DebugPrint=False,    # Print debug information
                   app=None):
    """
    Retrieves specific bus information from PSSE.

    Parameters:
        abusString (str): Requested information key.
        DebugPrint (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        list or None: A list of the requested information if found, otherwise None.
    """
    if DebugPrint:
        bsprint(f"[DEBUG] Requested bus information for abusString: '{abusString}'",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Validate abusString
    if abusString not in BusInfoDic:
        bsprint(f"[ERROR] Invalid abusString '{abusString}'. Check BusInfoDic for valid options.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    try:
        # Fetch data type for the key
        ierr, datatype = psspy.abustypes([abusString])
        if ierr != 0:
            bsprint(f"[ERROR] Failed to fetch data type for abusString '{abusString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
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
            bsprint(f"[ERROR] Unsupported data type '{datatype[0]}' for abusString '{abusString}'.",app=app)
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
            bsprint(f"[ERROR] Failed to retrieve data for abusString '{abusString}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None

        if DebugPrint:
            bsprint(f"[DEBUG] Successfully retrieved data for '{abusString}': {data}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        return data

    except Exception as e:
        bsprint(f"[ERROR] Exception occurred while retrieving data: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None


async def BusTrip(t, BSPSSEPyBus=None, Bus = None, BusNumber=None, BusName=None, DebugPrint=False,app=None):
    """
    Trips a bus (sets its status to 4) and updates the BSPSSEPyBus dataFrame.

    Parameters:
        t (float): Current simulation time.
        BSPSSEPyBus (pd.dataFrame): dataFrame containing bus data.
        Bus (int or str, optional): could be Bus Number of Bus Name.
        BusNumber (int, optional): Bus Number.
        BusName (str, optional): Bus Name.
        DebugPrint (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """

    DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()


    # Initial debug message
    if DebugPrint:
        bsprint(f"[DEBUG] BusTrip called with inputs:\n"
              f"  Bus: {Bus}\n"
              f"  BusName: {BusName}\n"
              f"  BusNumber: {BusNumber}\n"
              f"  Simulation Time: {t}s\n",
              app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        

    # Identify the bus row based on name or number
    if isinstance(Bus, numbers.Number):
        BusNumber = Bus
    else:
        BusName = Bus


    # Resolve BusNumber if BusName is given
    if BusName:
        BusNumber = await GetBusInfo("NUMBER", Bus = BusName, BSPSSEPyBus=BSPSSEPyBus, DebugPrint=DebugPrint, app=app)
    elif not BusNumber:
        bsprint("[ERROR] Either BusName or BusNumber must be provided.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    
    BusRow = await GetBusInfo(
        BusKeys=["NAME", "NUMBER", "TYPE"],
        Bus = BusNumber,
        BSPSSEPyBus=BSPSSEPyBus,
        DebugPrint=DebugPrint,
        app=app
    )

    # Ensure the bus exists in the dataFrame
    if BusRow.empty:
        bsprint(f"[ERROR] Bus with Name '{BusName}' or Number '{BusNumber}' not found.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    
    BusNumber = BusRow["NUMBER"].iloc[0]
    BusName = BusRow["NAME"].iloc[0]
    BusType = BusRow["TYPE"].iloc[0]

    # Debug message with resolved values
    if DebugPrint:
        bsprint(f"[DEBUG] Resolved Bus details:\n"
              f"  BusName: {BusName}\n"
              f"  BusNumber: {BusNumber}\n"
              f"  BusType: {BusType}\n",
              app=app
             )
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    
    # Change bus status in PSSE to 4 (tripped)
    ierr = psspy.bus_chng_4(BusNumber, 0,
            [4, DefaultInt, DefaultInt, DefaultInt],
            [DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal],
            DefaultChar)

    if ierr != 0:
        bsprint(f"[ERROR] Failed to trip bus with Number '{BusNumber}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return ierr

    NewType = await GetBusInfo("TYPE", Bus = BusNumber, DebugPrint=DebugPrint,app=app)

    if not(BSPSSEPyBus is None or BSPSSEPyBus.empty):
        # Update the BSPSSEPyBus dataFrame to reflect the action
        BSPSSEPyBus.loc[(BSPSSEPyBus["NUMBER"] == BusNumber) & (BSPSSEPyBus["NAME"] == BusName), [
            "BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "TYPE"
        ]] = ["Tripped", "Trip", t, "Bus successfully tripped.", NewType]

    if DebugPrint:
        bsprint(f"[SUCCESS] Bus with Number '{BusNumber}', Name '{BusName}' successfully tripped.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    return ierr


async def BusClose(t, BSPSSEPyBus=None, Bus = None, BusNumber=None, BusName=None, DebugPrint=False, app=None):
    """
    Resets a bus to its original type and updates the BSPSSEPyBus dataFrame.

    Parameters:
        t (float): Current simulation time.
        BSPSSEPyBus (pd.dataFrame): dataFrame containing bus data.
        Bus (int or str, optional): could be Bus Number of Bus Name.
        BusNumber (int, optional): Bus Number.
        BusName (str, optional): Bus Name.
        DebugPrint (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """
    DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()


    # Initial debug message
    if DebugPrint:
        bsprint(f"[DEBUG] BusClose called with inputs:\n"
              f"  Bus: {Bus}\n"
              f"  BusName: {BusName}\n"
              f"  BusNumber: {BusNumber}\n"
              f"  Simulation Time: {t}s\n",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        

    # Identify the bus row based on name or number
    if isinstance(Bus, numbers.Number):
        BusNumber = Bus
    else:
        BusName = Bus


    # Resolve BusNumber if BusName is given
    if BusName:
        BusNumber = await GetBusInfo("NUMBER", Bus = BusName, BSPSSEPyBus=BSPSSEPyBus, DebugPrint=DebugPrint,app=app)
    elif not BusNumber:
        bsprint("[ERROR] Either BusName or BusNumber must be provided.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    
    BusRow = await GetBusInfo(
        BusKeys=["NAME", "NUMBER", "TYPE", "BSPSSEPyType_0"],
        Bus = BusNumber,
        BSPSSEPyBus=BSPSSEPyBus,
        DebugPrint=DebugPrint,
        app=app
    )

    # Ensure the bus exists in the dataFrame
    if BusRow.empty:
        bsprint(f"[ERROR] Bus with Name '{BusName}' or Number '{BusNumber}' not found.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    
    BusNumber = BusRow["NUMBER"].iloc[0]
    # BusNumber = BusRow["NUMBER"].values[0]
    BusName = BusRow["NAME"].iloc[0]
    BusType = BusRow["TYPE"].iloc[0]
    BusType_0 = BusRow["BSPSSEPyType_0"].iloc[0]

    # Debug message with resolved values
    if DebugPrint:
        bsprint(f"[DEBUG] Resolved Bus details:\n"
              f"  BusName: {BusName}\n"
              f"  BusNumber: {BusNumber}\n"
              f"  BusType: {BusType}\n"
              f"  BusType_0: {BusType_0}\n",
              app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    
    # Change bus status in PSSE to 4 (tripped)
    ierr = psspy.bus_chng_4(BusNumber, 0,
            [BusType_0, DefaultInt, DefaultInt, DefaultInt],
            [DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal],
            DefaultChar)
    
    NewType = await GetBusInfo("TYPE", Bus=BusNumber, DebugPrint=DebugPrint,app=app)

    if ierr != 0:
        bsprint(f"[ERROR] Failed to close bus with Number '{BusNumber}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return ierr

    if not(BSPSSEPyBus is None or BSPSSEPyBus.empty):
        # Update the BSPSSEPyBus dataFrame to reflect the action
        BSPSSEPyBus.loc[(BSPSSEPyBus["NUMBER"] == BusNumber) & (BSPSSEPyBus["NAME"] == BusName), [
            "BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "TYPE"
        ]] = ["Closed", "Close", t, "Bus successfully Closed.", NewType]

    if DebugPrint:
        bsprint(f"[SUCCESS] Bus with Number '{BusNumber}', Name '{BusName}' successfully closed.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    return ierr




async def ChangeBusType(t, NewBusType, BSPSSEPyBus=None, Bus = None, BusNumber=None, BusName=None, DebugPrint=False, app=None):
    """
    This function allows for changing bus types manually during the simulation.

    Parameters:
        t (float): Current simulation time.
        NewBusType (int): 1,2,3,4
        BSPSSEPyBus (pd.dataFrame): dataFrame containing bus data.
        Bus (int or str, optional): could be Bus Number of Bus Name.
        BusNumber (int, optional): Bus Number.
        BusName (str, optional): Bus Name.
        DebugPrint (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        int: PSSE error code (0 for success).
    """
    DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()


    # Initial debug message
    if DebugPrint:
        bsprint(f"[DEBUG] BusClose called with inputs:\n"
              f"  BusType: {NewBusType}\n"
              f"  Bus: {Bus}\n"
              f"  BusName: {BusName}\n"
              f"  BusNumber: {BusNumber}\n"
              f"  Simulation Time: {t}s\n",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        

    # Identify the bus row based on name or number
    if isinstance(Bus, numbers.Number):
        BusNumber = Bus
    else:
        BusName = Bus


    # Resolve BusNumber if BusName is given
    if BusName:
        BusNumber = await GetBusInfo("NUMBER", Bus = BusName, BSPSSEPyBus=BSPSSEPyBus, DebugPrint=DebugPrint,app=app)
    elif not BusNumber:
        bsprint("[ERROR] Either BusName or BusNumber must be provided.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    
    BusRow = await GetBusInfo(
        BusKeys=["NAME", "NUMBER", "TYPE", "BSPSSEPyType_0"],
        Bus = BusNumber,
        BSPSSEPyBus=BSPSSEPyBus,
        DebugPrint=DebugPrint,
        app=app
    )

    # Ensure the bus exists in the dataFrame
    if BusRow.empty:
        bsprint(f"[ERROR] Bus with Name '{BusName}' or Number '{BusNumber}' not found.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    
    BusNumber = BusRow["NUMBER"].iloc[0]
    # BusNumber = BusRow["NUMBER"].values[0]
    BusName = BusRow["NAME"].iloc[0]
    BusType = BusRow["TYPE"].iloc[0]
    BusType_0 = BusRow["BSPSSEPyType_0"].iloc[0]

    # Debug message with resolved values
    if DebugPrint:
        bsprint(f"[DEBUG] Resolved Bus details:\n"
              f"  BusName: {BusName}\n"
              f"  BusNumber: {BusNumber}\n"
              f"  BusType: {BusType}\n"
              f"  BusType_0: {BusType_0}\n"
             ,app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    
    # Change bus status in PSSE to 4 (tripped)
    ierr = psspy.bus_chng_4(BusNumber, 0,
            [NewBusType, DefaultInt, DefaultInt, DefaultInt],
            [DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal, DefaultReal],
            DefaultChar)
    
    NewType = await GetBusInfo("TYPE", Bus=BusNumber, DebugPrint=DebugPrint,app=app)

    if ierr != 0:
        bsprint(f"[ERROR] Failed to close bus with Number '{BusNumber}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return ierr

    if not(BSPSSEPyBus is None or BSPSSEPyBus.empty):
        # Update the BSPSSEPyBus dataFrame to reflect the action
        BSPSSEPyBus.loc[(BSPSSEPyBus["NUMBER"] == BusNumber) & (BSPSSEPyBus["NAME"] == BusName), [
            "BSPSSEPyStatus", "BSPSSEPyLastAction", "BSPSSEPyLastActionTime", "BSPSSEPySimulationNotes", "TYPE"
        ]] = ["Closed", "ModifyType", t, "BusType modified successfully.", NewType] if NewType != 4 else ["Tripped", "ModifyType", t, "BusType modified successfully.", NewType]

    if DebugPrint:
        bsprint(f"[SUCCESS] Bus with Number '{BusNumber}', Name '{BusName}' successfully modified.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    return ierr