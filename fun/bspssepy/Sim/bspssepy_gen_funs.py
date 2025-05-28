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

# pyright: reportMissingImports=false
import psspy  # noqa: F401 pylint: disable=import-error
import pandas as pd
from fun.bspssepy.bspssepy_dict import *
from .bspssepy_channels import FetchChannelValue
from fun.bspssepy.app.app_helper_funs import bp
import asyncio

    

async def GetGenInfo(GenKeys, # The key(s) for the required information of the generator(s)
               GenName=None,    # Generator Name (optional) --> could be a list
               Bus=None,        # Bus name or number where the generator(s) are (optional)
               bspssepy_gen=None, # bspssepy_gen DataFrame containing BSPSSEPy extra information associated with the generators (optional)
               debug_print=False, # Enable detailed debug output
               app=None,
               ):
    
    """
    Retrieves information about generators based on the specified keys.

    This function fetches the requested data from both PSSE and the bspssepy_gen DataFrame, providing flexibility for dynamic and pre-stored data retrieval. Handles multiple cases based on the input parameters:

    Key(s) for Genrator(s). If no generator is specified, then it will the corresponding values for all generators!


    Arguments:
        GenKeys (str or list of str): The key(s) for the required information. Valid keys include PSSE keys and bspssepy_gen columns.
        GenName (str or list of str, optional): Name of the generator to filter. Defaults to None.
        Bus (str or int, optional): Bus number or name where the generator(s) are located. Defaults to None.
        bspssepy_gen (pd.DataFrame, optional): The bspssepy_gen DataFrame containing generator data. Defaults to None.
        debug_print (bool, optional): Enable detailed debug output. Defaults to False.

    Returns:
        Depending on the input case:
            for single key with one generator --> it returns single value
            for any other case, it returns a pd.DataFrame.
    Notes:
        - Input strings (e.g., GenKeys, GenName, Bus) are normalized by stripping extra spaces.
        - The function combines PSSE and bspssepy_gen data if both are available for comprehensive results.
        # - Filtering logic is applied based on BranchName, FromBus, and ToBus.
    """


    # Debug logging
    if debug_print:
        bp(f"[DEBUG] Retrieving generator info for GenKeys: {GenKeys}, GenName: {GenName}, Bus: {Bus}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
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
    

    ValidPSSEKeys = gen_info_dict.keys()
    ValidBSPSSEPyKeys = [] if bspssepy_gen is None else bspssepy_gen.columns

    # Add PSSE Keys needed for basic branch operations
    _GenKeys = ["ID", "MCNAME", "NAME", "NUMBER"]
    _GenKeysPSSE = list(_GenKeys)
    for key in GenKeys:
        if key in ValidPSSEKeys and key not in _GenKeysPSSE:
            _GenKeysPSSE.append(key)
    

    if debug_print:
        bp(f"[DEBUG] Fetching PSSE data for keys: {_GenKeysPSSE}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    

    #Ensure no duplicate columns are fetched from bspssepy_gen if it is provided
    if bspssepy_gen is not None and not bspssepy_gen.empty:
        # Remove overlapping keys from the dataframe search
        ValidBSPSSEPyKeys = [key for key in ValidBSPSSEPyKeys if key not in _GenKeysPSSE]


    if debug_print:
        bp(f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {ValidBSPSSEPyKeys}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    

    # Fetch PSSE data for the required keys
    PSSEData = {}
    for PSSEKey in _GenKeysPSSE:
        PSSEData[PSSEKey] = await GetGenInfoPSSE(PSSEKey, debug_print=debug_print, app=app)
    
    # Combine PSSEData and bspssepy_gen (if proivded) into a single DataFrame
    if bspssepy_gen is not None and not bspssepy_gen.empty:
        ValidBSPSSEPyGen = bspssepy_gen[ValidBSPSSEPyKeys]
        PSSEDataDF = pd.DataFrame(PSSEData)
        CombinedData = pd.concat([PSSEDataDF, ValidBSPSSEPyGen], axis=1)
    else:
        CombinedData = pd.DataFrame(PSSEData)

    if debug_print:
        bp(f"[DEBUG] Combined Data:\n{CombinedData}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Filter CombinedData based on GenName or Bus

    if GenName:
        CombinedData = CombinedData[CombinedData["MCNAME"].str.strip() == GenName]
    elif BusKey:
        if BusKey == "NAME":
            CombinedData = CombinedData[CombinedData[BusKey].str.strip() == Bus]
        else:
            CombinedData = CombinedData[CombinedData[BusKey] == Bus]

    if debug_print:
        bp(f"[DEBUG] Filtered Data: \n {CombinedData}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    # Handle cases based on the number of GenKeys
    if len(GenKeys) == 1:
        Key = GenKeys[0]
        return CombinedData[Key].iloc[0] if len(CombinedData) == 1 else CombinedData[Key]
    else:
        return CombinedData[GenKeys]
    


async def GetGenInfoPSSE(amachstring, # Requested info string - check available strings in gen_info_dict
                   debug_print = False, # Print debug information
                   app=None,
                   ):
    """
    This function returns the requested information about the generators from PSSE. It accepts one key at a time and return the corresponding values of all generators.

    Arguments:
        amachstring (str)
            The requesteed info string - check available strings in gen_info_dict
        debug_print (bool, defaults to False)
    
    Returns:
        list or None:
            a list of the requested information if found, otherwise None
    
    Notes:
        The function will clean up any "strings lists from extra spaces" using "strip" function!
    """

    amachFlag = 4 #1 --> only in service machines at in-service plants (code 2 or 3), 2 --> all machines at in-service plants (type 2 or 3), 3--> in-service machines at all buses (all types including 1 and 4), 4 --> all machines)
        
    amachSID = -1   # treating the whole network as one system

    if debug_print:
        bp(f"[DEBUG] Requested generator information for amachstring: '{amachstring}'",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    

    # check if amachstring exists in gen_info_dict
    if amachstring not in gen_info_dict:
        bp(f"[ERROR] Invalid amachstring '{amachstring}'. Check gen_info_dict for valid options!",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    
    parameters = {
        'sid':amachSID,
        'flag':amachFlag,
        'string': [amachstring],
    }

    # Fetch the datatype for teh requested string
    ierr, dataType = psspy.amachtypes([amachstring])
    if ierr != 0:
        bp(f"[ERROR] Failed to fetch data type for amachstring '{amachstring}'. PSSE error code: {ierr}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
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
            bp(f"[ERROR] Unsupported data type '{dataType[0]}' for amachstring '{amachstring}'.",app=app)
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
            bp(f"[ERROR] Failed to retrieve data for amachstring '{amachstring}'. PSSE error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if debug_print:
            bp(f"[DEBUG] Successfully retrieved data for '{amachstring}': {data}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        return data

    except Exception as e:
        bp(f"[ERROR] Exception occurred while retrieving data: {e}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
 


    



async def ExtendBSPSSEPyGenDataFrame(
        bspssepy_gen,
        ConfigTable,
        SimConfig,
        bspssepy_trn,
        bspssepy_bus,
        bspssepy_brn,
        bspssepy_load,
        config,
        debug_print=False,
        app=None
):
    
    from .bspssepy_load_funs import NewLoad
    
    """
    Modify the given dataframe by adding columns related to generator phases and states
    based on the provided configuration table. Updates all generators in one call.

    Parameters:
        bspssepy_gen  (pd.DataFrame): The dataframe containing generator data.
        ConfigTable (list): A list of dictionaries with generator configurations, where each dictionary has the keys "Generator Name", "Bus Name", "Status", "load Name", "Cranking Time", "Ramp Rate", "Generator Type", "Cranking load Array".
    Returns:
        pd.DataFrame: The updated dataframe with the new columns and assigned values.

    Notes:
        - The function uses the ConfigTable to match and update each generator in bspssepy_gen .
        - If a generator in bspssepy_gen  is not found in ConfigTable, it uses default values.




        Status (str, optional): Default value for the "Generator Status" column if not in ConfigTable.
        LOADNAME (str, optional): Default value for the "Generator load Name" column.
        CrankingTime (float, optional): Default value for the "Generator Cranking Time" column.
        RampRate (float, optional): Default value for the "Generator Ramp Rate" column.
        BSPSSEPyGeneratorType (str, optional): Default value for the "BSPSSEPy Generator Type" column.
        CrankingLoadArray (list, optional): Default value for the "Generator Cranking load Array" column.

    """
    bp("Extending bspssepy_gen Dataframe...",app=app)
    await asyncio.sleep(app.async_print_delay if app else 0)


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
        if Col not in bspssepy_gen.columns:
            if isinstance(DefaultValue, list):  # For list values, use object dtype
                bspssepy_gen[Col] = pd.Series([DefaultValue] * len(bspssepy_gen), dtype="object")
            else:
                bspssepy_gen[Col] = DefaultValue
            
            if debug_print:
                bp(f"[DEBUG] Added column '{Col}' with default value: {DefaultValue}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)


    for config in ConfigTable:
        GenName = config.get("Generator Name")
        # gen_id = config.get("Generator ID")
        BusName = config.get("Bus Name")

        if debug_print:
            bp(f"[DEBUG] Processing configuration for Generator Name: {GenName}, Bus Name: {BusName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Locate the generator based on GenName or BusName
        GeneratorIndices = None
        if GenName:
            GeneratorIndices = bspssepy_gen[bspssepy_gen["MCNAME"] == GenName].index
            if debug_print:
                bp(f"[DEBUG] Located generator index by Name ({GenName}): {list(GeneratorIndices)}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
        elif BusName:
            GeneratorIndices = bspssepy_gen[bspssepy_gen["NAME"] == BusName].index
            if debug_print:
                bp(f"[DEBUG] Located generator index by Bus Name ({BusName}): {list(GeneratorIndices)}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

        # If no matching generator is found, skip
        if GeneratorIndices is None or GeneratorIndices.empty:
            bp(f"Warning: No matching generator found for '{GenName or BusName}'. Skipping.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            continue

        if debug_print:
            bp(f"[DEBUG] Generator index to update: {list(GeneratorIndices)}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Extract configuration values or use defaults
        BSPSSEPyGenType = config.get("Generator Type", BSPSSEPyGenType)
        BSPSSEPyStatus = 3 if BSPSSEPyGenType == "BS" else config.get("Status", BSPSSEPyStatus)
        GenLoadName = config.get("load Name", GenLoadName)
        GenCrankingTime = config.get("Cranking Time", GenCrankingTime)
        GenRampRate = config.get("Ramp Rate", GenRampRate)
        GenCrankingLoadPowerArray = config.get("Cranking load Array", GenCrankingLoadPowerArray)
        AGCAlpha = config.get("AGC Participation Factor", AGCAlpha)
        LoadDampConstant = config.get("load Damping Constant", LoadDampConstant)
        EffectiveSpeedDroop = config.get("Effective Speed Droop", EffectiveSpeedDroop)
        BiasScaling = config.get("Bias Scaling", BiasScaling)
        POPF = config.get("POPF", POPF)
        QOPF = config.get("QOPF", QOPF)
        UseGenRampRate = config.get("UseGenRampRate", False)
        LoadEnabledResponse = config.get("load Enabled Response", False)
        LERPF = config.get("LERPF", -1)


        # if debug_print:
            # bp(f"[DEBUG] Calling GetGeneratorInfoFun with string = 'Active Power Output (Pgen) MW'",app=app)
            # await asyncio.sleep(app.async_print_delay if app else 0)
        # Gref = GetGeneratorInfoFun("Active Power Output (Pgen) MW", GenName = GenName, debug_print=debug_print)
        
        # Gref = 0
            
        # Vref = GetGeneratorInfoFun("PU", GenName = GenName, debug_print=debug_print)
        # Vref = 0
        # if debug_print:
            # bp(f"[DEBUG] Gref = {Gref}, Vref = {Vref}",app=app)
            # await asyncio.sleep(app.async_print_delay if app else 0)
        

        if debug_print:
            bp(f"[DEBUG] Extracted config Values for '{GenName}':",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Status: {BSPSSEPyStatus} (0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active)",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        load Name: {GenLoadName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Cranking Time: {GenCrankingTime}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Ramp Rate: {GenRampRate}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Generator Type: {BSPSSEPyGenType}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Cranking load Array: {GenCrankingLoadPowerArray}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        AGC Participation Factor: {AGCAlpha}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        load Damping Constant: {LoadDampConstant}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Effective Speed Droop: {EffectiveSpeedDroop}")
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Bias Scaling: {BiasScaling}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Effective Bias: {BiasScaling *(1/EffectiveSpeedDroop + LoadDampConstant)}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        
        
        # # Perform PSSE load Flow Analysis to get Gref and Vref
        # bus_num = config.get("Bus Number")
        # # Fetch Gref and Vref using PSSE APIs
        # bus_num = config.get("Bus Number")
        # try:
        #     Gref = generator(bus_num)
        #     Vref = pssdynmdl.get_vref(bus_num)
        # except Exception as e:
        #     bp(f"Error fetching dynamic simulation data for Generator '{GenName}': {e}")
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
        #     "Generator load Name": LOADNAME,
        #     "Generator Cranking Time": CrankingTime,
        #     "Generator Ramp Rate": RampRate,
        #     "BSPSSEPy Generator Type": BSPSSEPyGeneratorType,
        #     "Generator Cranking load Array": CrankingLoadArray,
        #     "AGC Participation Factor": AGCAlpha,
        #     "load Damping Constant": D,  # D
        #     "Effective Speed Droop": R,  # R
        #     "Bias Scaling": BScaling,  # Bias Scaling (Effective Bias = Bias * Bias Scaling)
        #     "Effective Bias": BScaling *(1/R + D)
        # }
        
        # Update the generator(s) in the DataFrame
        for Col, Value in Updates.items():
            if debug_print:
                bp(f"[DEBUG] Updating column '{Col}' with value: {Value}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            
            if Col == "GenCrankingLoadPowerArray":  # Special handling for lists
                for idx in GeneratorIndices:  # Assign each list individually
                    bspssepy_gen.at[idx, Col] = Value
                    if debug_print:
                        bp(f"[DEBUG] Updated '{Col}' at index {idx} with list value: {Value}",app=app)
                        await asyncio.sleep(app.async_print_delay if app else 0)
            else:
                bspssepy_gen.loc[GeneratorIndices, Col] = Value
                if debug_print:
                    bp(f"[DEBUG] Updated '{Col}' for generator(s) at indices {list(GeneratorIndices)} with value: {Value}",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)

    # bspssepy_gen["BSPSSEPyStatus"] = bspssepy_gen["STATUS"].apply(
    #         lambda x: "In-Service" if x == 1 else "Offline"
    #     )

    bspssepy_gen["BSPSSEPyStatus_0"] = bspssepy_gen["BSPSSEPyStatus"] # Initial Status

    bspssepy_gen["BSPSSEPyLastAction"] = "Initialized"
    bspssepy_gen["BSPSSEPyLastActionTime"] = 0.0
    bspssepy_gen["BSPSSEPySimulationNotes"] = "Initialized"  
    bspssepy_gen["GREFChannel"] = -1      # --> corresponding to GREF in machine_array_channel (check the API - status(2) = 14)
    bspssepy_gen["VREFChannel"] = -1      # --> corresponding to VREF in machine_array_channel (check the API - status(2) = 11)
    bspssepy_gen["PELECChannel"] = -1         # --> corresponding to PELEC in machine_array_channel (check the API - status(2) = 2)
    bspssepy_gen["QELECChannel"] = -1         # --> corresponding to QELEC in machine_array_channel (check the API - status(2) = 3)
    bspssepy_gen["PMECHChannel"] = -1        # --> corresponding to PMECH in machine_array_channel (check the API - status(2) = 6)
    bspssepy_gen["FChannel"] = -1        # --> This is the frequency channel for the generator (will be fetched from config.Channels)

    
    # Informaiton about the main connection element that connect the generator to the grid. This is required for "simulating the non-black-start generators connection back to the grid". The idea is to enable "load cranking" for some time, and then when we would like to connect the generator, we disconnect the load, close the branch/transformer and then control the output power of the generator until ramp-up phase is complete.
    bspssepy_gen["ConnectionType"] = None
    bspssepy_gen["ConnectionElementFromBus"] = None
    bspssepy_gen["ConnectionElementToBus"] = None
    bspssepy_gen["ConnectionElementID"] = None
    bspssepy_gen["ConnectionElementName"] = None

    

    bp("Adding 'GREF', 'VREF', 'PELEC', 'QELEC', 'PMECH' channels to all generators + custom loads for non-black-start generators.",app=app)
    await asyncio.sleep(app.async_print_delay if app else 0)
    bp("Also adding informaiton about generator connection elements to bspssepy_gen",app=app)
    await asyncio.sleep(app.async_print_delay if app else 0)
    # Loop through generators and process them based on their type
    for GeneratorRowIndex, gen_row in bspssepy_gen.iterrows():
        GeneratorType = gen_row.get("BSPSSEPyGenType", "")
        GenName = gen_row['MCNAME']

        # Call the GetGeneratorConnectionPoint function
        ConnectionPoint = await GetGeneratorConnectionPoint(
            t = 0,
            bspssepy_gen=bspssepy_gen,
            bspssepy_bus=bspssepy_bus,
            GenName=GenName,
            bspssepy_trn=bspssepy_trn,
            bspssepy_brn=bspssepy_brn,
            debug_print=debug_print,
            app=app
        )

        # Add the connection point details to the Updates dictionary if found
        if not(ConnectionPoint):
            bp(f"[ERROR] Could not find a connection point for generator {GenName}.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                raise Exception("Error in ExtendBSPSSEPyGenDataFrame Function!")
            else:
                SystemExit(1)
        
        # Define the mapping between bspssepy_gen columns and ConnectionPoint keys
        keys = ["ConnectionType",
                "ConnectionElementFromBus",
                "ConnectionElementToBus",
                "ConnectionElementID",
                "ConnectionElementName"
                ]
        
       

        # Use a list comprehension to extract values from ConnectionPoint
        gen_row[keys] = [ConnectionPoint[key] for key in keys]
        bspssepy_gen.loc[GeneratorRowIndex, keys] = [ConnectionPoint[key] for key in keys]


        # Map the desired keys in gen_row to the corresponding keys in ConnectionPoint
        # bspssepy_gen.loc[GeneratorRowIndex,
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

        # bp(GenName)
        # bp("HI")
        for key in bspssepy_gen_ch_mapping.keys():
            ierr = psspy.machine_array_channel(
                [-1,        # Next available channel
                bspssepy_gen_ch_mapping[key],       # status(2) --> quantity to monitor
                int(gen_row["NUMBER"]),  # Bus number corresponding to machine location
                ],
                gen_row["ID"],       # ID of the machine
                key + gen_row["MCNAME"],      # Channel Identifier
                )
            
            if ierr != 0:
                bp(f"[ERROR] Error occured during adding channel for Gen: {gen_row['MCNAME']} to monitor {key} with key_status number: {bspssepy_gen_ch_mapping[key]}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            else:
                bspssepy_gen.at[GeneratorRowIndex,key+'Channel'] = SimConfig.CurrentChannelIndex
                if debug_print:
                    bp(f"[DEBUG] Successfully added channel for Gen: {gen_row['MCNAME']} to monitor {key} with channel index {SimConfig.CurrentChannelIndex}",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                SimConfig.CurrentChannelIndex += 1 # Increament Channel index

        # Check if generator is a black-start generator
        if GeneratorType.lower() in ["blackstart", "black-start", "black start", "bs"]:
            bp(f"Skipping black-start generator: {GenName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            continue
        
        
        bus_num = gen_row['NUMBER']
        BusName = gen_row['NAME']
        
        LoadBusNumber = gen_row["ConnectionElementFromBus"] if (bus_num == gen_row["ConnectionElementToBus"]) else gen_row["ConnectionElementToBus"]
        from .bspssepy_bus_funs import get_bus_info
        LoadBusName = await get_bus_info("NAME", Bus = LoadBusNumber, debug_print=debug_print,app=app)

        LOADNAME = gen_row['GenLoadName']
        if LOADNAME == "" or LOADNAME is None:
            LOADNAME = f"CL{GenName}"
        
        bp(f"Adding custom load for Genrator: {GenName} at bus {LoadBusName}(#{LoadBusNumber}), with loadname {LOADNAME}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

        # Prepare power array for the new load
        CrankingLoadArray = gen_row.get("GenCrankingLoadPowerArray","")
        # [
        #     gen_row.get("Active Power Output (Pgen) MW", None),
        #     gen_row.get("Reactive Power Output (Qgen) MVar", None),
        #     None,  # IP: Constant current active load
        #     None,  # IQ: Constant current reactive load
        #     None,  # YP: Constant admittance active load
        #     None,  # YQ: Constant admittance reactive load
        #     None   # Power Factor
        # ]

        # Add a custom load at the generator's bus location
        # bp(f"Adding custom load for non-black-start generator: {GenName}")
        bspssepy_load, ierr = await NewLoad(
            LOADNAME=LOADNAME,
            bspssepy_load=bspssepy_load,
            BusName=LoadBusName,
            bus_num=LoadBusNumber,
            ElementName=GenName,
            ElementType="Gen",
            PowerArray=CrankingLoadArray,
            t = 0,
            debug_print=debug_print,
            app=app,
        )
    bp("DataFrame successfully updated with new generator phases and states.",app=app)
    await asyncio.sleep(app.async_print_delay if app else 0)





    return bspssepy_gen, bspssepy_load


async def GetGeneratorConnectionPoint(t, bspssepy_gen, GenName, bspssepy_bus, bspssepy_trn, bspssepy_brn, debug_print=False, app=None):
    """
    Identifies the main connection point (transformer or branch) of a generator to the grid.
    
    Parameters:
        bspssepy_gen (pd.DataFrame): DataFrame containing generator information.
        GenName (str): Name of the generator for which the connection point is to be identified.
        bspssepy_trn (pd.DataFrame): DataFrame containing transformer information.
        bspssepy_brn (pd.DataFrame): DataFrame containing branch information.
        debug_print (bool, optional): If True, enables detailed debug output. Defaults to False.
    
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

    if debug_print:
        bp(f"[DEBUG] Running GetGeneratorConnectionPoint for {GenName}.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Get generator information
    try:
        GenRow = bspssepy_gen.loc[bspssepy_gen["MCNAME"] == GenName].iloc[0]
    except IndexError:
        bp(f"[ERROR] Generator {GenName} not found in bspssepy_gen.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    GenBus = GenRow["NAME"]

    # Setting GenBus as swing for all Gens
    from .bspssepy_bus_funs import ChangeBusType
    # ierr = ChangeBusType(t = t, NewBusType=3, bspssepy_bus=bspssepy_bus, Bus=GenBus, debug_print=debug_print)


    # Identify the main connection device (transformer or branch)
    TransformerRow = bspssepy_trn[
        (bspssepy_trn["FROMNAME"] == GenBus) | (bspssepy_trn["TONAME"] == GenBus)
    ]
    BranchRow = bspssepy_brn[
        (bspssepy_brn["FROMNAME"] == GenBus) | (bspssepy_brn["TONAME"] == GenBus)
    ]

    # Check if a transformer is connected
    if not TransformerRow.empty:
        MainConnectionType = device_type_mapping['t']
        MainConnectionRow = TransformerRow.iloc[0]
        DeviceName = MainConnectionRow["XFRNAME"]
        if GenRow["BSPSSEPyGenType"] != "BS":
            bspssepy_trn.loc[bspssepy_trn.index == MainConnectionRow.name, "GenControlled"] = True
    elif not BranchRow.empty:
        MainConnectionType = device_type_mapping['branch']
        MainConnectionRow = BranchRow.iloc[0]
        DeviceName = MainConnectionRow["BRANCHNAME"]
        if GenRow["BSPSSEPyGenType"] != "BS":
            bspssepy_brn.loc[bspssepy_brn.index == MainConnectionRow.name, "GenControlled"] = True
    else:
        bp(f"[ERROR] No connection device found for generator {GenName} at Bus {GenBus}.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Extract connection details
    FromBus = MainConnectionRow["FROMNUMBER"]
    ToBus = MainConnectionRow["TONUMBER"]
    DeviceID = MainConnectionRow["ID"]

    if debug_print:
        bp(f"[DEBUG] Connection Point for {GenName}: {MainConnectionType} from Bus {FromBus} to Bus {ToBus}.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    return {
        "ConnectionType": MainConnectionType,
        "ConnectionElementFromBus": FromBus,
        "ConnectionElementToBus": ToBus,
        "ConnectionElementID": DeviceID,
        "ConnectionElementName": DeviceName,
        "Row": MainConnectionRow,
    }




async def GenEnable(
        bspssepy_gen,
        t,
        action,
        GenName,
        bspssepy_trn,
        bspssepy_brn,
        bspssepy_load,
        bspssepy_bus,
        bspssepy_agc,
        config,
        debug_print = False,
        app=None,
        ):
    """
    This function will go through the process of enabling a generator.
    The function will require the following information as input:

    Parameters:
        GenName: Generator name of interest
        bspssepy_gen: The dataframe containing generator data.
        t: The current simulation time
        action: The action dictionary entry that has all required information about the generator and its latest status. This action element needs to be updated to keep track of the progress of the action requested, to tell the main program when the action is completed.
        debug_print (bool, optional): Enable detauled debug output. Defaults to False.
    Returns:
        UpdatedActionStatus: The updated Action Status of the generator.
    """

    if debug_print:
        bp(f"[DEBUG] Running GenEnable function for action: {action}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    # get Gen row from bspssepy_gen
    BSPSSEPyGenRow = bspssepy_gen.loc[bspssepy_gen["MCNAME"] == action['ElementIDValue']].copy()



    from .bspssepy_default_vars import bspssepy_default_vars_fun
    default_int, default_real, default_char = bspssepy_default_vars_fun()


    # To turn on this generator, we need to check at which phase it is currently!
    # 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active
    # Check if the generator is off --> To enter cranking phase
    if BSPSSEPyGenRow['BSPSSEPyStatus'].values[0] == 0:
        # So the generator is off, let's prepare it to "crank".
        
        
        #▂▃▄▅▆▇█▓▒░ Cranking (0 → 1) ░▒▓█▇▆▅▄▃▂

        
        # First check that there is an energized line or transformer at the generator bus!
        GenBusName = BSPSSEPyGenRow['NAME'].values[0]
        if debug_print:
            bp(f"[DEBUG] Checking if the generator is energized correctly by examining bus:{GenBusName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        if (
                any(
                    brn["BSPSSEPyStatus"] == "Closed"
                    for _, brn in bspssepy_brn[
                        (bspssepy_brn["FROMNAME"] == GenBusName) | (bspssepy_brn["TONAME"] == GenBusName)
                    ].iterrows()
                )
                or any(
                    trn["BSPSSEPyStatus"] == "Closed"
                    for _, trn in bspssepy_trn[
                        (bspssepy_trn["FROMNAME"] == GenBusName) | (bspssepy_trn["TONAME"] == GenBusName)
                    ].iterrows()
                )
            ):
            bp(f"[ERROR] Cannot Enter Cranking phase as GenBusName: {GenBusName} is energized. With this, the generator is already connected! Check the recovery plan to energize the 'far' bus first and crank the Genload before energizing the transformer/line connected to the generator! The program will exit.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

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
        
        if debug_print:
            bp(f"[DEBUG] Generator is about to crank. Attempting to enable the associated load: {GenLoadName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        from .bspssepy_load_funs import LoadEnable, LoadDisable
        # Enable GenLoad to start cranking and set the generator output power to zero
        ierr = await LoadEnable(t = t, bspssepy_load=bspssepy_load, LOADNAME=GenLoadName, debug_print=debug_print,app=app, bspssepy_agc=bspssepy_agc, bspssepy_gen=bspssepy_gen)

        if ierr != 0:
            bp(f"[ERROR] Could not enable GenLoad:{GenLoadName}. Generator did not start the cranking phase.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            UpdatedActionStatus = 0
            return UpdatedActionStatus
        
        if debug_print:
            bp(f"[DEBUG] GenLoad:{GenLoadName} was enabled successfully. Recording Cranking Start Time in bspssepy_gen dataframe",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)


        BSPSSEPyGenRow['BSPSSEPyStatus'] = 1    # 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active
        BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'Crank'
        BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
        BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Successfully entered cranking phase at t = {t}'

        # Write the row back to the DataFrame
        bspssepy_gen.loc[bspssepy_gen["MCNAME"] == GenName, :] = BSPSSEPyGenRow

        bp(f"Generator '{GenName}' started cranking phase.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

        UpdatedActionStatus = 1     # 0: Not started, 1: In progress, 2: Completed
        return UpdatedActionStatus
    

    # Check if the generator is Cranking --> To enter Ramp-up phase
    elif BSPSSEPyGenRow['BSPSSEPyStatus'].values[0] == 1:
        
        #▂▃▄▅▆▇█▓▒░ Ramp-up (1 → 2) ░▒▓█▇▆▅▄▃▂
        # So the generator is cranking. Check if cranking should stop and start ramping up the generator.
        
        
        # Check if Cranking time is met!
        if t < BSPSSEPyGenRow["GenCrankingTime"].values[0]*60 + BSPSSEPyGenRow["BSPSSEPyLastActionTime"].values[0]:
            if debug_print:
                bp(f"[DEBUG] Gen {GenName} is still cranking. (Cranking ends at t = {BSPSSEPyGenRow['GenCrankingTime'].values[0]*60 + BSPSSEPyGenRow['BSPSSEPyLastActionTime'].values[0]} - remaining {BSPSSEPyGenRow['GenCrankingTime'].values[0]*60 + BSPSSEPyGenRow['BSPSSEPyLastActionTime'].values[0] - t}s)",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            UpdatedActionStatus = 1
            return UpdatedActionStatus
        else:
            bp(f"Generator: '{GenName}' cranking time met. Disabling the associated load. ",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            

            # Cranking finished! Let's disable the GenLoad
            GenLoadName = BSPSSEPyGenRow['GenLoadName'].values[0]
        
            if debug_print:
                bp(f"[DEBUG] Attempting to disable the associated load: {GenLoadName}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)


            from .bspssepy_load_funs import LoadDisable
            
            # Enable GenLoad to start cranking and set the generator output power to zero
            ierr = await LoadDisable(t = t, bspssepy_load=bspssepy_load, LOADNAME=GenLoadName, debug_print=debug_print,app=app)

            
            if ierr != 0:
                bp(f"[ERROR] Could not disable GenLoad:{GenLoadName}. Generator did not stop the cranking phase.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                UpdatedActionStatus = 1
                return UpdatedActionStatus
            
            if debug_print:
                bp(f"[DEBUG] GenLoad:{GenLoadName} was disabled successfully. Energizing the connection element (TRN or BRN) to start the Ramp-up phase.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            

            ElementName = BSPSSEPyGenRow["ConnectionElementName"].values[0]

            if BSPSSEPyGenRow["ConnectionType"].values[0] == "TRN":
                from .bspssepy_trn_funs import TrnClose
                ierr = await TrnClose(t = t,TrnName=ElementName, bspssepy_trn=bspssepy_trn,bspssepy_bus=bspssepy_bus, CalledByGen=True, debug_print=debug_print, app=app)

                if ierr == 0:
                    if debug_print:
                        bp(f"[DEBUG] generator is connected successfully. Controlling the generator output power.",app=app)
                        await asyncio.sleep(app.async_print_delay if app else 0)
                else:
                    bp("[ERROR] Encountered error during GenEnabled -- TrnClose function! Program will exit",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    if app:
                        raise Exception("Error in GenEnable Function --> Could not start ramp-up phase!")
                    else:
                        SystemExit(1)
                
            elif BSPSSEPyGenRow["ConnectionType"].values[0] == "BRN":
                from .bspssepy_brn_funs import BrnClose
                ierr = await BrnClose(t = t, BranchName=ElementName, bspssepy_brn=bspssepy_brn,bspssepy_bus=bspssepy_bus, CalledByGen=True, debug_print=debug_print, app=app)

                if ierr == 0:
                    if debug_print:
                        bp(f"[DEBUG] generator is connected successfully. Controlling the generator output power.",app=app)
                        await asyncio.sleep(app.async_print_delay if app else 0)
                else:
                    bp("[ERROR] Encountered error during GenEnabled -- BrnClose function! Program will exit",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    if app:
                        raise Exception("Error in GenEnable Function --> Could not start ramp-up phase!")
                    else:
                        SystemExit(1)
            
            else:
                bp("[ERROR] Unkown element. Could not enable/connect the generator. Program will exit",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(1)


            # GenG = await FetchChannelValue(int(BSPSSEPyGenRow["GREFChannel"].values[0]), debug_print=debug_print,app=app)
            GenV = await FetchChannelValue(int(BSPSSEPyGenRow["VREFChannel"].values[0]), debug_print=debug_print,app=app)
            # GenP = await FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), debug_print=debug_print,app=app)
            # GenQ = await FetchChannelValue(int(BSPSSEPyGenRow["QELECChannel"].values[0]), debug_print=debug_print,app=app)
            # GenPm = await FetchChannelValue(int(BSPSSEPyGenRow["PMECHChannel"].values[0]), debug_print=debug_print,app=app)
            # bp(f"GenG: {GenG}, GenV: {GenV}, GenP: {GenP}, GenQ: {GenQ}, GenPm: {GenPm}",app=app)
            # await asyncio.sleep(app.async_print_delay if app else 0)
            

            GenBusNum = BSPSSEPyGenRow["NUMBER"].values[0]
            GenID = BSPSSEPyGenRow["ID"].values[0]

            # Get the base MVA of the generator
            ierr, gen_mva_base = psspy.macdat(GenBusNum, GenID, 'MBASE')

            # Set the generator output real power to zero
            ierr = psspy.change_gref(GenBusNum, GenID, 0/gen_mva_base)

            if ierr != 0:
                bp(f"[ERROR] Error occured when setting generator: {GenName} output real power to zero. System will exit.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable Function!")
                else:
                    SystemExit(0)

            if debug_print:
                bp(f"[DEBUG] Successfully set generator: {GenName} output real power to zero.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            # Set the generator output reactive power to zero (we set Vref to Vref channel value -- no change in Q of teh generator is needed then)
            ierr = psspy.change_vref(GenBusNum, GenID, GenV)
            if ierr != 0:
                bp(f"[ERROR] Error occured when setting generator: {GenName} output reactive power to zero. System will exit.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)

            if debug_print:
                bp(f"[DEBUG] Successfully set generator: {GenName} output reactive power to zero.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            

            
            BSPSSEPyGenRow['BSPSSEPyStatus'] = 2
            BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'Ramp-Up'
            BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
            BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Successfully entered Ramping-up phase at t = {t}'

            # Write the row back to the DataFrame
            bspssepy_gen.loc[bspssepy_gen["MCNAME"] == GenName, :] = BSPSSEPyGenRow


            bp(f"Generator '{GenName}' started Ramping-Up phase.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

            UpdatedActionStatus = 1
            return UpdatedActionStatus

            











            
            
    
    elif BSPSSEPyGenRow['BSPSSEPyStatus'].values[0] == 2:
        
        #▂▃▄▅▆▇█▓▒░ In-service (2 → 3) ░▒▓█▇▆▅▄▃▂
        # So the generator is Ramping-Up. Check if ramping-up should stop and start In-Service Phase of the generator.

        # The goal is to ramp up the generator to the POPF value for now.
        # When the generator is at around that value, the ramp-up phase will be considered complete.


        # Check if the generator is supposed to use the explicit ramp-rate defiend in bspssepy_gen or this will be embedded in the generator model (i.e. IEEEG1 model for example has its own ramp-rate model inside it)
        GenBusNum = BSPSSEPyGenRow["NUMBER"].values[0]
        GenID = BSPSSEPyGenRow["ID"].values[0]
        ierr, gen_mva_base = psspy.macdat(GenBusNum, GenID, 'MBASE')
        GenPOPF = BSPSSEPyGenRow["POPF"].values[0]
        GenPOPFpu = GenPOPF/gen_mva_base
        # Check if the generator is at the target power level
        GenP = await FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), debug_print=debug_print, app=app) * gen_mva_base

        
        if GenPOPF == 0:
            # Ramp-up is provided by the plan - exit the ramp-up phase!
            bp(f"Generator: '{GenName}' ramp-up phase is skipped (provided by the plan). Setting the generator to In-service phase.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        
            BSPSSEPyGenRow['BSPSSEPyStatus'] = 3
            BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'In-service'
            BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
            BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Successfully entered In-service phase at t = {t}'

            # Write the row back to the DataFrame
            bspssepy_gen.loc[bspssepy_gen["MCNAME"] == GenName, :] = BSPSSEPyGenRow

            bp(f"Generator '{GenName}' started In-service phase.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            UpdatedActionStatus = 2
            return UpdatedActionStatus

        UseGenRampRate = BSPSSEPyGenRow["UseGenRampRate"].values[0]
        if UseGenRampRate: # will use the explicit ramp-rate defined in bspssepy_gen
            if debug_print:
                bp(f"[DEBUG] Using explicit ramp-rate for generator: {GenName} - Ramp Rate: {BSPSSEPyGenRow['GenRampRate'].values[0]} MW/min",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            GenRampRateSec = BSPSSEPyGenRow["GenRampRate"].values[0]/60         # convert the ramp rate to MW/sec

            if GenP > GenPOPF:
                GenRampRateSec = -GenRampRateSec
            
            
            # we use psspy.increment_gref function to increase/adjust generator output power gradually.
            ierr = psspy.increment_gref(GenBusNum, GenID, GenRampRateSec/gen_mva_base)  # Apply increment


            if ierr != 0:
                bp(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)


            
            # bp(f"t ={t}, GenP = {GenP}\t\tGenPOPF = {GenPOPF}\t\tGenRampRateSec = {GenRampRateSec}\t\te={100*(GenPOPF - GenP)/GenPOPF}%")
            
            # GenRampRate = BSPSSEPyGenRow["GenRampRate"].values[0]
            # # we use psspy.increment_gref function to increase/adjust generator output power gradually.
            # ierr = psspy.increment_gref(GenBusNum, GenID, GenRampRateSec/gen_mva_base)  # Apply increment

            # if ierr != 0:
            #     bp(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}")
            #     if app:
                #     raise Exception("Error in GenEnable function!")
                # else:
                #     SystemExit(0)

        else: # will use the generator model ramp-rate (we simply provide the target output power, and the generator model will take care of the ramp-rate)
            if debug_print:
                bp(f"[DEBUG] Using generator model ramp-rate for generator: {GenName} - Target Power: {GenPOPF} MW",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            # we use psspy.increment_gref function to increase/adjust generator output power gradually.
            ierr = psspy.increment_gref(GenBusNum, GenID, GenPOPFpu)  # Apply the target output power
            if ierr != 0:
                bp(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)
            UpdatedActionStatus = 2
            return UpdatedActionStatus
        
        # # Check if the generator is at the target power level
        # GenP = FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), debug_print=debug_print) * gen_mva_base

        if debug_print:
            bp(f"[DEBUG] Generator: {GenName} - Current Power: {GenP}, Target Power: {GenPOPF} MW",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        
        # If generator output power is within 1% of the target power, we consider the ramp-up phase to be complete, and we provide the generator with the reference value for Gref
        if (abs(GenPOPF - GenP)/GenPOPF <= 0.01):
            if UseGenRampRate:
                if (abs(GenPOPF - GenP) > GenRampRateSec):
                    if debug_print:
                        bp(f"[DEBUG] Generator: {GenName} is still ramping up. (Current Power: {GenP}, Target Power: {GenPOPF} MW)",app=app)
                        await asyncio.sleep(app.async_print_delay if app else 0)
                    UpdatedActionStatus = 1
                    return UpdatedActionStatus

            # Set the generator output real power to zero
            ierr = psspy.change_gref(GenBusNum, GenID, GenPOPFpu)

            if ierr != 0:
                bp(f"[ERROR] Error occured when setting generator: {GenName} output real power to GenPOPF: {GenPOPF}.System will exit.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)

            if debug_print:
                bp(f"[DEBUG] Successfully set generator: {GenName} output real power to GenPOPF: {GenPOPF}.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            
            bp(f"Generator: '{GenName}' ramp-up phase completed. Setting the generator to In-service phase.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        
            BSPSSEPyGenRow['BSPSSEPyStatus'] = 3
            BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'In-service'
            BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
            BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Successfully entered In-service phase at t = {t}'

            # Write the row back to the DataFrame
            bspssepy_gen.loc[bspssepy_gen["MCNAME"] == GenName, :] = BSPSSEPyGenRow

            bp(f"Generator '{GenName}' started In-service phase.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            UpdatedActionStatus = 2
            return UpdatedActionStatus
        
        else:    
            if debug_print:
                bp(f"[DEBUG] Generator: {GenName} is still ramping up. (Current Power: {GenP}, Target Power: {GenPOPF} MW)",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            
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


async def GenDisable(t, GenName, bspssepy_gen,bspssepy_bus, bspssepy_trn, bspssepy_brn, debug_print=False, app=None):
    """
    This function disables a generator based on its "name" only. The way it works is that it will check the Connection Point Element (TRN, BRN) and ensure that it is disabled.
    
    
    For a group of generators, we better make a new function that handle bus location and fetches all machines at that location for disabling them one by one.

    Arguments:
        t: float
            Current simulation time.
        GenName: str or int
            The unique name of the generator.
        bspssepy_gen: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy generators data.
        bspssepy_trn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy Two-winding transformers data.
        bspssepy_brn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy branch data.
        debug_print: bool
            Enable detailed debug output (default = False).

    Returns:
        int:
            0: The generator is successfully disabled
            Otherwise: an error occured.
    """

    # Initial debug message

    if debug_print:
        bp(f"[DEBUG] GenDisable called with inputs:\n"
              f"  t = {t}"
              f"  GenName: {GenName}"
            #   f"  bspssepy_gen: {bspssepy_gen}"
              ,app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    # Fetch Generator details
    GenRow = await GetGenInfo(["NAME", "MCNAME", "ID", "NUMBER", "STATUS", "ConnectionType", "ConnectionElementName", "BSPSSEPyStatus"], GenName=GenName, bspssepy_gen=bspssepy_gen, debug_print=debug_print,app=app)

   
    if GenRow is None or len(GenRow) == 0:
        bp(f"[ERROR] Generator not found for GenName = {GenName}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    
    GenBusName = GenRow["NAME"].values[0]
    GenID = GenRow["ID"].values[0]
    GenBusNum = GenRow["NUMBER"].values[0]
    GenStatus = GenRow["STATUS"].values[0]
    GenBSPSSEPyStatus = GenRow["BSPSSEPyStatus"].values[0]
    GenConType = GenRow["ConnectionType"].values[0]
    GenConElementName = GenRow["ConnectionElementName"].values[0]
    

    if debug_print:
        bp(f"[DEBUG] Determining the connection point element (TRN or BRN) for Gen {GenName}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    if GenConType == "TRN":
        bp(f"Checking the status of the transformer connecting {GenName} to the grid:{GenConType} - {GenConElementName}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        from .bspssepy_trn_funs import GetTrnInfo, TrnTrip
        ElementStatus = await GetTrnInfo("STATUS", TrnName=GenConElementName, debug_print=debug_print,app=app)
        if ElementStatus != 0:
            if debug_print:
                bp(f"[DEBUG] The two-winding transformer: {GenConElementName} status is {ElementStatus}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            bp(f"Tripping the transformer connecting {GenName} --> {GenConType} - {GenConElementName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

            await TrnTrip(t=t, bspssepy_trn=bspssepy_trn,TrnName=GenConElementName, debug_print=debug_print,app=app)
            
            if debug_print:
                bp(f"[DEBUG] Successfully tripped two-winding transformer: {GenConElementName}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
        else:
            bp(f"The transformer connecting the generator is tripped already ({GenName} --> {GenConType} - {GenConElementName})",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)


    elif GenRow["ConnectionType"].values[0] == "BRN":
        bp(f"Checking the status of the branch connecting {GenName} to the grid:{GenConType} - {GenConElementName}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        from .bspssepy_brn_funs import get_brn_info, BrnTrip
        ElementStatus = await get_brn_info("STATUS", BranchName=GenConElementName, debug_print=debug_print,app=app)
        if ElementStatus != 0:
            if debug_print:
                bp(f"[DEBUG] The branch: {GenConElementName} status is {ElementStatus}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            bp(f"Tripping the branch connecting {GenName} --> {GenConType} - {GenConElementName}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

            await BrnTrip(t=t, bspssepy_brn=bspssepy_brn, BranchName=GenConElementName, debug_print=debug_print,app=app)
            
            if debug_print:
                bp(f"[DEBUG] Successfully tripped Branch: {GenConElementName}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
        else:
            bp(f"The branch connecting the generator is tripped already ({GenName} --> {GenConType} - {GenConElementName})",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
    else:
        bp(f"[ERROR] Could not identify how the generator is connected to the grid. program will exit!",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        if app:
            raise Exception("Error in GenDisable function!")
        else:
            SystemExit(1)
        


    from .bspssepy_default_vars import bspssepy_default_vars_fun
    default_int, default_real, default_char = bspssepy_default_vars_fun()
        
    # Check if the generator status is 1 --> then disable it!
    # if GenBSPSSEPyStatus == 0:
    #     bp(f"[INFO] Generator '{GenName} at Bus '{GenBusNum}' is already disabled.")
    #     return 0
    
    from .bspssepy_bus_funs import ChangeBusType

    ierr = await ChangeBusType(t = t, NewBusType=3, bspssepy_bus=bspssepy_bus, Bus=GenBusName, debug_print=debug_print,app=app)
    if ierr != 0:
        bp(f"[ERROR] Could not set the bus of Gen {GenName} (Bus {GenBusName}) to type 3 (swing), program will exit.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        if app:
            raise Exception("Error in GenEnable function!")
        else:
            SystemExit(1)
        
    # Updating bspssepy_gen to reflect that the generator is not connected
    if not(bspssepy_gen is None or bspssepy_gen.empty):
        GenUpdatedStatus = await GetGenInfo("STATUS", GenName=GenName, debug_print=debug_print,app=app)

        # Update the bspssepy_gen DataFrame
        bspssepy_gen.loc[
            (bspssepy_gen["MCNAME"].apply(str) == str(GenName)) &
            (bspssepy_gen["ID"].apply(str) == str(GenID)) &
            (bspssepy_gen["NUMBER"].apply(str) == str(GenBusNum)),
                ["BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "STATUS"]] = [0, "Disable", t, "Generator Successfully Disabled.", GenUpdatedStatus]
        

async def GenUpdate(
        bspssepy_gen,
        t,
        action,
        GenName,
        bspssepy_trn,
        bspssepy_brn,
        bspssepy_load,
        bspssepy_bus,
        bspssepy_agc,
        config,
        debug_print = False,
        app=None,
        ):
    """
    This function will go through the process of enabling a generator.
    The function will require the following information as input:

    Parameters:
        GenName: Generator name of interest
        bspssepy_gen: The dataframe containing generator data.
        t: The current simulation time
        action: The action dictionary entry that has all required information about the generator and its latest status. This action element needs to be updated to keep track of the progress of the action requested, to tell the main program when the action is completed.
        debug_print (bool, optional): Enable detauled debug output. Defaults to False.
    Returns:
        UpdatedActionStatus: The updated Action Status of the generator.
    """
    
    if debug_print:
        bp(f"[DEBUG] Running GenEnable function for action: {action}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    
    Values: dict = config.bspssepy_sequence.at[action["BSPSSEPySequenceRowIndex"], "Values"]
    # bp(f"Values Type = {type(Values)}"
    #         f"Values Content:\n{Values}")
    # await asyncio.sleep(app.async_print_delay if app else 0)
    
    GenPSetPoint = Values["P"] if "P" in Values else None
    GenQSetPoint = Values["Q"] if "Q" in Values else None
    
    
    # get Gen row from bspssepy_gen
    BSPSSEPyGenRow = bspssepy_gen.loc[bspssepy_gen["MCNAME"] == action['ElementIDValue']].copy()



    from .bspssepy_default_vars import bspssepy_default_vars_fun
    default_int, default_real, default_char = bspssepy_default_vars_fun()

    # Check if the generator is supposed to use the explicit ramp-rate defiend in bspssepy_gen or this will be embedded in the generator model (i.e. IEEEG1 model for example has its own ramp-rate model inside it)
    GenBusNum = BSPSSEPyGenRow["NUMBER"].values[0]
    GenID = BSPSSEPyGenRow["ID"].values[0]
    ierr, gen_mva_base = psspy.macdat(GenBusNum, GenID, 'MBASE')
    # GenTargetPower = BSPSSEPyGenRow["POPF"].values[0]
    GenPSetPointpu = GenPSetPoint/gen_mva_base
    # Check if the generator is at the target power level
    GenP = await FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), debug_print=debug_print, app=app) * gen_mva_base


    UseGenRampRate = BSPSSEPyGenRow["UseGenRampRate"].values[0]
    if UseGenRampRate: # will use the explicit ramp-rate defined in bspssepy_gen
        if debug_print:
            bp(f"[DEBUG] Using explicit ramp-rate for generator: {GenName} - Ramp Rate: {BSPSSEPyGenRow['GenRampRate'].values[0]} MW/min",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        GenRampRateSec = BSPSSEPyGenRow["GenRampRate"].values[0]/60         # convert the ramp rate to MW/sec

        if GenP > GenPSetPoint:
            GenRampRateSec = -GenRampRateSec
        
        
        # we use psspy.increment_gref function to increase/adjust generator output power gradually.
        ierr = psspy.increment_gref(GenBusNum, GenID, GenRampRateSec/gen_mva_base)  # Apply increment


        if ierr != 0:
            bp(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                raise Exception("Error in GenEnable function!")
            else:
                SystemExit(0)

        
        
        # bp(f"t ={t}, GenP = {GenP}\t\tGenPOPF = {GenPOPF}\t\tGenRampRateSec = {GenRampRateSec}\t\te={100*(GenPOPF - GenP)/GenPOPF}%")
        
        # GenRampRate = BSPSSEPyGenRow["GenRampRate"].values[0]
        # # we use psspy.increment_gref function to increase/adjust generator output power gradually.
        # ierr = psspy.increment_gref(GenBusNum, GenID, GenRampRateSec/gen_mva_base)  # Apply increment

        # if ierr != 0:
        #     bp(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}")
        #     if app:
            #     raise Exception("Error in GenEnable function!")
            # else:
            #     SystemExit(0)

    else: # will use the generator model ramp-rate (we simply provide the target output power, and the generator model will take care of the ramp-rate)
        if debug_print:
            bp(f"[DEBUG] Using generator model ramp-rate for generator: {GenName} - Target Power: {GenPSetPoint} MW",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        # we use psspy.increment_gref function to increase/adjust generator output power gradually.
        ierr = psspy.change_gref(GenBusNum, GenID, GenPSetPointpu)  # Apply the target output power
        if ierr != 0:
            bp(f"[ERROR] Updating setpoint for Generator {GenName} (ID = {GenID}) at Bus {GenBusNum}, ierr={ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                raise Exception("Error in GenUpdate function!")
            else:
                SystemExit(0)
        UpdatedActionStatus = 2

    # # Check if the generator is at the target power level
    # GenP = FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), debug_print=debug_print) * gen_mva_base

    if debug_print:
        bp(f"[DEBUG] Generator: {GenName} - Current Power: {GenP}, Target Power: {GenPSetPoint} MW",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
    # If generator output power is within 1% of the target power, we consider the ramp-up phase to be complete, and we provide the generator with the reference value for Gref
    if (abs(GenPSetPoint - GenP)/GenPSetPoint <= 0.01):
        if UseGenRampRate:
            if (abs(GenPSetPoint - GenP) > GenRampRateSec):
                if debug_print:
                    bp(f"[DEBUG] Generator: {GenName} is still ramping up. (Current Power: {GenP}, Target Power: {GenPSetPoint} MW)",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                UpdatedActionStatus = 1
                return UpdatedActionStatus

        # Set the generator output real power to 
        ierr = psspy.change_gref(GenBusNum, GenID, GenPSetPointpu)

        if ierr != 0:
            bp(f"[ERROR] Error occured when setting generator: {GenName} output real power to GenPSetPoint: {GenPSetPoint}.System will exit.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                raise Exception("Error in GenUpdate function!")
            else:
                SystemExit(0)

        if debug_print:
            bp(f"[DEBUG] Successfully set generator: {GenName} output real power to GenPSetPoint: {GenPSetPoint}.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        
        bp(f"Generator: '{GenName}' Set-point updated.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
    
        BSPSSEPyGenRow['BSPSSEPyStatus'] = 3
        BSPSSEPyGenRow['BSPSSEPyLastAction'] = 'Update Set-point'
        BSPSSEPyGenRow['BSPSSEPyLastActionTime'] = t
        BSPSSEPyGenRow['BSPSSEPySimulationNotes'] = f'Updated Set-point to {GenPSetPoint}'

        # Write the row back to the DataFrame
        bspssepy_gen.loc[bspssepy_gen["MCNAME"] == GenName, :] = BSPSSEPyGenRow
        UpdatedActionStatus = 2
    
    # else:    
    #     if debug_print:
    #         bp(f"[DEBUG] Generator: {GenName} is still ramping up. (Current Power: {GenP}, Target Power: {GenPSetPoint} MW)",app=app)
    #         await asyncio.sleep(app.async_print_delay if app else 0)
        
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
