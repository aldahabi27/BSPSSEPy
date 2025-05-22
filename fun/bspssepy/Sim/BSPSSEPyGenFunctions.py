# BSPSSEPy Generators Functions
# This python code contains all 'Generator' related functions:
#
# 
#   1. GetAllGenerator: This function returns a pandas table with all information about all Generators.
#                       It can be used to check on the buses later using the functions below.
# 
#   
#   2. GeneratorStatus: This function returns the Generator status of the Generator of interest 
# 
# 
#
#    Last Update for this file was on BSPSSEPy Ver 0.1 (1 Dec. 2024)
#
#       BSPSSEPy Application
#       Copyright (c) 2024, Ilyas Farhat
#       by Ilyas Farhat
#    
#       This file is part of BSPSSEPy Application
#       Contact the developer at ilyas.farhat@outlook.com

import psspy
import pandas as pd
from Functions.BSPSSEPy.BSPSSEPyDictionary import *
from .BSPSSEPyChannels import FetchChannelValue
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint
import asyncio

    

async def GetGenInfo(GenKeys, # The key(s) for the required information of the generator(s)
               GenName=None,    # Generator Name (optional) --> could be a list
               Bus=None,        # Bus name or number where the generator(s) are (optional)
               BSPSSEPyGen=None, # BSPSSEPyGen DataFrame containing BSPSSEPy extra information associated with the generators (optional)
               DebugPrint=False, # Enable detailed debug output
               app=None,
               ):
    
    """
    Retrieves information about generators based on the specified keys.

    This function fetches the requested data from both PSSE and the BSPSSEPyGen DataFrame, providing flexibility for dynamic and pre-stored data retrieval. Handles multiple cases based on the input parameters:

    Key(s) for Genrator(s). If no generator is specified, then it will the corresponding values for all generators!


    Arguments:
        GenKeys (str or list of str): The key(s) for the required information. Valid keys include PSSE keys and BSPSSEPyGen columns.
        GenName (str or list of str, optional): Name of the generator to filter. Defaults to None.
        Bus (str or int, optional): Bus number or name where the generator(s) are located. Defaults to None.
        BSPSSEPyGen (pd.DataFrame, optional): The BSPSSEPyGen DataFrame containing generator data. Defaults to None.
        DebugPrint (bool, optional): Enable detailed debug output. Defaults to False.

    Returns:
        Depending on the input case:
            for single key with one generator --> it returns single value
            for any other case, it returns a pd.DataFrame.
    Notes:
        - Input strings (e.g., GenKeys, GenName, Bus) are normalized by stripping extra spaces.
        - The function combines PSSE and BSPSSEPyGen data if both are available for comprehensive results.
        # - Filtering logic is applied based on BranchName, FromBus, and ToBus.
    """


    # Debug logging
    if DebugPrint:
        bsprint(f"[DEBUG] Retrieving generator info for GenKeys: {GenKeys}, GenName: {GenName}, Bus: {Bus}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    # Ensure BrnKeys is a list
    if isinstance(GenKeys, str):
        GenKeys = [GenKeys]
        # Normalize strings to remove extra spaces
        GenKeys = [key.strip() for key in GenKeys]
    
    
    # Ensure GenName is a list
    if GenName is not None and isinstance(GenName, str):
        GenName = [GenName]
        # Normalize strings to remove extra spaces
        GenName = [gn.strip() for gn in GenName]
        if len(GenName) == 1:
            GenName = GenName[0]
    
    
    # Normalize strings to remove extra spaces
    if isinstance(Bus, str) and Bus:
        Bus = Bus.strip()
        BusKey = "NAME"
    elif Bus:
        BusKey = "NUMBER"
    else:
        BusKey = None
    

    ValidPSSEKeys = GenInfoDic.keys()
    ValidBSPSSEPyKeys = [] if BSPSSEPyGen is None else BSPSSEPyGen.columns

    # Add PSSE Keys needed for basic branch operations
    _GenKeys = ["ID", "MCNAME", "NAME", "NUMBER"]
    _GenKeysPSSE = list(_GenKeys)
    for key in GenKeys:
        if key in ValidPSSEKeys and key not in _GenKeysPSSE:
            _GenKeysPSSE.append(key)
    

    if DebugPrint:
        bsprint(f"[DEBUG] Fetching PSSE data for keys: {_GenKeysPSSE}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    

    #Ensure no duplicate columns are fetched from BSPSSEPyGen if it is provided
    if BSPSSEPyGen is not None and not BSPSSEPyGen.empty:
        # Remove overlapping keys from the dataframe search
        ValidBSPSSEPyKeys = [key for key in ValidBSPSSEPyKeys if key not in _GenKeysPSSE]


    if DebugPrint:
        bsprint(f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {ValidBSPSSEPyKeys}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    

    # Fetch PSSE data for the required keys
    PSSEData = {}
    for PSSEKey in _GenKeysPSSE:
        PSSEData[PSSEKey] = await GetGenInfoPSSE(PSSEKey, DebugPrint=DebugPrint, app=app)
    
    # Combine PSSEData and BSPSSEPyGen (if proivded) into a single DataFrame
    if BSPSSEPyGen is not None and not BSPSSEPyGen.empty:
        ValidBSPSSEPyGen = BSPSSEPyGen[ValidBSPSSEPyKeys]
        PSSEDataDF = pd.DataFrame(PSSEData)
        CombinedData = pd.concat([PSSEDataDF, ValidBSPSSEPyGen], axis=1)
    else:
        CombinedData = pd.DataFrame(PSSEData)

    if DebugPrint:
        bsprint(f"[DEBUG] Combined Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Filter CombinedData based on GenName or Bus

    if GenName:
        CombinedData = CombinedData[CombinedData["MCNAME"].str.strip() == GenName]
    elif BusKey:
        if BusKey == "NAME":
            CombinedData = CombinedData[CombinedData[BusKey].str.strip() == Bus]
        else:
            CombinedData = CombinedData[CombinedData[BusKey] == Bus]

    if DebugPrint:
        bsprint(f"[DEBUG] Filtered Data: \n {CombinedData}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    # Handle cases based on the number of GenKeys
    if len(GenKeys) == 1:
        Key = GenKeys[0]
        return CombinedData[Key].iloc[0] if len(CombinedData) == 1 else CombinedData[Key]
    else:
        return CombinedData[GenKeys]
    


async def GetGenInfoPSSE(amachstring, # Requested info string - check available strings in GenInfoDic
                   DebugPrint = False, # Print debug information
                   app=None,
                   ):
    """
    This function returns the requested information about the generators from PSSE. It accepts one key at a time and return the corresponding values of all generators.

    Arguments:
        amachstring (str)
            The requesteed info string - check available strings in GenInfoDic
        DebugPrint (bool, defaults to False)
    
    Returns:
        list or None:
            a list of the requested information if found, otherwise None
    
    Notes:
        The function will clean up any "strings lists from extra spaces" using "strip" function!
    """

    amachFlag = 4 #1 --> only in service machines at in-service plants (code 2 or 3), 2 --> all machines at in-service plants (type 2 or 3), 3--> in-service machines at all buses (all types including 1 and 4), 4 --> all machines)
        
    amachSID = -1   # treating the whole network as one system

    if DebugPrint:
        bsprint(f"[DEBUG] Requested generator information for amachstring: '{amachstring}'",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    

    # check if amachstring exists in GenInfoDic
    if amachstring not in GenInfoDic:
        bsprint(f"[ERROR] Invalid amachstring '{amachstring}'. Check GenInfoDic for valid options!",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    
    parameters = {
        'sid':amachSID,
        'flag':amachFlag,
        'string': [amachstring],
    }

    # Fetch the datatype for teh requested string
    ierr, dataType = psspy.amachtypes([amachstring])
    if ierr != 0:
        bsprint(f"[ERROR] Failed to fetch data type for amachstring '{amachstring}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    
    # Retrieve data based on the type
    try:
        if dataType[0] == 'I':  # Integer data
            ierr, data = psspy.amachint(**parameters)
        elif dataType[0] == 'R':  # Real data
            ierr, data = psspy.amachreal(**parameters)
        elif dataType[0] == 'C':  # Character data
            ierr, data = psspy.amachchar(**parameters)
        elif dataType[0] == 'X':  # Complex data
            ierr, data = psspy.amachcplx(**parameters)
        else:
            bsprint(f"[ERROR] Unsupported data type '{dataType[0]}' for amachstring '{amachstring}'.",app=app)
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
            bsprint(f"[ERROR] Failed to retrieve data for amachstring '{amachstring}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            return None

        if DebugPrint:
            bsprint(f"[DEBUG] Successfully retrieved data for '{amachstring}': {data}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return data

    except Exception as e:
        bsprint(f"[ERROR] Exception occurred while retrieving data: {e}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
 


    



async def ExtendBSPSSEPyGenDataFrame(
        BSPSSEPyGen,
        ConfigTable,
        SimConfig,
        BSPSSEPyTrn,
        BSPSSEPyBus,
        BSPSSEPyBrn,
        BSPSSEPyLoad,
        Config,
        DebugPrint=False,
        app=None
):
    
    from .BSPSSEPyLoadFunctions import NewLoad
    
    """
    Modify the given dataframe by adding columns related to generator phases and states
    based on the provided configuration table. Updates all generators in one call.

    Parameters:
        BSPSSEPyGen  (pd.DataFrame): The dataframe containing generator data.
        ConfigTable (list): A list of dictionaries with generator configurations, where each dictionary has the keys "Generator Name", "Bus Name", "Status", "Load Name", "Cranking Time", "Ramp Rate", "Generator Type", "Cranking Load Array".
    Returns:
        pd.DataFrame: The updated dataframe with the new columns and assigned values.

    Notes:
        - The function uses the ConfigTable to match and update each generator in BSPSSEPyGen .
        - If a generator in BSPSSEPyGen  is not found in ConfigTable, it uses default values.




        Status (str, optional): Default value for the "Generator Status" column if not in ConfigTable.
        LoadName (str, optional): Default value for the "Generator Load Name" column.
        CrankingTime (float, optional): Default value for the "Generator Cranking Time" column.
        RampRate (float, optional): Default value for the "Generator Ramp Rate" column.
        BSPSSEPyGeneratorType (str, optional): Default value for the "BSPSSEPy Generator Type" column.
        CrankingLoadArray (list, optional): Default value for the "Generator Cranking Load Array" column.

    """
    bsprint("Extending BSPSSEPyGen Dataframe...",app=app)
    await asyncio.sleep(app.bsprintasynciotime if app else 0)


    BSPSSEPyStatus=0         # 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active
    GenLoadName="Default"   # Default --> load name is "L[Gen Name]"
    GenCrankingTime=0.0    # TBD
    GenRampRate=0.0         # TBD
    BSPSSEPyGenType="NBS" # NBS or BS
    GenCrankingLoadPowerArray=[1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    AGCAlpha=0.0
    LoadDampConstant=0.0
    EffectiveSpeedDroop=0.05
    BiasScaling=1.0
    POPF = 0
    QOPF = 0


    # Add new columns if they don't already exist
    NewColumns = {
        "BSPSSEPyStatus": BSPSSEPyStatus,
        "GenLoadName": GenLoadName,
        "GenCrankingTime": GenCrankingTime,
        "GenRampRate": GenRampRate,
        "BSPSSEPyGenType": BSPSSEPyGenType,
        "GenCrankingLoadPowerArray": GenCrankingLoadPowerArray,
        "AGCAlpha": AGCAlpha,
        "LoadDampConstant": LoadDampConstant,  # D
        "EffectiveSpeedDroop": EffectiveSpeedDroop,  # R
        "BiasScaling": BiasScaling,  # Bias Scaling (Effective Bias = Bias * Bias Scaling)
        "EffectiveBias": 0.0,  # Effective Bias (updated by the simulation)
        "GenTrnBrnName": "",
        "POPF": 0.0,
        "QOPF": 0.0,

    }

        # Add new columns if they don't already exist
    for Col, DefaultValue in NewColumns.items():
        if Col not in BSPSSEPyGen.columns:
            if isinstance(DefaultValue, list):  # For list values, use object dtype
                BSPSSEPyGen[Col] = pd.Series([DefaultValue] * len(BSPSSEPyGen), dtype="object")
            else:
                BSPSSEPyGen[Col] = DefaultValue
            
            if DebugPrint:
                bsprint(f"[DEBUG] Added column '{Col}' with default value: {DefaultValue}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)


    for Config in ConfigTable:
        GenName = Config.get("Generator Name")
        # GeneratorID = Config.get("Generator ID")
        BusName = Config.get("Bus Name")

        if DebugPrint:
            bsprint(f"[DEBUG] Processing configuration for Generator Name: {GenName}, Bus Name: {BusName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Locate the generator based on GenName or BusName
        GeneratorIndices = None
        if GenName:
            GeneratorIndices = BSPSSEPyGen[BSPSSEPyGen["MCNAME"] == GenName].index
            if DebugPrint:
                bsprint(f"[DEBUG] Located generator index by Name ({GenName}): {list(GeneratorIndices)}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
        elif BusName:
            GeneratorIndices = BSPSSEPyGen[BSPSSEPyGen["NAME"] == BusName].index
            if DebugPrint:
                bsprint(f"[DEBUG] Located generator index by Bus Name ({BusName}): {list(GeneratorIndices)}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # If no matching generator is found, skip
        if GeneratorIndices is None or GeneratorIndices.empty:
            bsprint(f"Warning: No matching generator found for '{GenName or BusName}'. Skipping.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            continue

        if DebugPrint:
            bsprint(f"[DEBUG] Generator index to update: {list(GeneratorIndices)}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Extract configuration values or use defaults
        BSPSSEPyGenType = Config.get("Generator Type", BSPSSEPyGenType)
        BSPSSEPyStatus = 3 if BSPSSEPyGenType == "BS" else Config.get("Status", BSPSSEPyStatus)
        GenLoadName = Config.get("Load Name", GenLoadName)
        GenCrankingTime = Config.get("Cranking Time", GenCrankingTime)
        GenRampRate = Config.get("Ramp Rate", GenRampRate)
        GenCrankingLoadPowerArray = Config.get("Cranking Load Array", GenCrankingLoadPowerArray)
        AGCAlpha = Config.get("AGC Participation Factor", AGCAlpha)
        LoadDampConstant = Config.get("Load Damping Constant", LoadDampConstant)
        EffectiveSpeedDroop = Config.get("Effective Speed Droop", EffectiveSpeedDroop)
        BiasScaling = Config.get("Bias Scaling", BiasScaling)
        POPF = Config.get("POPF", POPF)
        QOPF = Config.get("QOPF", QOPF)
        UseGenRampRate = Config.get("UseGenRampRate", False)
        LoadEnabledResponse = Config.get("Load Enabled Response", False)
        LERPF = Config.get("LERPF", -1)


        # if DebugPrint:
            # bsprint(f"[DEBUG] Calling GetGeneratorInfoFun with string = 'Active Power Output (Pgen) MW'",app=app)
            # await asyncio.sleep(app.bsprintasynciotime if app else 0)
        # Gref = GetGeneratorInfoFun("Active Power Output (Pgen) MW", GenName = GenName, DebugPrint=DebugPrint)
        
        # Gref = 0
            
        # Vref = GetGeneratorInfoFun("PU", GenName = GenName, DebugPrint=DebugPrint)
        # Vref = 0
        # if DebugPrint:
            # bsprint(f"[DEBUG] Gref = {Gref}, Vref = {Vref}",app=app)
            # await asyncio.sleep(app.bsprintasynciotime if app else 0)
        

        if DebugPrint:
            bsprint(f"[DEBUG] Extracted Config Values for '{GenName}':",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Status: {BSPSSEPyStatus} (0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active)",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Load Name: {GenLoadName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Cranking Time: {GenCrankingTime}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Ramp Rate: {GenRampRate}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Generator Type: {BSPSSEPyGenType}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Cranking Load Array: {GenCrankingLoadPowerArray}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        AGC Participation Factor: {AGCAlpha}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Load Damping Constant: {LoadDampConstant}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Effective Speed Droop: {EffectiveSpeedDroop}")
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Bias Scaling: {BiasScaling}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(f"        Effective Bias: {BiasScaling *(1/EffectiveSpeedDroop + LoadDampConstant)}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        
        # # Perform PSSE Load Flow Analysis to get Gref and Vref
        # BusNumber = Config.get("Bus Number")
        # # Fetch Gref and Vref using PSSE APIs
        # BusNumber = Config.get("Bus Number")
        # try:
        #     Gref = generator(BusNumber)
        #     Vref = pssdynmdl.get_vref(BusNumber)
        # except Exception as e:
        #     bsprint(f"Error fetching dynamic simulation data for Generator '{GenName}': {e}")
        #     Gref = 0
        #     Vref = 0

        Updates = {
            "BSPSSEPyStatus": BSPSSEPyStatus,
            "GenLoadName": GenLoadName,
            "GenCrankingTime": GenCrankingTime,
            "GenRampRate": GenRampRate,
            "BSPSSEPyGenType": BSPSSEPyGenType,
            "GenCrankingLoadPowerArray": GenCrankingLoadPowerArray,
            "AGCAlpha": AGCAlpha,
            "LoadDampConstant": LoadDampConstant,  # D
            "EffectiveSpeedDroop": EffectiveSpeedDroop,  # R
            "BiasScaling": BiasScaling,  # Bias Scaling (Effective Bias = Bias * Bias Scaling)
            "EffectiveBias": BiasScaling * ((1 / EffectiveSpeedDroop) + LoadDampConstant),
            "POPF": POPF,
            "QOPF": QOPF,
            "UseGenRampRate": UseGenRampRate,
            "LoadEnabledResponse": LoadEnabledResponse,
            "LERPF": LERPF,
        }

        # # Prepare values to update
        # Updates = {
        #     "Generator Status": Status,
        #     "Generator Load Name": LoadName,
        #     "Generator Cranking Time": CrankingTime,
        #     "Generator Ramp Rate": RampRate,
        #     "BSPSSEPy Generator Type": BSPSSEPyGeneratorType,
        #     "Generator Cranking Load Array": CrankingLoadArray,
        #     "AGC Participation Factor": AGCAlpha,
        #     "Load Damping Constant": D,  # D
        #     "Effective Speed Droop": R,  # R
        #     "Bias Scaling": BScaling,  # Bias Scaling (Effective Bias = Bias * Bias Scaling)
        #     "Effective Bias": BScaling *(1/R + D)
        # }
        
        # Update the generator(s) in the DataFrame
        for Col, Value in Updates.items():
            if DebugPrint:
                bsprint(f"[DEBUG] Updating column '{Col}' with value: {Value}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            
            if Col == "GenCrankingLoadPowerArray":  # Special handling for lists
                for idx in GeneratorIndices:  # Assign each list individually
                    BSPSSEPyGen.at[idx, Col] = Value
                    if DebugPrint:
                        bsprint(f"[DEBUG] Updated '{Col}' at index {idx} with list value: {Value}",app=app)
                        await asyncio.sleep(app.bsprintasynciotime if app else 0)
            else:
                BSPSSEPyGen.loc[GeneratorIndices, Col] = Value
                if DebugPrint:
                    bsprint(f"[DEBUG] Updated '{Col}' for generator(s) at indices {list(GeneratorIndices)} with value: {Value}",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # BSPSSEPyGen["BSPSSEPyStatus"] = BSPSSEPyGen["STATUS"].apply(
    #         lambda x: "In-Service" if x == 1 else "Offline"
    #     )

    BSPSSEPyGen["BSPSSEPyStatus_0"] = BSPSSEPyGen["BSPSSEPyStatus"] # Initial Status

    BSPSSEPyGen["BSPSSEPyLastAction"] = "Initialized"
    BSPSSEPyGen["BSPSSEPyLastActionTime"] = 0.0
    BSPSSEPyGen["BSPSSEPySimulationNotes"] = "Initialized"  
    BSPSSEPyGen["GREFChannel"] = -1      # --> corresponding to GREF in machine_array_channel (check the API - status(2) = 14)
    BSPSSEPyGen["VREFChannel"] = -1      # --> corresponding to VREF in machine_array_channel (check the API - status(2) = 11)
    BSPSSEPyGen["PELECChannel"] = -1         # --> corresponding to PELEC in machine_array_channel (check the API - status(2) = 2)
    BSPSSEPyGen["QELECChannel"] = -1         # --> corresponding to QELEC in machine_array_channel (check the API - status(2) = 3)
    BSPSSEPyGen["PMECHChannel"] = -1        # --> corresponding to PMECH in machine_array_channel (check the API - status(2) = 6)
    BSPSSEPyGen["FChannel"] = -1        # --> This is the frequency channel for the generator (will be fetched from Config.Channels)

    
    # Informaiton about the main connection element that connect the generator to the grid. This is required for "simulating the non-black-start generators connection back to the grid". The idea is to enable "load cranking" for some time, and then when we would like to connect the generator, we disconnect the load, close the branch/transformer and then control the output power of the generator until ramp-up phase is complete.
    BSPSSEPyGen["ConnectionType"] = None
    BSPSSEPyGen["ConnectionElementFromBus"] = None
    BSPSSEPyGen["ConnectionElementToBus"] = None
    BSPSSEPyGen["ConnectionElementID"] = None
    BSPSSEPyGen["ConnectionElementName"] = None

    

    bsprint("Adding 'GREF', 'VREF', 'PELEC', 'QELEC', 'PMECH' channels to all generators + custom loads for non-black-start generators.",app=app)
    await asyncio.sleep(app.bsprintasynciotime if app else 0)
    bsprint("Also adding informaiton about generator connection elements to BSPSSEPyGen",app=app)
    await asyncio.sleep(app.bsprintasynciotime if app else 0)
    # Loop through generators and process them based on their type
    for GeneratorRowIndex, GeneratorRow in BSPSSEPyGen.iterrows():
        GeneratorType = GeneratorRow.get("BSPSSEPyGenType", "")
        GenName = GeneratorRow['MCNAME']

        # Call the GetGeneratorConnectionPoint function
        ConnectionPoint = await GetGeneratorConnectionPoint(
            t = 0,
            BSPSSEPyGen=BSPSSEPyGen,
            BSPSSEPyBus=BSPSSEPyBus,
            GenName=GenName,
            BSPSSEPyTrn=BSPSSEPyTrn,
            BSPSSEPyBrn=BSPSSEPyBrn,
            DebugPrint=DebugPrint,
            app=app
        )

        # Add the connection point details to the Updates dictionary if found
        if not(ConnectionPoint):
            bsprint(f"[ERROR] Could not find a connection point for generator {GenName}.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if app:
                raise Exception("Error in ExtendBSPSSEPyGenDataFrame Function!")
            else:
                SystemExit(1)
        
        # Define the mapping between BSPSSEPyGen columns and ConnectionPoint keys
        keys = ["ConnectionType",
                "ConnectionElementFromBus",
                "ConnectionElementToBus",
                "ConnectionElementID",
                "ConnectionElementName"
                ]
        
       

        # Use a list comprehension to extract values from ConnectionPoint
        GeneratorRow[keys] = [ConnectionPoint[key] for key in keys]
        BSPSSEPyGen.loc[GeneratorRowIndex, keys] = [ConnectionPoint[key] for key in keys]


        # Map the desired keys in GeneratorRow to the corresponding keys in ConnectionPoint
        # BSPSSEPyGen.loc[GeneratorRowIndex,
        #                ["ConnectionType",
        #                 "ConnectionElementFromBus",
        #                 "ConnectionElementToBus",
        #                 "ConnectionElementID",
        #                 "ConnectionElementName"]] = [ConnectionPoint["ConnectionType"],
        #                                              ConnectionPoint["ConnectionElementFromBus"],
        #                                              ConnectionPoint["ConnectionElementToBus"],
        #                                              ConnectionPoint["ConnectionElementID"],
        #                                              ConnectionPoint["ConnectionElementName"],
        #                                              ]
        #     "ConnectionType": ConnectionPoint["ConnectionType"],
        #     "ConnectionElementFromBus": ConnectionPoint["ConnectionElementFromBus"],
        #     "ConnectionElementToBus": ConnectionPoint["ConnectionElementToBus"],
        #     "ConnectionElementID": ConnectionPoint["ConnectionElementID"],
        #     "ConnectionElementName": ConnectionPoint["ConnectionElementName"],  
        # })


        # Adding Channels for monitoring generator powers
        # Adding channel for Gref

        # bsprint(GenName)
        # bsprint("HI")
        for key in BSPSSEPyGenChannelsMapping.keys():
            ierr = psspy.machine_array_channel(
                [-1,        # Next available channel
                BSPSSEPyGenChannelsMapping[key],       # status(2) --> quantity to monitor
                int(GeneratorRow["NUMBER"]),  # Bus number corresponding to machine location
                ],
                GeneratorRow["ID"],       # ID of the machine
                key + GeneratorRow["MCNAME"],      # Channel Identifier
                )
            
            if ierr != 0:
                bsprint(f"[ERROR] Error occured during adding channel for Gen: {GeneratorRow['MCNAME']} to monitor {key} with key_status number: {BSPSSEPyGenChannelsMapping[key]}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            else:
                BSPSSEPyGen.at[GeneratorRowIndex,key+'Channel'] = SimConfig.CurrentChannelIndex
                if DebugPrint:
                    bsprint(f"[DEBUG] Successfully added channel for Gen: {GeneratorRow['MCNAME']} to monitor {key} with channel index {SimConfig.CurrentChannelIndex}",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                SimConfig.CurrentChannelIndex += 1 # Increament Channel index

        # Check if generator is a black-start generator
        if GeneratorType.lower() in ["blackstart", "black-start", "black start", "bs"]:
            bsprint(f"Skipping black-start generator: {GenName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            continue
        
        
        BusNumber = GeneratorRow['NUMBER']
        BusName = GeneratorRow['NAME']
        
        LoadBusNumber = GeneratorRow["ConnectionElementFromBus"] if (BusNumber == GeneratorRow["ConnectionElementToBus"]) else GeneratorRow["ConnectionElementToBus"]
        from .BSPSSEPyBusFunctions import GetBusInfo
        LoadBusName = await GetBusInfo("NAME", Bus = LoadBusNumber, DebugPrint=DebugPrint,app=app)

        LoadName = GeneratorRow['GenLoadName']
        if LoadName == "" or LoadName is None:
            LoadName = f"CL{GenName}"
        
        bsprint(f"Adding custom load for Genrator: {GenName} at bus {LoadBusName}(#{LoadBusNumber}), with loadname {LoadName}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Prepare power array for the new load
        CrankingLoadArray = GeneratorRow.get("GenCrankingLoadPowerArray","")
        # [
        #     GeneratorRow.get("Active Power Output (Pgen) MW", None),
        #     GeneratorRow.get("Reactive Power Output (Qgen) MVar", None),
        #     None,  # IP: Constant current active load
        #     None,  # IQ: Constant current reactive load
        #     None,  # YP: Constant admittance active load
        #     None,  # YQ: Constant admittance reactive load
        #     None   # Power Factor
        # ]

        # Add a custom load at the generator's bus location
        # bsprint(f"Adding custom load for non-black-start generator: {GenName}")
        BSPSSEPyLoad, ierr = await NewLoad(
            LoadName=LoadName,
            BSPSSEPyLoad=BSPSSEPyLoad,
            BusName=LoadBusName,
            BusNumber=LoadBusNumber,
            ElementName=GenName,
            ElementType="Gen",
            PowerArray=CrankingLoadArray,
            t = 0,
            DebugPrint=DebugPrint,
            app=app,
        )
    bsprint("DataFrame successfully updated with new generator phases and states.",app=app)
    await asyncio.sleep(app.bsprintasynciotime if app else 0)





    return BSPSSEPyGen, BSPSSEPyLoad


async def GetGeneratorConnectionPoint(t, BSPSSEPyGen, GenName, BSPSSEPyBus, BSPSSEPyTrn, BSPSSEPyBrn, DebugPrint=False, app=None):
    """
    Identifies the main connection point (transformer or branch) of a generator to the grid.
    
    Parameters:
        BSPSSEPyGen (pd.DataFrame): DataFrame containing generator information.
        GenName (str): Name of the generator for which the connection point is to be identified.
        BSPSSEPyTrn (pd.DataFrame): DataFrame containing transformer information.
        BSPSSEPyBrn (pd.DataFrame): DataFrame containing branch information.
        DebugPrint (bool, optional): If True, enables detailed debug output. Defaults to False.
    
    Returns:
        dict: A dictionary containing the connection type ("Transformer" or "Branch"),
              connection point details (e.g., buses and device ID), and connection row.
              Returns None if no connection point is found.
    
    Example Output:
        {
            "ConnectionType": "Transformer",
            "FromBus": 101,
            "ToBus": 102,
            "DeviceID": "T1",
            "DeviceName: "TFTrn1",
            "Row": <Row DataFrame>
        }
    """

    if DebugPrint:
        bsprint(f"[DEBUG] Running GetGeneratorConnectionPoint for {GenName}.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Get generator information
    try:
        GenRow = BSPSSEPyGen.loc[BSPSSEPyGen["MCNAME"] == GenName].iloc[0]
    except IndexError:
        bsprint(f"[ERROR] Generator {GenName} not found in BSPSSEPyGen.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    GenBus = GenRow["NAME"]

    # Setting GenBus as swing for all Gens
    from .BSPSSEPyBusFunctions import ChangeBusType
    # ierr = ChangeBusType(t = t, NewBusType=3, BSPSSEPyBus=BSPSSEPyBus, Bus=GenBus, DebugPrint=DebugPrint)


    # Identify the main connection device (transformer or branch)
    TransformerRow = BSPSSEPyTrn[
        (BSPSSEPyTrn["FROMNAME"] == GenBus) | (BSPSSEPyTrn["TONAME"] == GenBus)
    ]
    BranchRow = BSPSSEPyBrn[
        (BSPSSEPyBrn["FROMNAME"] == GenBus) | (BSPSSEPyBrn["TONAME"] == GenBus)
    ]

    # Check if a transformer is connected
    if not TransformerRow.empty:
        MainConnectionType = DeviceTypeMapping['t']
        MainConnectionRow = TransformerRow.iloc[0]
        DeviceName = MainConnectionRow["XFRNAME"]
        if GenRow["BSPSSEPyGenType"] != "BS":
            BSPSSEPyTrn.loc[BSPSSEPyTrn.index == MainConnectionRow.name, "GenControlled"] = True
    elif not BranchRow.empty:
        MainConnectionType = DeviceTypeMapping['branch']
        MainConnectionRow = BranchRow.iloc[0]
        DeviceName = MainConnectionRow["BRANCHNAME"]
        if GenRow["BSPSSEPyGenType"] != "BS":
            BSPSSEPyBrn.loc[BSPSSEPyBrn.index == MainConnectionRow.name, "GenControlled"] = True
    else:
        bsprint(f"[ERROR] No connection device found for generator {GenName} at Bus {GenBus}.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None

    # Extract connection details
    FromBus = MainConnectionRow["FROMNUMBER"]
    ToBus = MainConnectionRow["TONUMBER"]
    DeviceID = MainConnectionRow["ID"]

    if DebugPrint:
        bsprint(f"[DEBUG] Connection Point for {GenName}: {MainConnectionType} from Bus {FromBus} to Bus {ToBus}.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    return {
        "ConnectionType": MainConnectionType,
        "ConnectionElementFromBus": FromBus,
        "ConnectionElementToBus": ToBus,
        "ConnectionElementID": DeviceID,
        "ConnectionElementName": DeviceName,
        "Row": MainConnectionRow,
    }




async def GenEnable(
        BSPSSEPyGen,
        t,
        action,
        GenName,
        BSPSSEPyTrn,
        BSPSSEPyBrn,
        BSPSSEPyLoad,
        BSPSSEPyBus,
        BSPSSEPyAGCDF,
        Config,
        DebugPrint = False,
        app=None,
        ):
    """
    This function will go through the process of enabling a generator.
    The function will require the following information as input:

    Parameters:
        GenName: Generator name of interest
        BSPSSEPyGen: The dataframe containing generator data.
        t: The current simulation time
        action: The action dictionary entry that has all required information about the generator and its latest status. This action element needs to be updated to keep track of the progress of the action requested, to tell the main program when the action is completed.
        DebugPrint (bool, optional): Enable detauled debug output. Defaults to False.
    Returns:
        UpdatedActionStatus: The updated Action Status of the generator.
    """

    if DebugPrint:
        bsprint(f"[DEBUG] Running GenEnable function for action: {action}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    # get Gen row from BSPSSEPyGen
    BSPSSEPyGenRow = BSPSSEPyGen.loc[BSPSSEPyGen["MCNAME"] == action['ElementIDValue']].copy()



    from .BSPSSEPyDefaultVariables import BSPSSEPyDefaultVariablesFun
    DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()


    # To turn on this generator, we need to check at which phase it is currently!
    # 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active
    # Check if the generator is off --> To enter cranking phase
    if BSPSSEPyGenRow['BSPSSEPyStatus'].values[0] == 0:
        # So the generator is off, let's prepare it to "crank".
        
        
        #▂▃▄▅▆▇█▓▒░ Cranking (0 → 1) ░▒▓█▇▆▅▄▃▂

        
        # First check that there is an energized line or transformer at the generator bus!
        GenBusName = BSPSSEPyGenRow['NAME'].values[0]
        if DebugPrint:
            bsprint(f"[DEBUG] Checking if the generator is energized correctly by examining bus:{GenBusName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        if (
                any(
                    brn["BSPSSEPyStatus"] == "Closed"
                    for _, brn in BSPSSEPyBrn[
                        (BSPSSEPyBrn["FROMNAME"] == GenBusName) | (BSPSSEPyBrn["TONAME"] == GenBusName)
                    ].iterrows()
                )
                or any(
                    trn["BSPSSEPyStatus"] == "Closed"
                    for _, trn in BSPSSEPyTrn[
                        (BSPSSEPyTrn["FROMNAME"] == GenBusName) | (BSPSSEPyTrn["TONAME"] == GenBusName)
                    ].iterrows()
                )
            ):
            bsprint(f"[ERROR] Cannot Enter Cranking phase as GenBusName: {GenBusName} is energized. With this, the generator is already connected! Check the recovery plan to energize the 'far' bus first and crank the Genload before energizing the transformer/line connected to the generator! The program will exit.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            if app:
                raise Exception("Error in GenEnable function!")
            else:
                SystemExit(1)

        # Before Enrgizing the generator bus, or the transformer/transmission line connecting the generator, we first need to "Crank it". 

            # SystemError()
            # UpdatedActionStatus = 0
            # return UpdatedActionStatus
        
        

        # The generator is energized properly, let's start the cranking process!
        GenLoadName = BSPSSEPyGenRow['GenLoadName'].values[0]
        
        if DebugPrint:
            bsprint(f"[DEBUG] Generator is about to crank. Attempting to enable the associated load: {GenLoadName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        from .BSPSSEPyLoadFunctions import LoadEnable, LoadDisable
        # Enable GenLoad to start cranking and set the generator output power to zero
        ierr = await LoadEnable(t = t, BSPSSEPyLoad=BSPSSEPyLoad, LoadName=GenLoadName, DebugPrint=DebugPrint,app=app, BSPSSEPyAGCDF=BSPSSEPyAGCDF, BSPSSEPyGen=BSPSSEPyGen)

        if ierr != 0:
            bsprint(f"[ERROR] Could not enable GenLoad:{GenLoadName}. Generator did not start the cranking phase.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            UpdatedActionStatus = 0
            return UpdatedActionStatus
        
        if DebugPrint:
            bsprint(f"[DEBUG] GenLoad:{GenLoadName} was enabled successfully. Recording Cranking Start Time in BSPSSEPyGen dataframe",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)


        BSPSSEPyGenRow['BSPSSEPyStatus'] = 1    # 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active
        BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'Crank'
        BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
        BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Successfully entered cranking phase at t = {t}'

        # Write the row back to the DataFrame
        BSPSSEPyGen.loc[BSPSSEPyGen["MCNAME"] == GenName, :] = BSPSSEPyGenRow

        bsprint(f"Generator '{GenName}' started cranking phase.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

        UpdatedActionStatus = 1     # 0: Not started, 1: In progress, 2: Completed
        return UpdatedActionStatus
    

    # Check if the generator is Cranking --> To enter Ramp-up phase
    elif BSPSSEPyGenRow['BSPSSEPyStatus'].values[0] == 1:
        
        #▂▃▄▅▆▇█▓▒░ Ramp-up (1 → 2) ░▒▓█▇▆▅▄▃▂
        # So the generator is cranking. Check if cranking should stop and start ramping up the generator.
        
        
        # Check if Cranking time is met!
        if t < BSPSSEPyGenRow["GenCrankingTime"].values[0]*60 + BSPSSEPyGenRow["BSPSSEPyLastActionTime"].values[0]:
            if DebugPrint:
                bsprint(f"[DEBUG] Gen {GenName} is still cranking. (Cranking ends at t = {BSPSSEPyGenRow['GenCrankingTime'].values[0]*60 + BSPSSEPyGenRow['BSPSSEPyLastActionTime'].values[0]} - remaining {BSPSSEPyGenRow['GenCrankingTime'].values[0]*60 + BSPSSEPyGenRow['BSPSSEPyLastActionTime'].values[0] - t}s)",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            UpdatedActionStatus = 1
            return UpdatedActionStatus
        else:
            bsprint(f"Generator: '{GenName}' cranking time met. Disabling the associated load. ",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            

            # Cranking finished! Let's disable the GenLoad
            GenLoadName = BSPSSEPyGenRow['GenLoadName'].values[0]
        
            if DebugPrint:
                bsprint(f"[DEBUG] Attempting to disable the associated load: {GenLoadName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)


            from .BSPSSEPyLoadFunctions import LoadDisable
            
            # Enable GenLoad to start cranking and set the generator output power to zero
            ierr = await LoadDisable(t = t, BSPSSEPyLoad=BSPSSEPyLoad, LoadName=GenLoadName, DebugPrint=DebugPrint,app=app)

            
            if ierr != 0:
                bsprint(f"[ERROR] Could not disable GenLoad:{GenLoadName}. Generator did not stop the cranking phase.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                UpdatedActionStatus = 1
                return UpdatedActionStatus
            
            if DebugPrint:
                bsprint(f"[DEBUG] GenLoad:{GenLoadName} was disabled successfully. Energizing the connection element (TRN or BRN) to start the Ramp-up phase.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            

            ElementName = BSPSSEPyGenRow["ConnectionElementName"].values[0]

            if BSPSSEPyGenRow["ConnectionType"].values[0] == "TRN":
                from .BSPSSEPyTrnFunctions import TrnClose
                ierr = await TrnClose(t = t,TrnName=ElementName, BSPSSEPyTrn=BSPSSEPyTrn,BSPSSEPyBus=BSPSSEPyBus, CalledByGen=True, DebugPrint=DebugPrint, app=app)

                if ierr == 0:
                    if DebugPrint:
                        bsprint(f"[DEBUG] generator is connected successfully. Controlling the generator output power.",app=app)
                        await asyncio.sleep(app.bsprintasynciotime if app else 0)
                else:
                    bsprint("[ERROR] Encountered error during GenEnabled -- TrnClose function! Program will exit",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                    if app:
                        raise Exception("Error in GenEnable Function --> Could not start ramp-up phase!")
                    else:
                        SystemExit(1)
                
            elif BSPSSEPyGenRow["ConnectionType"].values[0] == "BRN":
                from .BSPSSEPyBrnFunctions import BrnClose
                ierr = await BrnClose(t = t, BranchName=ElementName, BSPSSEPyBrn=BSPSSEPyBrn,BSPSSEPyBus=BSPSSEPyBus, CalledByGen=True, DebugPrint=DebugPrint, app=app)

                if ierr == 0:
                    if DebugPrint:
                        bsprint(f"[DEBUG] generator is connected successfully. Controlling the generator output power.",app=app)
                        await asyncio.sleep(app.bsprintasynciotime if app else 0)
                else:
                    bsprint("[ERROR] Encountered error during GenEnabled -- BrnClose function! Program will exit",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                    if app:
                        raise Exception("Error in GenEnable Function --> Could not start ramp-up phase!")
                    else:
                        SystemExit(1)
            
            else:
                bsprint("[ERROR] Unkown element. Could not enable/connect the generator. Program will exit",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(1)


            # GenG = await FetchChannelValue(int(BSPSSEPyGenRow["GREFChannel"].values[0]), DebugPrint=DebugPrint,app=app)
            GenV = await FetchChannelValue(int(BSPSSEPyGenRow["VREFChannel"].values[0]), DebugPrint=DebugPrint,app=app)
            # GenP = await FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), DebugPrint=DebugPrint,app=app)
            # GenQ = await FetchChannelValue(int(BSPSSEPyGenRow["QELECChannel"].values[0]), DebugPrint=DebugPrint,app=app)
            # GenPm = await FetchChannelValue(int(BSPSSEPyGenRow["PMECHChannel"].values[0]), DebugPrint=DebugPrint,app=app)
            # bsprint(f"GenG: {GenG}, GenV: {GenV}, GenP: {GenP}, GenQ: {GenQ}, GenPm: {GenPm}",app=app)
            # await asyncio.sleep(app.bsprintasynciotime if app else 0)
            

            GenBusNum = BSPSSEPyGenRow["NUMBER"].values[0]
            GenID = BSPSSEPyGenRow["ID"].values[0]

            # Get the base MVA of the generator
            ierr, GeneratorMVA_Base = psspy.macdat(GenBusNum, GenID, 'MBASE')

            # Set the generator output real power to zero
            ierr = psspy.change_gref(GenBusNum, GenID, 0/GeneratorMVA_Base)

            if ierr != 0:
                bsprint(f"[ERROR] Error occured when setting generator: {GenName} output real power to zero. System will exit.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                if app:
                    raise Exception("Error in GenEnable Function!")
                else:
                    SystemExit(0)

            if DebugPrint:
                bsprint(f"[DEBUG] Successfully set generator: {GenName} output real power to zero.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            # Set the generator output reactive power to zero (we set Vref to Vref channel value -- no change in Q of teh generator is needed then)
            ierr = psspy.change_vref(GenBusNum, GenID, GenV)
            if ierr != 0:
                bsprint(f"[ERROR] Error occured when setting generator: {GenName} output reactive power to zero. System will exit.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)

            if DebugPrint:
                bsprint(f"[DEBUG] Successfully set generator: {GenName} output reactive power to zero.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            

            
            BSPSSEPyGenRow['BSPSSEPyStatus'] = 2
            BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'Ramp-Up'
            BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
            BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Successfully entered Ramping-up phase at t = {t}'

            # Write the row back to the DataFrame
            BSPSSEPyGen.loc[BSPSSEPyGen["MCNAME"] == GenName, :] = BSPSSEPyGenRow


            bsprint(f"Generator '{GenName}' started Ramping-Up phase.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            UpdatedActionStatus = 1
            return UpdatedActionStatus

            











            
            
    
    elif BSPSSEPyGenRow['BSPSSEPyStatus'].values[0] == 2:
        
        #▂▃▄▅▆▇█▓▒░ In-service (2 → 3) ░▒▓█▇▆▅▄▃▂
        # So the generator is Ramping-Up. Check if ramping-up should stop and start In-Service Phase of the generator.

        # The goal is to ramp up the generator to the POPF value for now.
        # When the generator is at around that value, the ramp-up phase will be considered complete.


        # Check if the generator is supposed to use the explicit ramp-rate defiend in BSPSSEPyGen or this will be embedded in the generator model (i.e. IEEEG1 model for example has its own ramp-rate model inside it)
        GenBusNum = BSPSSEPyGenRow["NUMBER"].values[0]
        GenID = BSPSSEPyGenRow["ID"].values[0]
        ierr, GeneratorMVA_Base = psspy.macdat(GenBusNum, GenID, 'MBASE')
        GenPOPF = BSPSSEPyGenRow["POPF"].values[0]
        GenPOPFpu = GenPOPF/GeneratorMVA_Base
        # Check if the generator is at the target power level
        GenP = await FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), DebugPrint=DebugPrint, app=app) * GeneratorMVA_Base

        
        if GenPOPF == 0:
            # Ramp-up is provided by the plan - exit the ramp-up phase!
            bsprint(f"Generator: '{GenName}' ramp-up phase is skipped (provided by the plan). Setting the generator to In-service phase.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
            BSPSSEPyGenRow['BSPSSEPyStatus'] = 3
            BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'In-service'
            BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
            BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Successfully entered In-service phase at t = {t}'

            # Write the row back to the DataFrame
            BSPSSEPyGen.loc[BSPSSEPyGen["MCNAME"] == GenName, :] = BSPSSEPyGenRow

            bsprint(f"Generator '{GenName}' started In-service phase.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            UpdatedActionStatus = 2
            return UpdatedActionStatus

        UseGenRampRate = BSPSSEPyGenRow["UseGenRampRate"].values[0]
        if UseGenRampRate: # will use the explicit ramp-rate defined in BSPSSEPyGen
            if DebugPrint:
                bsprint(f"[DEBUG] Using explicit ramp-rate for generator: {GenName} - Ramp Rate: {BSPSSEPyGenRow['GenRampRate'].values[0]} MW/min",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            GenRampRateSec = BSPSSEPyGenRow["GenRampRate"].values[0]/60         # convert the ramp rate to MW/sec

            if GenP > GenPOPF:
                GenRampRateSec = -GenRampRateSec
            
            
            # we use psspy.increment_gref function to increase/adjust generator output power gradually.
            ierr = psspy.increment_gref(GenBusNum, GenID, GenRampRateSec/GeneratorMVA_Base)  # Apply increment


            if ierr != 0:
                bsprint(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)


            
            # bsprint(f"t ={t}, GenP = {GenP}\t\tGenPOPF = {GenPOPF}\t\tGenRampRateSec = {GenRampRateSec}\t\te={100*(GenPOPF - GenP)/GenPOPF}%")
            
            # GenRampRate = BSPSSEPyGenRow["GenRampRate"].values[0]
            # # we use psspy.increment_gref function to increase/adjust generator output power gradually.
            # ierr = psspy.increment_gref(GenBusNum, GenID, GenRampRateSec/GeneratorMVA_Base)  # Apply increment

            # if ierr != 0:
            #     bsprint(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}")
            #     if app:
                #     raise Exception("Error in GenEnable function!")
                # else:
                #     SystemExit(0)

        else: # will use the generator model ramp-rate (we simply provide the target output power, and the generator model will take care of the ramp-rate)
            if DebugPrint:
                bsprint(f"[DEBUG] Using generator model ramp-rate for generator: {GenName} - Target Power: {GenPOPF} MW",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            # we use psspy.increment_gref function to increase/adjust generator output power gradually.
            ierr = psspy.increment_gref(GenBusNum, GenID, GenPOPFpu)  # Apply the target output power
            if ierr != 0:
                bsprint(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)
            UpdatedActionStatus = 2
            return UpdatedActionStatus
        
        # # Check if the generator is at the target power level
        # GenP = FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), DebugPrint=DebugPrint) * GeneratorMVA_Base

        if DebugPrint:
            bsprint(f"[DEBUG] Generator: {GenName} - Current Power: {GenP}, Target Power: {GenPOPF} MW",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        # If generator output power is within 1% of the target power, we consider the ramp-up phase to be complete, and we provide the generator with the reference value for Gref
        if (abs(GenPOPF - GenP)/GenPOPF <= 0.01):
            if UseGenRampRate:
                if (abs(GenPOPF - GenP) > GenRampRateSec):
                    if DebugPrint:
                        bsprint(f"[DEBUG] Generator: {GenName} is still ramping up. (Current Power: {GenP}, Target Power: {GenPOPF} MW)",app=app)
                        await asyncio.sleep(app.bsprintasynciotime if app else 0)
                    UpdatedActionStatus = 1
                    return UpdatedActionStatus

            # Set the generator output real power to zero
            ierr = psspy.change_gref(GenBusNum, GenID, GenPOPFpu)

            if ierr != 0:
                bsprint(f"[ERROR] Error occured when setting generator: {GenName} output real power to GenPOPF: {GenPOPF}.System will exit.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)

            if DebugPrint:
                bsprint(f"[DEBUG] Successfully set generator: {GenName} output real power to GenPOPF: {GenPOPF}.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            
            bsprint(f"Generator: '{GenName}' ramp-up phase completed. Setting the generator to In-service phase.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
            BSPSSEPyGenRow['BSPSSEPyStatus'] = 3
            BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'In-service'
            BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
            BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Successfully entered In-service phase at t = {t}'

            # Write the row back to the DataFrame
            BSPSSEPyGen.loc[BSPSSEPyGen["MCNAME"] == GenName, :] = BSPSSEPyGenRow

            bsprint(f"Generator '{GenName}' started In-service phase.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            UpdatedActionStatus = 2
            return UpdatedActionStatus
        
        else:    
            if DebugPrint:
                bsprint(f"[DEBUG] Generator: {GenName} is still ramping up. (Current Power: {GenP}, Target Power: {GenPOPF} MW)",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            
            """
            GetGenInfo("PGEN")
                0    0.175725
                1    0.000000
                2    0.059810
                Name: PGEN, dtype: float64
                GetGenInfo("QGEN")
            """

            UpdatedActionStatus = 1
            return UpdatedActionStatus


async def GenDisable(t, GenName, BSPSSEPyGen,BSPSSEPyBus, BSPSSEPyTrn, BSPSSEPyBrn, DebugPrint=False, app=None):
    """
    This function disables a generator based on its "name" only. The way it works is that it will check the Connection Point Element (TRN, BRN) and ensure that it is disabled.
    
    
    For a group of generators, we better make a new function that handle bus location and fetches all machines at that location for disabling them one by one.

    Arguments:
        t: float
            Current simulation time.
        GenName: str or int
            The unique name of the generator.
        BSPSSEPyGen: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy generators data.
        BSPSSEPyTrn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy Two-winding transformers data.
        BSPSSEPyBrn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy branch data.
        DebugPrint: bool
            Enable detailed debug output (default = False).

    Returns:
        int:
            0: The generator is successfully disabled
            Otherwise: an error occured.
    """

    # Initial debug message

    if DebugPrint:
        bsprint(f"[DEBUG] GenDisable called with inputs:\n"
              f"  t = {t}"
              f"  GenName: {GenName}"
            #   f"  BSPSSEPyGen: {BSPSSEPyGen}"
              ,app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    # Fetch Generator details
    GenRow = await GetGenInfo(["NAME", "MCNAME", "ID", "NUMBER", "STATUS", "ConnectionType", "ConnectionElementName", "BSPSSEPyStatus"], GenName=GenName, BSPSSEPyGen=BSPSSEPyGen, DebugPrint=DebugPrint,app=app)

   
    if GenRow is None or len(GenRow) == 0:
        bsprint(f"[ERROR] Generator not found for GenName = {GenName}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return None
    
    GenBusName = GenRow["NAME"].values[0]
    GenID = GenRow["ID"].values[0]
    GenBusNum = GenRow["NUMBER"].values[0]
    GenStatus = GenRow["STATUS"].values[0]
    GenBSPSSEPyStatus = GenRow["BSPSSEPyStatus"].values[0]
    GenConType = GenRow["ConnectionType"].values[0]
    GenConElementName = GenRow["ConnectionElementName"].values[0]
    

    if DebugPrint:
        bsprint(f"[DEBUG] Determining the connection point element (TRN or BRN) for Gen {GenName}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    if GenConType == "TRN":
        bsprint(f"Checking the status of the transformer connecting {GenName} to the grid:{GenConType} - {GenConElementName}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        from .BSPSSEPyTrnFunctions import GetTrnInfo, TrnTrip
        ElementStatus = await GetTrnInfo("STATUS", TrnName=GenConElementName, DebugPrint=DebugPrint,app=app)
        if ElementStatus != 0:
            if DebugPrint:
                bsprint(f"[DEBUG] The two-winding transformer: {GenConElementName} status is {ElementStatus}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            bsprint(f"Tripping the transformer connecting {GenName} --> {GenConType} - {GenConElementName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            await TrnTrip(t=t, BSPSSEPyTrn=BSPSSEPyTrn,TrnName=GenConElementName, DebugPrint=DebugPrint,app=app)
            
            if DebugPrint:
                bsprint(f"[DEBUG] Successfully tripped two-winding transformer: {GenConElementName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
        else:
            bsprint(f"The transformer connecting the generator is tripped already ({GenName} --> {GenConType} - {GenConElementName})",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)


    elif GenRow["ConnectionType"].values[0] == "BRN":
        bsprint(f"Checking the status of the branch connecting {GenName} to the grid:{GenConType} - {GenConElementName}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        from .BSPSSEPyBrnFunctions import GetBrnInfo, BrnTrip
        ElementStatus = await GetBrnInfo("STATUS", BranchName=GenConElementName, DebugPrint=DebugPrint,app=app)
        if ElementStatus != 0:
            if DebugPrint:
                bsprint(f"[DEBUG] The branch: {GenConElementName} status is {ElementStatus}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            bsprint(f"Tripping the branch connecting {GenName} --> {GenConType} - {GenConElementName}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            await BrnTrip(t=t, BSPSSEPyBrn=BSPSSEPyBrn, BranchName=GenConElementName, DebugPrint=DebugPrint,app=app)
            
            if DebugPrint:
                bsprint(f"[DEBUG] Successfully tripped Branch: {GenConElementName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
        else:
            bsprint(f"The branch connecting the generator is tripped already ({GenName} --> {GenConType} - {GenConElementName})",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
    else:
        bsprint(f"[ERROR] Could not identify how the generator is connected to the grid. program will exit!",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        if app:
            raise Exception("Error in GenDisable function!")
        else:
            SystemExit(1)
        


    from .BSPSSEPyDefaultVariables import BSPSSEPyDefaultVariablesFun
    DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()
        
    # Check if the generator status is 1 --> then disable it!
    # if GenBSPSSEPyStatus == 0:
    #     bsprint(f"[INFO] Generator '{GenName} at Bus '{GenBusNum}' is already disabled.")
    #     return 0
    
    from .BSPSSEPyBusFunctions import ChangeBusType

    ierr = await ChangeBusType(t = t, NewBusType=3, BSPSSEPyBus=BSPSSEPyBus, Bus=GenBusName, DebugPrint=DebugPrint,app=app)
    if ierr != 0:
        bsprint(f"[ERROR] Could not set the bus of Gen {GenName} (Bus {GenBusName}) to type 3 (swing), program will exit.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        if app:
            raise Exception("Error in GenEnable function!")
        else:
            SystemExit(1)
        
    # Updating BSPSSEPyGen to reflect that the generator is not connected
    if not(BSPSSEPyGen is None or BSPSSEPyGen.empty):
        GenUpdatedStatus = await GetGenInfo("STATUS", GenName=GenName, DebugPrint=DebugPrint,app=app)

        # Update the BSPSSEPyGen DataFrame
        BSPSSEPyGen.loc[
            (BSPSSEPyGen["MCNAME"].apply(str) == str(GenName)) &
            (BSPSSEPyGen["ID"].apply(str) == str(GenID)) &
            (BSPSSEPyGen["NUMBER"].apply(str) == str(GenBusNum)),
                ["BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "STATUS"]] = [0, "Disable", t, "Generator Successfully Disabled.", GenUpdatedStatus]
        

async def GenUpdate(
        BSPSSEPyGen,
        t,
        action,
        GenName,
        BSPSSEPyTrn,
        BSPSSEPyBrn,
        BSPSSEPyLoad,
        BSPSSEPyBus,
        BSPSSEPyAGCDF,
        Config,
        DebugPrint = False,
        app=None,
        ):
    """
    This function will go through the process of enabling a generator.
    The function will require the following information as input:

    Parameters:
        GenName: Generator name of interest
        BSPSSEPyGen: The dataframe containing generator data.
        t: The current simulation time
        action: The action dictionary entry that has all required information about the generator and its latest status. This action element needs to be updated to keep track of the progress of the action requested, to tell the main program when the action is completed.
        DebugPrint (bool, optional): Enable detauled debug output. Defaults to False.
    Returns:
        UpdatedActionStatus: The updated Action Status of the generator.
    """
    
    if DebugPrint:
        bsprint(f"[DEBUG] Running GenEnable function for action: {action}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    
    Values: dict = Config.BSPSSEPySequence.at[action["BSPSSEPySequenceRowIndex"], "Values"]
    # bsprint(f"Values Type = {type(Values)}"
    #         f"Values Content:\n{Values}")
    # await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    GenPSetPoint = Values["P"] if "P" in Values else None
    GenQSetPoint = Values["Q"] if "Q" in Values else None
    
    
    # get Gen row from BSPSSEPyGen
    BSPSSEPyGenRow = BSPSSEPyGen.loc[BSPSSEPyGen["MCNAME"] == action['ElementIDValue']].copy()



    from .BSPSSEPyDefaultVariables import BSPSSEPyDefaultVariablesFun
    DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()

    # Check if the generator is supposed to use the explicit ramp-rate defiend in BSPSSEPyGen or this will be embedded in the generator model (i.e. IEEEG1 model for example has its own ramp-rate model inside it)
    GenBusNum = BSPSSEPyGenRow["NUMBER"].values[0]
    GenID = BSPSSEPyGenRow["ID"].values[0]
    ierr, GeneratorMVA_Base = psspy.macdat(GenBusNum, GenID, 'MBASE')
    # GenTargetPower = BSPSSEPyGenRow["POPF"].values[0]
    GenPSetPointpu = GenPSetPoint/GeneratorMVA_Base
    # Check if the generator is at the target power level
    GenP = await FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), DebugPrint=DebugPrint, app=app) * GeneratorMVA_Base


    UseGenRampRate = BSPSSEPyGenRow["UseGenRampRate"].values[0]
    if UseGenRampRate: # will use the explicit ramp-rate defined in BSPSSEPyGen
        if DebugPrint:
            bsprint(f"[DEBUG] Using explicit ramp-rate for generator: {GenName} - Ramp Rate: {BSPSSEPyGenRow['GenRampRate'].values[0]} MW/min",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        GenRampRateSec = BSPSSEPyGenRow["GenRampRate"].values[0]/60         # convert the ramp rate to MW/sec

        if GenP > GenPSetPoint:
            GenRampRateSec = -GenRampRateSec
        
        
        # we use psspy.increment_gref function to increase/adjust generator output power gradually.
        ierr = psspy.increment_gref(GenBusNum, GenID, GenRampRateSec/GeneratorMVA_Base)  # Apply increment


        if ierr != 0:
            bsprint(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if app:
                raise Exception("Error in GenEnable function!")
            else:
                SystemExit(0)

        
        
        # bsprint(f"t ={t}, GenP = {GenP}\t\tGenPOPF = {GenPOPF}\t\tGenRampRateSec = {GenRampRateSec}\t\te={100*(GenPOPF - GenP)/GenPOPF}%")
        
        # GenRampRate = BSPSSEPyGenRow["GenRampRate"].values[0]
        # # we use psspy.increment_gref function to increase/adjust generator output power gradually.
        # ierr = psspy.increment_gref(GenBusNum, GenID, GenRampRateSec/GeneratorMVA_Base)  # Apply increment

        # if ierr != 0:
        #     bsprint(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}")
        #     if app:
            #     raise Exception("Error in GenEnable function!")
            # else:
            #     SystemExit(0)

    else: # will use the generator model ramp-rate (we simply provide the target output power, and the generator model will take care of the ramp-rate)
        if DebugPrint:
            bsprint(f"[DEBUG] Using generator model ramp-rate for generator: {GenName} - Target Power: {GenPSetPoint} MW",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        # we use psspy.increment_gref function to increase/adjust generator output power gradually.
        ierr = psspy.change_gref(GenBusNum, GenID, GenPSetPointpu)  # Apply the target output power
        if ierr != 0:
            bsprint(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if app:
                raise Exception("Error in GenUpdate function!")
            else:
                SystemExit(0)
        UpdatedActionStatus = 2

    # # Check if the generator is at the target power level
    # GenP = FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), DebugPrint=DebugPrint) * GeneratorMVA_Base

    if DebugPrint:
        bsprint(f"[DEBUG] Generator: {GenName} - Current Power: {GenP}, Target Power: {GenPSetPoint} MW",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    # If generator output power is within 1% of the target power, we consider the ramp-up phase to be complete, and we provide the generator with the reference value for Gref
    if (abs(GenPSetPoint - GenP)/GenPSetPoint <= 0.01):
        if UseGenRampRate:
            if (abs(GenPSetPoint - GenP) > GenRampRateSec):
                if DebugPrint:
                    bsprint(f"[DEBUG] Generator: {GenName} is still ramping up. (Current Power: {GenP}, Target Power: {GenPSetPoint} MW)",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                UpdatedActionStatus = 1
                return UpdatedActionStatus

        # Set the generator output real power to 
        ierr = psspy.change_gref(GenBusNum, GenID, GenPSetPointpu)

        if ierr != 0:
            bsprint(f"[ERROR] Error occured when setting generator: {GenName} output real power to GenPSetPoint: {GenPSetPoint}.System will exit.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if app:
                raise Exception("Error in GenUpdate function!")
            else:
                SystemExit(0)

        if DebugPrint:
            bsprint(f"[DEBUG] Successfully set generator: {GenName} output real power to GenPSetPoint: {GenPSetPoint}.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        bsprint(f"Generator: '{GenName}' Set-point updated.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
        BSPSSEPyGenRow['BSPSSEPyStatus'] = 3
        BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'Update Set-point'
        BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
        BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Updated Set-point to {GenPSetPoint}'

        # Write the row back to the DataFrame
        BSPSSEPyGen.loc[BSPSSEPyGen["MCNAME"] == GenName, :] = BSPSSEPyGenRow
        UpdatedActionStatus = 2
    
    # else:    
    #     if DebugPrint:
    #         bsprint(f"[DEBUG] Generator: {GenName} is still ramping up. (Current Power: {GenP}, Target Power: {GenPSetPoint} MW)",app=app)
    #         await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        """
        GetGenInfo("PGEN")
            0    0.175725
            1    0.000000
            2    0.059810
            Name: PGEN, dtype: float64
            GetGenInfo("QGEN")
        """

        # UpdatedActionStatus = 1
    return UpdatedActionStatus
