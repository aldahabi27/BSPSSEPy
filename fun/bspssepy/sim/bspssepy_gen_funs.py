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
from fun.bspssepy.config.config import config
from fun.bspssepy.bspssepy_dict import *
from .bspssepy_channels import fetch_channel_value
from fun.bspssepy.app.app_helper_funs import bp
import asyncio


async def get_gen_info(
    gen_keys,  # The key(s) for the required information of the generator(s)
    # Generator Name (optional) --> could be a list
    gen_name=None,
    # Bus name or number where the generator(s) are (optional)
    bus=None,
    # bspssepy_gen DataFrame containing BSPSSEPy extra information associated with the generators (optional)
    bspssepy_gen=None,
    debug_print=False,  # Enable detailed debug output
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
        bp(
            f"[DEBUG] Retrieving generator info for GenKeys: {gen_keys}, GenName: {gen_name}, Bus: {bus}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure BrnKeys is a list
    if isinstance(gen_keys, str):
        gen_keys = [gen_keys]
        # Normalize strings to remove extra spaces
        gen_keys = [key.strip() for key in gen_keys]

    # Ensure GenName is a list
    if gen_name is not None and isinstance(gen_name, str):
        gen_name = [gen_name]
        # Normalize strings to remove extra spaces
        gen_name = [gn.strip() for gn in gen_name]
        if len(gen_name) == 1:
            gen_name = gen_name[0]

    # Normalize strings to remove extra spaces
    if isinstance(bus, str) and bus:
        bus = bus.strip()
        bus_key = "NAME"
    elif bus:
        bus_key = "NUMBER"
    else:
        bus_key = None

    valid_psse_keys = gen_info_dict.keys()
    valid_bspssepy_keys = [] if bspssepy_gen is None else bspssepy_gen.columns

    # Add PSSE Keys needed for basic branch operations
    _gen_keys = ["ID", "MCNAME", "NAME", "NUMBER"]
    _gen_keys_psse = list(_gen_keys)
    for key in gen_keys:
        if key in valid_psse_keys and key not in _gen_keys_psse:
            _gen_keys_psse.append(key)

    if debug_print:
        bp(f"[DEBUG] Fetching PSSE data for keys: {_gen_keys_psse}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure no duplicate columns are fetched from bspssepy_gen if it is provided
    if bspssepy_gen is not None and not bspssepy_gen.empty:
        # Remove overlapping keys from the dataframe search
        valid_bspssepy_keys = [
            key for key in valid_bspssepy_keys if key not in _gen_keys_psse
        ]

    if debug_print:
        bp(
            f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {valid_bspssepy_keys}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Fetch PSSE data for the required keys
    psse_data = {}
    for psse_key in _gen_keys_psse:
        psse_data[psse_key] = await gen_gen_info_psse(
            psse_key, debug_print=debug_print, app=app
        )

    # Combine PSSEData and bspssepy_gen (if proivded) into a single DataFrame
    if bspssepy_gen is not None and not bspssepy_gen.empty:
        valid_bspssepy_gen = bspssepy_gen[valid_bspssepy_keys]
        psse_data = pd.DataFrame(psse_data)
        combined_data = pd.concat([psse_data, valid_bspssepy_gen], axis=1)
    else:
        combined_data = pd.DataFrame(psse_data)

    if debug_print:
        bp(f"[DEBUG] Combined Data:\n{combined_data}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Filter CombinedData based on GenName or Bus

    if gen_name:
        combined_data = combined_data[
            combined_data["MCNAME"].str.strip() == gen_name
        ]
    elif bus_key:
        if bus_key == "NAME":
            combined_data = combined_data[
                combined_data[bus_key].str.strip() == bus
            ]
        else:
            combined_data = combined_data[combined_data[bus_key] == bus]

    if debug_print:
        bp(f"[DEBUG] Filtered Data: \n {combined_data}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Handle cases based on the number of GenKeys
    if len(gen_keys) == 1:
        key = gen_keys[0]
        return (
            combined_data[key].iloc[0]
            if len(combined_data) == 1
            else combined_data[key]
        )
    else:
        return combined_data[gen_keys]


async def gen_gen_info_psse(
    amach_string,  # Requested info string - check available strings in gen_info_dict
    debug_print=False,  # Print debug information
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

    # 1 --> only in service machines at in-service plants (code 2 or 3), 2 --> all machines at in-service plants (type 2 or 3), 3--> in-service machines at all buses (all types including 1 and 4), 4 --> all machines)
    amach_flag = 4

    amach_sid = -1  # treating the whole network as one system

    if debug_print:
        bp(
            f"[DEBUG] Requested generator information for amachstring: '{amach_string}'",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # check if amachstring exists in gen_info_dict
    if amach_string not in gen_info_dict:
        bp(
            f"[ERROR] Invalid amachstring '{amach_string}'. Check gen_info_dict for valid options!",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    parameters = {
        "sid": amach_sid,
        "flag": amach_flag,
        "string": [amach_string],
    }

    # Fetch the datatype for teh requested string
    ierr, data_type = psspy.amachtypes([amach_string])
    if ierr != 0:
        bp(
            f"[ERROR] Failed to fetch data type for amachstring '{amach_string}'. PSSE error code: {ierr}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Retrieve data based on the type
    try:
        if data_type[0] == "I":  # Integer data
            ierr, data = psspy.amachint(**parameters)
        elif data_type[0] == "R":  # Real data
            ierr, data = psspy.amachreal(**parameters)
        elif data_type[0] == "C":  # Character data
            ierr, data = psspy.amachchar(**parameters)
        elif data_type[0] == "X":  # Complex data
            ierr, data = psspy.amachcplx(**parameters)
        else:
            bp(
                f"[ERROR] Unsupported data type '{data_type[0]}' for amachstring '{amach_string}'.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        # Check if data is a list containing a single nested list
        if (
            isinstance(data, list)
            and len(data) == 1
            and isinstance(data[0], list)
        ):
            data = data[0]  # Flatten the list

        # Check if data is a list
        if isinstance(data, list):
            # Check if the list contains strings
            if all(isinstance(item, str) for item in data):
                # Strip whitespace from each string in the list
                data = [item.strip() for item in data]

        if ierr != 0:
            bp(
                f"[ERROR] Failed to retrieve data for amachstring '{amach_string}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if debug_print:
            bp(
                f"[DEBUG] Successfully retrieved data for '{amach_string}': {data}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
        return data

    except Exception as e:
        bp(f"[ERROR] Exception occurred while retrieving data: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def extend_gen_data(
    bspssepy_gen,
    config_table,
    sim_config: config,
    bspssepy_trn,
    bspssepy_bus,
    bspssepy_brn,
    bspssepy_load,
    config,
    debug_print=False,
    app=None,
):

    from .bspssepy_load_funs import new_load

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
    bp("Extending bspssepy_gen Dataframe...", app=app)
    await asyncio.sleep(app.async_print_delay if app else 0)

    bspssepy_status = 0  # 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active
    gen_load_name = "Default"  # Default --> load name is "L[Gen Name]"
    gen_cranking_time = 0.0  # TBD
    gen_ramp_rate = 0.0  # TBD
    bspssepy_gen_type = "NBS"  # NBS or BS, or IBR
    # Type of IBR (e.g., BESS, Wind, Solar) - only used for IBRs
    ibr_type = "N/A"
    gen_cranking_load_power_array = [1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    agc_alpha = 0.0
    load_damp_constant = 0.0
    eff_speed_droop = 0.05
    bias_scaling = 1.0
    p_opf = 0
    q_opf = 0

    # Add new columns if they don't already exist
    new_col = {
        "BSPSSEPyStatus": bspssepy_status,
        "GenLoadName": gen_load_name,
        "GenCrankingTime": gen_cranking_time,
        "GenRampRate": gen_ramp_rate,
        "BSPSSEPyGenType": bspssepy_gen_type,
        # Type of IBR (e.g., BESS, Wind, Solar) - only used for IBRs
        "IBRType": ibr_type,
        "GenCrankingLoadPowerArray": gen_cranking_load_power_array,
        "AGCAlpha": agc_alpha,
        "LoadDampConstant": load_damp_constant,  # D
        "EffectiveSpeedDroop": eff_speed_droop,  # R
        # Bias Scaling (Effective Bias = Bias * Bias Scaling)
        "BiasScaling": bias_scaling,
        "EffectiveBias": 0.0,  # Effective Bias (updated by the simulation)
        "GenTrnBrnName": "",
        "POPF": 0.0,
        "QOPF": 0.0,
        "H": 1.0,  # Inertia constant in seconds (H)
    }

    # Add new columns if they don't already exist
    for col, default_val in new_col.items():
        if col not in bspssepy_gen.columns:
            if isinstance(
                default_val, list
            ):  # For list values, use object dtype
                bspssepy_gen[col] = pd.Series(
                    [default_val] * len(bspssepy_gen), dtype="object"
                )
            else:
                bspssepy_gen[col] = default_val

            if debug_print:
                bp(
                    f"[DEBUG] Added column '{col}' with default value: {default_val}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

    for config in config_table:
        gen_name = config.get("Generator Name")
        # gen_id = config.get("Generator ID")
        bus_name = config.get("Bus Name")

        if debug_print:
            bp(
                f"[DEBUG] Processing configuration for Generator Name: {gen_name}, Bus Name: {bus_name}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Locate the generator based on GenName or BusName
        gen_indicies = None
        if gen_name:
            gen_indicies = bspssepy_gen[
                bspssepy_gen["MCNAME"] == gen_name
            ].index
            if debug_print:
                bp(
                    f"[DEBUG] Located generator index by Name ({gen_name}): {list(gen_indicies)}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
        elif bus_name:
            gen_indicies = bspssepy_gen[
                bspssepy_gen["NAME"] == bus_name
            ].index
            if debug_print:
                bp(
                    f"[DEBUG] Located generator index by Bus Name ({bus_name}): {list(gen_indicies)}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

        # If no matching generator is found, skip
        if gen_indicies is None or gen_indicies.empty:
            bp(
                f"Warning: No matching generator found for '{gen_name or bus_name}'. Skipping.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            continue

        if debug_print:
            bp(
                f"[DEBUG] Generator index to update: {list(gen_indicies)}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Extract configuration values or use defaults
        bspssepy_gen_type = config.get("Generator Type", bspssepy_gen_type)
        bspssepy_status = (
            3
            if bspssepy_gen_type == "BS"
            else config.get("Status", bspssepy_status)
        )
        gen_load_name = config.get("load Name", gen_load_name)
        gen_cranking_time = config.get("Cranking Time", gen_cranking_time)
        gen_ramp_rate = config.get("Ramp Rate", gen_ramp_rate)
        gen_cranking_load_power_array = config.get(
            "Cranking load Array", gen_cranking_load_power_array
        )
        agc_alpha = config.get("AGC Participation Factor", agc_alpha)
        load_damp_constant = config.get(
            "load Damping Constant", load_damp_constant
        )
        eff_speed_droop = config.get("Effective Speed Droop", eff_speed_droop)
        bias_scaling = config.get("Bias Scaling", bias_scaling)
        p_opf = config.get("POPF", p_opf)
        q_opf = config.get("QOPF", q_opf)
        use_gen_ramo_rate = config.get("UseGenRampRate", False)
        load_enabled_response = config.get("Load Enabled Response", False)
        LERPF = config.get("LERPF", -1)
        H = config.get("Inertia Constant", 1.0)

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
            bp(f"[DEBUG] Extracted config Values for '{gen_name}':", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(
                f"        Status: {bspssepy_status} (0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active)",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        load Name: {gen_load_name}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Cranking Time: {gen_cranking_time}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Ramp Rate: {gen_ramp_rate}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Generator Type: {bspssepy_gen_type}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(
                f"        Cranking load Array: {gen_cranking_load_power_array}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        AGC Participation Factor: {agc_alpha}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(
                f"        load Damping Constant: {load_damp_constant}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Effective Speed Droop: {eff_speed_droop}")
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(f"        Bias Scaling: {bias_scaling}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(
                f"        Effective Bias: {bias_scaling * (1/eff_speed_droop + load_damp_constant)}",
                app=app,
            )
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

        updates = {
            "BSPSSEPyStatus": bspssepy_status,
            "GenLoadName": gen_load_name,
            "GenCrankingTime": gen_cranking_time,
            "GenRampRate": gen_ramp_rate,
            "BSPSSEPyGenType": bspssepy_gen_type,
            "GenCrankingLoadPowerArray": gen_cranking_load_power_array,
            "AGCAlpha": agc_alpha,
            "LoadDampConstant": load_damp_constant,  # D
            "EffectiveSpeedDroop": eff_speed_droop,  # R
            # Bias Scaling (Effective Bias = Bias * Bias Scaling)
            "BiasScaling": bias_scaling,
            "EffectiveBias": bias_scaling
            * ((1 / eff_speed_droop) + load_damp_constant),
            "POPF": p_opf,
            "QOPF": q_opf,
            "UseGenRampRate": use_gen_ramo_rate,
            "LoadEnabledResponse": load_enabled_response,
            "LERPF": LERPF,
            "H": H,  # Inertia constant in seconds (H)
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
        for col, val in updates.items():
            if debug_print:
                bp(
                    f"[DEBUG] Updating column '{col}' with value: {val}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            if (
                col == "GenCrankingLoadPowerArray"
            ):  # Special handling for lists
                for idx in gen_indicies:  # Assign each list individually
                    bspssepy_gen.at[idx, col] = val
                    if debug_print:
                        bp(
                            f"[DEBUG] Updated '{col}' at index {idx} with list value: {val}",
                            app=app,
                        )
                        await asyncio.sleep(
                            app.async_print_delay if app else 0
                        )
            else:
                bspssepy_gen.loc[gen_indicies, col] = val
                if debug_print:
                    bp(
                        f"[DEBUG] Updated '{col}' for generator(s) at indices {list(gen_indicies)} with value: {val}",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)

    # bspssepy_gen["BSPSSEPyStatus"] = bspssepy_gen["STATUS"].apply(
    #         lambda x: "In-Service" if x == 1 else "Offline"
    #     )

    # Initial Status
    bspssepy_gen["BSPSSEPyStatus_0"] = bspssepy_gen["BSPSSEPyStatus"]

    bspssepy_gen["BSPSSEPyLastAction"] = "Initialized"
    bspssepy_gen["BSPSSEPyLastActionTime"] = 0.0
    bspssepy_gen["BSPSSEPySimulationNotes"] = "Initialized"
    # --> corresponding to GREF in machine_array_channel (check the API - status(2) = 14)
    bspssepy_gen["GREFChannel"] = -1
    # --> corresponding to VREF in machine_array_channel (check the API - status(2) = 11)
    bspssepy_gen["VREFChannel"] = -1
    # --> corresponding to PELEC in machine_array_channel (check the API - status(2) = 2)
    bspssepy_gen["PELECChannel"] = -1
    # --> corresponding to QELEC in machine_array_channel (check the API - status(2) = 3)
    bspssepy_gen["QELECChannel"] = -1
    # --> corresponding to PMECH in machine_array_channel (check the API - status(2) = 6)
    bspssepy_gen["PMECHChannel"] = -1
    # --> This is the frequency channel for the generator (will be fetched from config.Channels)
    bspssepy_gen["FChannel"] = -1

    # Informaiton about the main connection element that connect the generator to the grid. This is required for "simulating the non-black-start generators connection back to the grid". The idea is to enable "load cranking" for some time, and then when we would like to connect the generator, we disconnect the load, close the branch/transformer and then control the output power of the generator until ramp-up phase is complete.
    bspssepy_gen["ConnectionType"] = None
    bspssepy_gen["ConnectionElementFromBus"] = None
    bspssepy_gen["ConnectionElementToBus"] = None
    bspssepy_gen["ConnectionElementID"] = None
    bspssepy_gen["ConnectionElementName"] = None
    bspssepy_gen["p_elec"] = 0
    bspssepy_gen["p_mech"] = 0
    bspssepy_gen["q_elec"] = 0
    bspssepy_gen["g_ref"] = 0
    bspssepy_gen["v_ref"] = 0
    bspssepy_gen["freq"] = 0

    bp(
        "Adding 'GREF', 'VREF', 'PELEC', 'QELEC', 'PMECH' channels to all generators + custom loads for non-black-start generators.",
        app=app,
    )
    await asyncio.sleep(app.async_print_delay if app else 0)
    bp(
        "Also adding informaiton about generator connection elements to bspssepy_gen",
        app=app,
    )
    await asyncio.sleep(app.async_print_delay if app else 0)
    # Loop through generators and process them based on their type
    for gen_row_index, gen_row in bspssepy_gen.iterrows():
        gen_type = gen_row.get("BSPSSEPyGenType", "")
        gen_name = gen_row["MCNAME"]

        # Call the GetGeneratorConnectionPoint function
        connection_point = await get_gen_connection_point(
            t=0,
            bspssepy_gen=bspssepy_gen,
            bspssepy_bus=bspssepy_bus,
            gen_name=gen_name,
            bspssepy_trn=bspssepy_trn,
            bspssepy_brn=bspssepy_brn,
            debug_print=debug_print,
            app=app,
        )

        # Add the connection point details to the Updates dictionary if found
        if not (connection_point):
            bp(
                f"[ERROR] Could not find a connection point for generator {gen_name}.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                raise Exception(
                    "Error in ExtendBSPSSEPyGenDataFrame Function!"
                )
            else:
                SystemExit(1)

        # Define the mapping between bspssepy_gen columns and ConnectionPoint keys
        keys = [
            "ConnectionType",
            "ConnectionElementFromBus",
            "ConnectionElementToBus",
            "ConnectionElementID",
            "ConnectionElementName",
        ]

        # Use a list comprehension to extract values from ConnectionPoint
        gen_row[keys] = [connection_point[key] for key in keys]
        bspssepy_gen.loc[gen_row_index, keys] = [
            connection_point[key] for key in keys
        ]

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
                [
                    -1,  # Next available channel
                    # status(2) --> quantity to monitor
                    bspssepy_gen_ch_mapping[key],
                    # Bus number corresponding to machine location
                    int(gen_row["NUMBER"]),
                ],
                gen_row["ID"],  # ID of the machine
                key + gen_row["MCNAME"],  # Channel Identifier
            )

            if ierr != 0:
                bp(
                    f"[ERROR] Error occured during adding channel for Gen: {gen_row['MCNAME']} to monitor {key} with key_status number: {bspssepy_gen_ch_mapping[key]}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
            else:
                bspssepy_gen.at[gen_row_index, key + "Channel"] = (
                    sim_config.current_channel_index
                )
                if debug_print:
                    bp(
                        f"[DEBUG] Successfully added channel for Gen: {gen_row['MCNAME']} to monitor {key} with channel index {sim_config.current_channel_index}",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                sim_config.current_channel_index += (
                    1  # Increament Channel index
                )

        # Check if generator is a black-start generator
        if gen_type.lower() in [
            "blackstart",
            "black-start",
            "black start",
            "bs",
        ]:
            bp(f"Skipping black-start generator: {gen_name}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            continue

        bus_num = gen_row["NUMBER"]
        bus_name = gen_row["NAME"]

        load_bus_num = (
            gen_row["ConnectionElementFromBus"]
            if (bus_num == gen_row["ConnectionElementToBus"])
            else gen_row["ConnectionElementToBus"]
        )
        from .bspssepy_bus_funs import get_bus_info

        load_bus_name = await get_bus_info(
            "NAME", bus=load_bus_num, debug_print=debug_print, app=app
        )

        load_name = gen_row["GenLoadName"]
        if load_name == "" or load_name is None:
            load_name = f"CL{gen_name}"

        bp(
            f"Adding custom load for Genrator: {gen_name} at bus {load_bus_name}(#{load_bus_num}), with loadname {load_name}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

        # Prepare power array for the new load
        cranking_load_array = gen_row.get("GenCrankingLoadPowerArray", "")
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
        bspssepy_load, ierr = await new_load(
            load_name=load_name,
            bspssepy_load=bspssepy_load,
            bus_name=load_bus_name,
            bus_num=load_bus_num,
            element_name=gen_name,
            element_type="Gen",
            power_array=cranking_load_array,
            t=0,
            debug_print=debug_print,
            app=app,
        )
    bp(
        "DataFrame successfully updated with new generator phases and states.",
        app=app,
    )
    await asyncio.sleep(app.async_print_delay if app else 0)

    return bspssepy_gen, bspssepy_load


async def get_gen_connection_point(
    t,
    bspssepy_gen,
    gen_name,
    bspssepy_bus,
    bspssepy_trn,
    bspssepy_brn,
    debug_print=False,
    app=None,
):
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
        bp(
            f"[DEBUG] Running GetGeneratorConnectionPoint for {gen_name}.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Get generator information
    try:
        gen_row = bspssepy_gen.loc[bspssepy_gen["MCNAME"] == gen_name].iloc[0]
    except IndexError:
        bp(
            f"[ERROR] Generator {gen_name} not found in bspssepy_gen.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    gen_bus = gen_row["NAME"]

    # Setting GenBus as swing for all Gens
    from .bspssepy_bus_funs import change_bus_type

    # ierr = ChangeBusType(t = t, NewBusType=3, bspssepy_bus=bspssepy_bus, Bus=GenBus, debug_print=debug_print)

    # Identify the main connection device (transformer or branch)
    trn_row = bspssepy_trn[
        (bspssepy_trn["FROMNAME"] == gen_bus)
        | (bspssepy_trn["TONAME"] == gen_bus)
    ]
    brn_row = bspssepy_brn[
        (bspssepy_brn["FROMNAME"] == gen_bus)
        | (bspssepy_brn["TONAME"] == gen_bus)
    ]

    # Check if a transformer is connected
    if not trn_row.empty:
        main_connection_type = device_type_mapping["t"]
        main_connection_row = trn_row.iloc[0]
        device_name = main_connection_row["XFRNAME"]
        if gen_row["BSPSSEPyGenType"] != "BS":
            bspssepy_trn.loc[
                bspssepy_trn.index == main_connection_row.name,
                "GenControlled",
            ] = True
    elif not brn_row.empty:
        main_connection_type = device_type_mapping["branch"]
        main_connection_row = brn_row.iloc[0]
        device_name = main_connection_row["BRANCHNAME"]
        if gen_row["BSPSSEPyGenType"] != "BS":
            bspssepy_brn.loc[
                bspssepy_brn.index == main_connection_row.name,
                "GenControlled",
            ] = True
    else:
        bp(
            f"[ERROR] No connection device found for generator {gen_name} at Bus {gen_bus}.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Extract connection details
    from_bus = main_connection_row["FROMNUMBER"]
    to_bus = main_connection_row["TONUMBER"]
    device_id = main_connection_row["ID"]

    if debug_print:
        bp(
            f"[DEBUG] Connection Point for {gen_name}: {main_connection_type} from Bus {from_bus} to Bus {to_bus}.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    return {
        "ConnectionType": main_connection_type,
        "ConnectionElementFromBus": from_bus,
        "ConnectionElementToBus": to_bus,
        "ConnectionElementID": device_id,
        "ConnectionElementName": device_name,
        "Row": main_connection_row,
    }


async def gen_enable(
    bspssepy_gen,
    t,
    action,
    gen_name,
    bspssepy_trn,
    bspssepy_brn,
    bspssepy_load,
    bspssepy_bus,
    bspssepy_agc,
    config,
    debug_print=False,
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
        bp(
            f"[DEBUG] Running GenEnable function for action: {action}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # get Gen row from bspssepy_gen
    gen_row = bspssepy_gen.loc[
        bspssepy_gen["MCNAME"] == action["ElementIDValue"]
    ].copy()

    from .bspssepy_default_vars import bspssepy_default_vars_fun

    default_int, default_real, default_char = bspssepy_default_vars_fun()

    # To turn on this generator, we need to check at which phase it is currently!
    # 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active
    # Check if the generator is off --> To enter cranking phase
    if gen_row["BSPSSEPyStatus"].values[0] == 0:
        # So the generator is off, let's prepare it to "crank".

        # ▂▃▄▅▆▇█▓▒░ Cranking (0 → 1) ░▒▓█▇▆▅▄▃▂

        # First check that there is an energized line or transformer at the generator bus!
        gen_bus_name = gen_row["NAME"].values[0]
        if debug_print:
            bp(
                f"[DEBUG] Checking if the generator is energized correctly by examining bus:{gen_bus_name}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        if any(
            brn["BSPSSEPyStatus"] == "Closed"
            for _, brn in bspssepy_brn[
                (bspssepy_brn["FROMNAME"] == gen_bus_name)
                | (bspssepy_brn["TONAME"] == gen_bus_name)
            ].iterrows()
        ) or any(
            trn["BSPSSEPyStatus"] == "Closed"
            for _, trn in bspssepy_trn[
                (bspssepy_trn["FROMNAME"] == gen_bus_name)
                | (bspssepy_trn["TONAME"] == gen_bus_name)
            ].iterrows()
        ):
            bp(
                f"[ERROR] Cannot Enter Cranking phase as GenBusName: {gen_bus_name} is energized. With this, the generator is already connected! Check the recovery plan to energize the 'far' bus first and crank the Genload before energizing the transformer/line connected to the generator! The program will exit.",
                app=app,
            )
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
        gen_load_name = gen_row["GenLoadName"].values[0]

        if debug_print:
            bp(
                f"[DEBUG] Generator is about to crank. Attempting to enable the associated load: {gen_load_name}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        from .bspssepy_load_funs import load_enable, load_disable

        # Enable GenLoad to start cranking and set the generator output power to zero
        ierr = await load_enable(
            t=t,
            bspssepy_load=bspssepy_load,
            load_name=gen_load_name,
            debug_print=debug_print,
            app=app,
            bspssepy_agc=bspssepy_agc,
            bspssepy_gen=bspssepy_gen,
        )

        if ierr != 0:
            bp(
                f"[ERROR] Could not enable GenLoad:{gen_load_name}. Generator did not start the cranking phase.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            updated_action_status = 0
            return updated_action_status

        if debug_print:
            bp(
                f"[DEBUG] GenLoad:{gen_load_name} was enabled successfully. Recording Cranking Start Time in bspssepy_gen dataframe",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        # 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active
        gen_row["BSPSSEPyStatus"] = 1
        gen_row["BSPSSEPyLastAction"] = "Crank"
        gen_row["BSPSSEPyLastActionTime"] = t
        gen_row["BSPSSEPySimulationNotes"] = (
            f"Successfully entered cranking phase at t = {t}"
        )

        # Write the row back to the DataFrame
        bspssepy_gen.loc[bspssepy_gen["MCNAME"] == gen_name, :] = gen_row

        bp(f"Generator '{gen_name}' started cranking phase.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

        updated_action_status = (
            1  # 0: Not started, 1: In progress, 2: Completed
        )
        return updated_action_status

    # Check if the generator is Cranking --> To enter Ramp-up phase
    elif gen_row["BSPSSEPyStatus"].values[0] == 1:

        # ▂▃▄▅▆▇█▓▒░ Ramp-up (1 → 2) ░▒▓█▇▆▅▄▃▂
        # So the generator is cranking. Check if cranking should stop and start ramping up the generator.

        # Check if Cranking time is met!
        if (
            t
            < gen_row["GenCrankingTime"].values[0] * 60
            + gen_row["BSPSSEPyLastActionTime"].values[0]
        ):
            if debug_print:
                bp(
                    f"[DEBUG] Gen {gen_name} is still cranking. (Cranking ends at t = {gen_row['GenCrankingTime'].values[0]*60 + gen_row['BSPSSEPyLastActionTime'].values[0]} - remaining {gen_row['GenCrankingTime'].values[0]*60 + gen_row['BSPSSEPyLastActionTime'].values[0] - t}s)",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
            updated_action_status = 1
            return updated_action_status
        else:
            bp(
                f"Generator: '{gen_name}' cranking time met. Disabling the associated load. ",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

            # Cranking finished! Let's disable the GenLoad
            gen_load_name = gen_row["GenLoadName"].values[0]

            if debug_print:
                bp(
                    f"[DEBUG] Attempting to disable the associated load: {gen_load_name}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            from .bspssepy_load_funs import load_disable

            # Enable GenLoad to start cranking and set the generator output power to zero
            ierr = await load_disable(
                t=t,
                bspssepy_load=bspssepy_load,
                load_name=gen_load_name,
                debug_print=debug_print,
                app=app,
            )

            if ierr != 0:
                bp(
                    f"[ERROR] Could not disable GenLoad:{gen_load_name}. Generator did not stop the cranking phase.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
                updated_action_status = 1
                return updated_action_status

            if debug_print:
                bp(
                    f"[DEBUG] GenLoad:{gen_load_name} was disabled successfully. Energizing the connection element (TRN or BRN) to start the Ramp-up phase.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            element_name = gen_row["ConnectionElementName"].values[0]

            if gen_row["ConnectionType"].values[0] == "TRN":
                from .bspssepy_trn_funs import trn_close

                ierr = await trn_close(
                    t=t,
                    trn_name=element_name,
                    bspssepy_trn=bspssepy_trn,
                    bspssepy_bus=bspssepy_bus,
                    called_by_gen=True,
                    debug_print=debug_print,
                    app=app,
                )

                if ierr == 0:
                    if debug_print:
                        bp(
                            f"[DEBUG] generator is connected successfully. Controlling the generator output power.",
                            app=app,
                        )
                        await asyncio.sleep(
                            app.async_print_delay if app else 0
                        )
                else:
                    bp(
                        "[ERROR] Encountered error during GenEnabled -- TrnClose function! Program will exit",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    if app:
                        raise Exception(
                            "Error in GenEnable Function --> Could not start ramp-up phase!"
                        )
                    else:
                        SystemExit(1)

            elif gen_row["ConnectionType"].values[0] == "BRN":
                from .bspssepy_brn_funs import brn_close

                ierr = await brn_close(
                    t=t,
                    brn_name=element_name,
                    bspssepy_brn=bspssepy_brn,
                    bspssepy_bus=bspssepy_bus,
                    called_by_gen=True,
                    debug_print=debug_print,
                    app=app,
                )

                if ierr == 0:
                    if debug_print:
                        bp(
                            f"[DEBUG] generator is connected successfully. Controlling the generator output power.",
                            app=app,
                        )
                        await asyncio.sleep(
                            app.async_print_delay if app else 0
                        )
                else:
                    bp(
                        "[ERROR] Encountered error during GenEnabled -- BrnClose function! Program will exit",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    if app:
                        raise Exception(
                            "Error in GenEnable Function --> Could not start ramp-up phase!"
                        )
                    else:
                        SystemExit(1)

            else:
                bp(
                    "[ERROR] Unkown element. Could not enable/connect the generator. Program will exit",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(1)

            # GenG = await FetchChannelValue(int(BSPSSEPyGenRow["GREFChannel"].values[0]), debug_print=debug_print,app=app)
            gen_v = await fetch_channel_value(
                int(gen_row["VREFChannel"].values[0]),
                debug_print=debug_print,
                app=app,
            )
            # GenP = await FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), debug_print=debug_print,app=app)
            # GenQ = await FetchChannelValue(int(BSPSSEPyGenRow["QELECChannel"].values[0]), debug_print=debug_print,app=app)
            # GenPm = await FetchChannelValue(int(BSPSSEPyGenRow["PMECHChannel"].values[0]), debug_print=debug_print,app=app)
            # bp(f"GenG: {GenG}, GenV: {GenV}, GenP: {GenP}, GenQ: {GenQ}, GenPm: {GenPm}",app=app)
            # await asyncio.sleep(app.async_print_delay if app else 0)

            gen_bus_num = gen_row["NUMBER"].values[0]
            gen_id = gen_row["ID"].values[0]

            # Get the base MVA of the generator
            ierr, gen_mva_base = psspy.macdat(gen_bus_num, gen_id, "MBASE")

            # Set the generator output real power to zero
            ierr = psspy.change_gref(gen_bus_num, gen_id, 0 / gen_mva_base)

            if ierr != 0:
                bp(
                    f"[ERROR] Error occured when setting generator: {gen_name} output real power to zero. System will exit.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable Function!")
                else:
                    SystemExit(0)

            if debug_print:
                bp(
                    f"[DEBUG] Successfully set generator: {gen_name} output real power to zero.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            # Set the generator output reactive power to zero (we set Vref to Vref channel value -- no change in Q of teh generator is needed then)
            ierr = psspy.change_vref(gen_bus_num, gen_id, gen_v)
            if ierr != 0:
                bp(
                    f"[ERROR] Error occured when setting generator: {gen_name} output reactive power to zero. System will exit.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)

            if debug_print:
                bp(
                    f"[DEBUG] Successfully set generator: {gen_name} output reactive power to zero.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            gen_row["BSPSSEPyStatus"] = 2
            gen_row["BSPSSEPyLastAction"] = "Ramp-Up"
            gen_row["BSPSSEPyLastActionTime"] = t
            gen_row["BSPSSEPySimulationNotes"] = (
                f"Successfully entered Ramping-up phase at t = {t}"
            )

            # Write the row back to the DataFrame
            bspssepy_gen.loc[bspssepy_gen["MCNAME"] == gen_name, :] = gen_row

            bp(f"Generator '{gen_name}' started Ramping-Up phase.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

            updated_action_status = 1
            return updated_action_status

    elif gen_row["BSPSSEPyStatus"].values[0] == 2:

        # ▂▃▄▅▆▇█▓▒░ In-service (2 → 3) ░▒▓█▇▆▅▄▃▂
        # So the generator is Ramping-Up. Check if ramping-up should stop and start In-Service Phase of the generator.

        # The goal is to ramp up the generator to the POPF value for now.
        # When the generator is at around that value, the ramp-up phase will be considered complete.

        # Check if the generator is supposed to use the explicit ramp-rate defiend in bspssepy_gen or this will be embedded in the generator model (i.e. IEEEG1 model for example has its own ramp-rate model inside it)
        gen_bus_num = gen_row["NUMBER"].values[0]
        gen_id = gen_row["ID"].values[0]
        ierr, gen_mva_base = psspy.macdat(gen_bus_num, gen_id, "MBASE")
        gen_p_opf = gen_row["POPF"].values[0]
        gen_p_opf_pu = gen_p_opf / gen_mva_base
        # Check if the generator is at the target power level
        gen_p = (
            await fetch_channel_value(
                int(gen_row["PELECChannel"].values[0]),
                debug_print=debug_print,
                app=app,
            )
            * gen_mva_base
        )

        if gen_p_opf == 0:
            # Ramp-up is provided by the plan - exit the ramp-up phase!
            bp(
                f"Generator: '{gen_name}' ramp-up phase is skipped (provided by the plan). Setting the generator to In-service phase.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

            gen_row["BSPSSEPyStatus"] = 3
            gen_row["BSPSSEPyLastAction"] = "In-service"
            gen_row["BSPSSEPyLastActionTime"] = t
            gen_row["BSPSSEPySimulationNotes"] = (
                f"Successfully entered In-service phase at t = {t}"
            )

            # Write the row back to the DataFrame
            bspssepy_gen.loc[bspssepy_gen["MCNAME"] == gen_name, :] = gen_row

            bp(f"Generator '{gen_name}' started In-service phase.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            updated_action_status = 2
            return updated_action_status

        use_gen_ramp_rate = gen_row["UseGenRampRate"].values[0]
        if (
            use_gen_ramp_rate
        ):  # will use the explicit ramp-rate defined in bspssepy_gen
            if debug_print:
                bp(
                    f"[DEBUG] Using explicit ramp-rate for generator: {gen_name} - Ramp Rate: {gen_row['GenRampRate'].values[0]} MW/min",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
            # convert the ramp rate to MW/sec
            gen_ramp_rate_per_sec = gen_row["GenRampRate"].values[0] / 60

            if gen_p > gen_p_opf:
                gen_ramp_rate_per_sec = -gen_ramp_rate_per_sec

            # we use psspy.increment_gref function to increase/adjust generator output power gradually.
            ierr = psspy.increment_gref(
                gen_bus_num, gen_id, gen_ramp_rate_per_sec / gen_mva_base
            )  # Apply increment

            if ierr != 0:
                bp(
                    f"[ERROR] Updating setpoint for Generator {gen_name} (ID = {gen_id}) at Bus {gen_bus_num}, ierr={ierr}",
                    app=app,
                )
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

        # will use the generator model ramp-rate (we simply provide the target output power, and the generator model will take care of the ramp-rate)
        else:
            if debug_print:
                bp(
                    f"[DEBUG] Using generator model ramp-rate for generator: {gen_name} - Target Power: {gen_p_opf} MW",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
            # we use psspy.increment_gref function to increase/adjust generator output power gradually.
            # Apply the target output power
            ierr = psspy.increment_gref(gen_bus_num, gen_id, gen_p_opf_pu)
            if ierr != 0:
                bp(
                    f"[ERROR] Updating setpoint for Generator {gen_name} (ID = {gen_id}) at Bus {gen_bus_num}, ierr={ierr}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)
            updated_action_status = 2
            return updated_action_status

        # # Check if the generator is at the target power level
        # GenP = FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), debug_print=debug_print) * gen_mva_base

        if debug_print:
            bp(
                f"[DEBUG] Generator: {gen_name} - Current Power: {gen_p}, Target Power: {gen_p_opf} MW",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        # If generator output power is within 1% of the target power, we consider the ramp-up phase to be complete, and we provide the generator with the reference value for Gref
        if abs(gen_p_opf - gen_p) / gen_p_opf <= 0.01:
            if use_gen_ramp_rate:
                if abs(gen_p_opf - gen_p) > gen_ramp_rate_per_sec:
                    if debug_print:
                        bp(
                            f"[DEBUG] Generator: {gen_name} is still ramping up. (Current Power: {gen_p}, Target Power: {gen_p_opf} MW)",
                            app=app,
                        )
                        await asyncio.sleep(
                            app.async_print_delay if app else 0
                        )
                    updated_action_status = 1
                    return updated_action_status

            # Set the generator output real power to zero
            ierr = psspy.change_gref(gen_bus_num, gen_id, gen_p_opf_pu)

            if ierr != 0:
                bp(
                    f"[ERROR] Error occured when setting generator: {gen_name} output real power to GenPOPF: {gen_p_opf}.System will exit.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
                if app:
                    raise Exception("Error in GenEnable function!")
                else:
                    SystemExit(0)

            if debug_print:
                bp(
                    f"[DEBUG] Successfully set generator: {gen_name} output real power to GenPOPF: {gen_p_opf}.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            bp(
                f"Generator: '{gen_name}' ramp-up phase completed. Setting the generator to In-service phase.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

            gen_row["BSPSSEPyStatus"] = 3
            gen_row["BSPSSEPyLastAction"] = "In-service"
            gen_row["BSPSSEPyLastActionTime"] = t
            gen_row["BSPSSEPySimulationNotes"] = (
                f"Successfully entered In-service phase at t = {t}"
            )

            # Write the row back to the DataFrame
            bspssepy_gen.loc[bspssepy_gen["MCNAME"] == gen_name, :] = gen_row

            bp(f"Generator '{gen_name}' started In-service phase.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            updated_action_status = 2
            return updated_action_status

        else:
            if debug_print:
                bp(
                    f"[DEBUG] Generator: {gen_name} is still ramping up. (Current Power: {gen_p}, Target Power: {gen_p_opf} MW)",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            """
            GetGenInfo("PGEN")
                0    0.175725
                1    0.000000
                2    0.059810
                Name: PGEN, dtype: float64
                GetGenInfo("QGEN")
            """

            updated_action_status = 1
            return updated_action_status


async def gen_disable(
    t,
    gen_name,
    bspssepy_gen,
    bspssepy_bus,
    bspssepy_trn,
    bspssepy_brn,
    debug_print=False,
    app=None,
):
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
        bp(
            f"[DEBUG] GenDisable called with inputs:\n"
            f"  t = {t}"
            f"  GenName: {gen_name}",  # f"  bspssepy_gen: {bspssepy_gen}"
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Fetch Generator details
    gen_row = await get_gen_info(
        [
            "NAME",
            "MCNAME",
            "ID",
            "NUMBER",
            "STATUS",
            "ConnectionType",
            "ConnectionElementName",
            "BSPSSEPyStatus",
        ],
        gen_name=gen_name,
        bspssepy_gen=bspssepy_gen,
        debug_print=debug_print,
        app=app,
    )

    if gen_row is None or len(gen_row) == 0:
        bp(f"[ERROR] Generator not found for GenName = {gen_name}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    gen_bus_name = gen_row["NAME"].values[0]
    gen_id = gen_row["ID"].values[0]
    gen_bus_num = gen_row["NUMBER"].values[0]
    gen_status = gen_row["STATUS"].values[0]
    gen_bspssepy_status = gen_row["BSPSSEPyStatus"].values[0]
    gen_con_type = gen_row["ConnectionType"].values[0]
    gen_con_element_name = gen_row["ConnectionElementName"].values[0]

    if debug_print:
        bp(
            f"[DEBUG] Determining the connection point element (TRN or BRN) for Gen {gen_name}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
    if gen_con_type == "TRN":
        bp(
            f"Checking the status of the transformer connecting {gen_name} to the grid:{gen_con_type} - {gen_con_element_name}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        from .bspssepy_trn_funs import get_trn_info, trn_trip

        element_status = await get_trn_info(
            "STATUS",
            trn_name=gen_con_element_name,
            debug_print=debug_print,
            app=app,
        )
        if element_status != 0:
            if debug_print:
                bp(
                    f"[DEBUG] The two-winding transformer: {gen_con_element_name} status is {element_status}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            bp(
                f"Tripping the transformer connecting {gen_name} --> {gen_con_type} - {gen_con_element_name}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

            await trn_trip(
                t=t,
                bspssepy_trn=bspssepy_trn,
                trn_name=gen_con_element_name,
                debug_print=debug_print,
                app=app,
            )

            if debug_print:
                bp(
                    f"[DEBUG] Successfully tripped two-winding transformer: {gen_con_element_name}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
        else:
            bp(
                f"The transformer connecting the generator is tripped already ({gen_name} --> {gen_con_type} - {gen_con_element_name})",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

    elif gen_row["ConnectionType"].values[0] == "BRN":
        bp(
            f"Checking the status of the branch connecting {gen_name} to the grid:{gen_con_type} - {gen_con_element_name}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        from .bspssepy_brn_funs import get_brn_info, brn_trip

        element_status = await get_brn_info(
            "STATUS",
            brn_name=gen_con_element_name,
            debug_print=debug_print,
            app=app,
        )
        if element_status != 0:
            if debug_print:
                bp(
                    f"[DEBUG] The branch: {gen_con_element_name} status is {element_status}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            bp(
                f"Tripping the branch connecting {gen_name} --> {gen_con_type} - {gen_con_element_name}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

            await brn_trip(
                t=t,
                bspssepy_brn=bspssepy_brn,
                brn_name=gen_con_element_name,
                debug_print=debug_print,
                app=app,
            )

            if debug_print:
                bp(
                    f"[DEBUG] Successfully tripped Branch: {gen_con_element_name}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
        else:
            bp(
                f"The branch connecting the generator is tripped already ({gen_name} --> {gen_con_type} - {gen_con_element_name})",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
    else:
        bp(
            f"[ERROR] Could not identify how the generator is connected to the grid. program will exit!",
            app=app,
        )
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

    from .bspssepy_bus_funs import change_bus_type

    ierr = await change_bus_type(
        t=t,
        new_bus_type=3,
        bspssepy_bus=bspssepy_bus,
        bus=gen_bus_name,
        debug_print=debug_print,
        app=app,
    )
    if ierr != 0:
        bp(
            f"[ERROR] Could not set the bus of Gen {gen_name} (Bus {gen_bus_name}) to type 3 (swing), program will exit.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        if app:
            raise Exception("Error in GenEnable function!")
        else:
            SystemExit(1)

    # Updating bspssepy_gen to reflect that the generator is not connected
    if not (bspssepy_gen is None or bspssepy_gen.empty):
        gen_updated_status = await get_gen_info(
            "STATUS", gen_name=gen_name, debug_print=debug_print, app=app
        )

        # Update the bspssepy_gen DataFrame
        bspssepy_gen.loc[
            (bspssepy_gen["MCNAME"].apply(str) == str(gen_name))
            & (bspssepy_gen["ID"].apply(str) == str(gen_id))
            & (bspssepy_gen["NUMBER"].apply(str) == str(gen_bus_num)),
            [
                "BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "STATUS",
            ],
        ] = [
            0,
            "Disable",
            t,
            "Generator Successfully Disabled.",
            gen_updated_status,
        ]


async def gen_update(
    bspssepy_gen,
    t,
    action,
    gen_name,
    bspssepy_trn,
    bspssepy_brn,
    bspssepy_load,
    bspssepy_bus,
    bspssepy_agc,
    config,
    debug_print=False,
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
        bp(
            f"[DEBUG] Running GenEnable function for action: {action}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    values: dict = config.bspssepy_sequence.at[
        action["BSPSSEPySequenceRowIndex"], "Values"
    ]
    # bp(f"Values Type = {type(Values)}"
    #         f"Values Content:\n{Values}")
    # await asyncio.sleep(app.async_print_delay if app else 0)

    gen_p_setpoint = values["P"] if "P" in values else None
    gen_q_setpoint = values["Q"] if "Q" in values else None

    # get Gen row from bspssepy_gen
    gen_row = bspssepy_gen.loc[
        bspssepy_gen["MCNAME"] == action["ElementIDValue"]
    ].copy()

    from .bspssepy_default_vars import bspssepy_default_vars_fun

    default_int, default_real, default_char = bspssepy_default_vars_fun()

    # Check if the generator is supposed to use the explicit ramp-rate defiend in bspssepy_gen or this will be embedded in the generator model (i.e. IEEEG1 model for example has its own ramp-rate model inside it)
    gen_bus_num = gen_row["NUMBER"].values[0]
    gen_id = gen_row["ID"].values[0]
    ierr, gen_mva_base = psspy.macdat(gen_bus_num, gen_id, "MBASE")
    # GenTargetPower = BSPSSEPyGenRow["POPF"].values[0]
    gen_p_setpoint_pu = gen_p_setpoint / gen_mva_base
    # Check if the generator is at the target power level
    gen_p = (
        await fetch_channel_value(
            int(gen_row["PELECChannel"].values[0]),
            debug_print=debug_print,
            app=app,
        )
        * gen_mva_base
    )

    use_gen_ramp_rate = gen_row["UseGenRampRate"].values[0]
    if (
        use_gen_ramp_rate
    ):  # will use the explicit ramp-rate defined in bspssepy_gen
        if debug_print:
            bp(
                f"[DEBUG] Using explicit ramp-rate for generator: {gen_name} - Ramp Rate: {gen_row['GenRampRate'].values[0]} MW/min",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
        # convert the ramp rate to MW/sec
        gen_ramp_rate_per_sec = gen_row["GenRampRate"].values[0] / 60

        if gen_p > gen_p_setpoint:
            gen_ramp_rate_per_sec = -gen_ramp_rate_per_sec

        # we use psspy.increment_gref function to increase/adjust generator output power gradually.
        ierr = psspy.increment_gref(
            gen_bus_num, gen_id, gen_ramp_rate_per_sec / gen_mva_base
        )  # Apply increment

        if ierr != 0:
            bp(
                f"[ERROR] Updating setpoint for Generator {gen_name} (ID = {gen_id}) at Bus {gen_bus_num}, ierr={ierr}",
                app=app,
            )
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

    # will use the generator model ramp-rate (we simply provide the target output power, and the generator model will take care of the ramp-rate)
    else:
        if debug_print:
            bp(
                f"[DEBUG] Using generator model ramp-rate for generator: {gen_name} - Target Power: {gen_p_setpoint} MW",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
        # we use psspy.increment_gref function to increase/adjust generator output power gradually.
        # Apply the target output power
        ierr = psspy.change_gref(gen_bus_num, gen_id, gen_p_setpoint_pu)
        if ierr != 0:
            bp(
                f"[ERROR] Updating setpoint for Generator {gen_name} (ID = {gen_id}) at Bus {gen_bus_num}, ierr={ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                raise Exception("Error in GenUpdate function!")
            else:
                SystemExit(0)
        updated_action_status = 2

    # # Check if the generator is at the target power level
    # GenP = FetchChannelValue(int(BSPSSEPyGenRow["PELECChannel"].values[0]), debug_print=debug_print) * gen_mva_base

    if debug_print:
        bp(
            f"[DEBUG] Generator: {gen_name} - Current Power: {gen_p}, Target Power: {gen_p_setpoint} MW",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # If generator output power is within 1% of the target power, we consider the ramp-up phase to be complete, and we provide the generator with the reference value for Gref
    if abs(gen_p_setpoint - gen_p) / gen_p_setpoint <= 0.01:
        if use_gen_ramp_rate:
            if abs(gen_p_setpoint - gen_p) > gen_ramp_rate_per_sec:
                if debug_print:
                    bp(
                        f"[DEBUG] Generator: {gen_name} is still ramping up. (Current Power: {gen_p}, Target Power: {gen_p_setpoint} MW)",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                updated_action_status = 1
                return updated_action_status

        # Set the generator output real power to
        ierr = psspy.change_gref(gen_bus_num, gen_id, gen_p_setpoint_pu)

        if ierr != 0:
            bp(
                f"[ERROR] Error occured when setting generator: {gen_name} output real power to GenPSetPoint: {gen_p_setpoint}.System will exit.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                raise Exception("Error in GenUpdate function!")
            else:
                SystemExit(0)

        if debug_print:
            bp(
                f"[DEBUG] Successfully set generator: {gen_name} output real power to GenPSetPoint: {gen_p_setpoint}.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        bp(f"Generator: '{gen_name}' Set-point updated.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

        gen_row["BSPSSEPyStatus"] = 3
        gen_row["BSPSSEPyLastAction"] = "Update Set-point"
        gen_row["BSPSSEPyLastActionTime"] = t
        gen_row["BSPSSEPySimulationNotes"] = (
            f"Updated Set-point to {gen_p_setpoint}"
        )

        # Write the row back to the DataFrame
        bspssepy_gen.loc[bspssepy_gen["MCNAME"] == gen_name, :] = gen_row
        updated_action_status = 2

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
    return updated_action_status
