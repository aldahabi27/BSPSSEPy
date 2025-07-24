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
from .bspssepy_gen_funs import get_gen_info
from .bspssepy_trn_funs import get_trn_info
from .bspssepy_bus_funs import get_bus_info
from fun.bspssepy.app.app_helper_funs import bp
from .bspssepy_default_vars import bspssepy_default_vars_fun


async def get_load_info(
    load_keys: str | list[str],
    load: str | None = None,
    load_name: str | None = None,
    load_id: str | None = None,
    bspssepy_load: pd.DataFrame | None = None,
    debug_print: bool = False,
    app: App | None = None,
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
        bp(
            f"[DEBUG] Retrieving load info for load_keys: {load_keys}, load: {load}, LOADNAME: {load_name}, load_id: {load_id}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure load_keys is a list
    if isinstance(load_keys, str):
        load_keys = [load_keys]

    # Normalize strings to remove extra spaces
    load_keys = [key.strip() for key in load_keys]
    if isinstance(load, str) and load:
        load_name = load

    if load_name is not None and load_name:
        load_name = load_name.strip()

    # Separate PSSE and bspssepy_load keys
    valid_psse_keys = load_info_dict.keys()
    valid_bspssepy_keys = (
        [] if bspssepy_load is None else bspssepy_load.columns
    )

    # Add PSSE Keys needed for basic load operations
    _load_keys = ["ID", "LOADNAME"]
    _load_keys_psse = list(_load_keys)
    for key in load_keys:
        if key in valid_psse_keys and key not in _load_keys_psse:
            _load_keys_psse.append(key)

    if debug_print:
        bp(f"[DEBUG] Fetching PSSE data for keys: {_load_keys_psse}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure no duplicate columns are fetched from PSSE if bspssepy_load is provided
    if bspssepy_load is not None and not bspssepy_load.empty:
        # Remove overlapping keys from the PSSE fetch list
        valid_bspssepy_keys = [
            key for key in valid_bspssepy_keys if key not in _load_keys_psse
        ]

    if debug_print:
        bp(
            f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {valid_bspssepy_keys}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Fetch PSSE data for the required keys
    psse_data = {}
    for key in _load_keys_psse:
        psse_data[key] = await get_load_info_psse(
            key, debug_print=debug_print, app=app
        )

    # Combine PSSEData and bspssepy_trn (if provided) into a single DataFrame
    if bspssepy_load is not None and not bspssepy_load.empty:
        valid_bspssepy_load = bspssepy_load[valid_bspssepy_keys]
        psse_df = pd.DataFrame(psse_data)
        combined_data = pd.concat([psse_df, valid_bspssepy_load], axis=1)
    else:
        combined_data = pd.DataFrame(psse_data)

    if debug_print:
        bp(f"[DEBUG] Combined Data:\n{combined_data}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Filter CombinedData based on TrnName, FromBus, and ToBus
    if load_name and load_id:
        combined_data = combined_data[
            (combined_data["LOADNAME"].str.strip() == load_name.strip())
            & (combined_data["ID"].str.strip() == load_id.strip())
        ]
    elif load_name or load_id:
        id_key = "LOADNAME" if load_name else "ID"
        id_val = load_name.strip() if load_name else load_id.strip()

        combined_data = combined_data[
            combined_data[id_key].str.strip() == id_val
        ]

    if debug_print:
        bp(f"[DEBUG] Filtered Data:\n{combined_data}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Handle cases based on the number of BrnKeys
    if len(load_keys) == 1:
        key = load_keys[0]
        return (
            combined_data[key].iloc[0]
            if len(combined_data) == 1
            else combined_data[key]
        )
    else:
        return combined_data[load_keys]


async def get_load_info_psse(aload_string, debug_print=False, app=None):
    """
    Retrieves specific load information from PSSE.

    Parameters:
        aloadString (str): Requested information key.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        list or None: A list of the requested information if found, otherwise None.
    """
    if debug_print:
        bp(
            f"[DEBUG] Requested load information for aloadString: '{aload_string}'",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Validate aloadString
    if aload_string not in load_info_dict:
        bp(
            f"[ERROR] Invalid aloadString '{aload_string}'. Check load_info_dict for valid options.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    try:
        # Fetch data type for the key
        ierr, data_type = psspy.aloadtypes([aload_string])
        if ierr != 0:
            bp(
                f"[ERROR] Failed to fetch data type for aloadString '{aload_string}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        # Retrieve data based on type
        if data_type[0] == "I":
            ierr, data = psspy.aloadint(-1, 4, [aload_string])
        elif data_type[0] == "R":
            ierr, data = psspy.aloadreal(-1, 4, [aload_string])
        elif data_type[0] == "C":
            ierr, data = psspy.aloadchar(-1, 4, [aload_string])
        elif data_type[0] == "X":
            ierr, data = psspy.aloadcplx(-1, 4, [aload_string])
        else:
            bp(
                f"[ERROR] Unsupported data type '{data_type[0]}' for aloadString '{aload_string}'.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if ierr != 0:
            bp(
                f"[ERROR] Failed to retrieve data for aloadString '{aload_string}'. PSSE error code: {ierr}",
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

        if debug_print:
            bp(
                f"[DEBUG] Successfully retrieved data for '{aload_string}': {data}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
        return data

    except Exception as e:
        bp(
            f"[ERROR] Exception occurred while retrieving load data: {e}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def load_disable(
    t,
    bspssepy_load,
    load_name=None,
    load_id=None,
    debug_print=False,
    app=None,
):
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
        bp(
            f"[DEBUG] Starting loadDisable for LOADNAME: {load_name}, load_id: {load_id}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    default_int, default_real, default_char = bspssepy_default_vars_fun()

    load_row = await get_load_info(
        load_keys=["LOADNAME", "ID", "NUMBER", "STATUS"],
        load=load_name,
        load_id=load_id,
        bspssepy_load=bspssepy_load,
        debug_print=debug_print,
        app=app,
    )

    if load_row is None or len(load_row) == 0:
        bp(
            f"[ERROR] load with Name '{load_name}' or ID '{load_id}' not found.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    load_id = load_row["ID"].iloc[0]
    load_bus_number = int(load_row["NUMBER"].iloc[0])
    load_name = load_row["LOADNAME"].iloc[0]
    load_status = load_row["STATUS"].iloc[0]

    if debug_print:
        bp(
            f"[DEBUG] load_id: {load_id}, LOADNAME: {load_name}, loadBusNumber: {load_bus_number}, loadStatus: {load_status} extracted for disabling.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    if load_status != 1:
        bp(
            f"[INFO] load '{load_name} at Bus '{load_bus_number}' is already disabled.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0

    # Attempt to disable the load
    try:
        if debug_print:
            bp(
                f"[DEBUG] Attempting to disable load '{load_name}' at bus '{load_bus_number}'.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        ierr = psspy.load_chng_7(
            load_bus_number,
            load_id,
            [0] + [default_int] * 6,  # load status (disabled)
            [default_real] * 8,
            default_char,
            load_name,
        )

        if ierr != 0:
            bp(
                f"[ERROR] Failed to disable load '{load_name or load_id}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return ierr

        new_status = await get_load_info(
            "STATUS",
            load=load_name,
            load_id=load_id,
            debug_print=debug_print,
            app=app,
        )
        if not (bspssepy_load is None or bspssepy_load.empty):
            bspssepy_load.loc[
                (bspssepy_load["LOADNAME"] == load_name)
                & (bspssepy_load["ID"] == load_id),
                [
                    "BSPSSEPyStatus",
                    "BSPSSEPyLastAction",
                    "BSPSSEPyLastActionTime",
                    "BSPSSEPySimulationNotes",
                    "STATUS",
                ],
            ] = [
                "Disabled",
                "Disable",
                t,
                "load successfully disabled.",
                new_status,
            ]

        if debug_print:
            bp(
                f"[SUCCESS] load '{load_name or load_id}' successfully disabled. DataFrame updated.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        return ierr

    except KeyError as e:
        bp(f"[ERROR] Key error while disabling load: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    except Exception as e:
        bp(f"[ERROR] Unexpected error while disabling load: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def load_enable(
    t: int,
    bspssepy_load: pd.DataFrame,
    load_name: str | None = None,
    load_id: str | None = None,
    debug_print: bool | None = False,
    app: App | None = None,
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
        bp(
            f"[DEBUG] Starting loadEnable for LOADNAME: {load_name}, load_id: {load_id}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    default_int, default_real, default_char = bspssepy_default_vars_fun()

    load_row = await get_load_info(
        load_keys=["LOADNAME", "ID", "NUMBER", "STATUS"],
        load=load_name,
        load_id=load_id,
        bspssepy_load=bspssepy_load,
        debug_print=debug_print,
        app=app,
    )

    if load_row is None or len(load_row) == 0:
        bp(
            f"[ERROR] load with Name '{load_name}' or ID '{load_id}' not found.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    load_id = load_row["ID"].iloc[0]
    load_bus_num = int(load_row["NUMBER"].iloc[0])
    load_name = load_row["LOADNAME"].iloc[0]
    load_status = int(load_row["STATUS"].iloc[0])

    if debug_print:
        bp(
            f"[DEBUG] load_id: {load_id}, LOADNAME: {load_name}, loadBusNumber: {load_bus_num}, loadStatus: {load_status} extracted for enabling.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    if load_status != 0:
        bp(
            f"[INFO] load '{load_name} at Bus '{load_bus_num}' is already enabled.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0

    # Attempt to enable the load
    try:
        if debug_print:
            bp(
                f"[DEBUG] Attempting to enable load '{load_name}' at bus '{load_bus_num}'.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        ierr = psspy.load_chng_7(
            load_bus_num,
            load_id,
            [
                1,  # load status (enabled)
                default_int,
                default_int,
                default_int,
                default_int,
                default_int,
                default_int,
            ],
            [
                default_real,
                default_real,
                default_real,
                default_real,
                default_real,
                default_real,
                default_real,
                default_real,
            ],
            default_char,
            default_char,
        )

        if ierr != 0:
            bp(
                f"[ERROR] Failed to enable load '{load_name or load_id}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return ierr

        new_status = await get_load_info(
            "STATUS",
            load=load_name,
            load_id=load_id,
            debug_print=debug_print,
            app=app,
        )
        if not (bspssepy_load is None or bspssepy_load.empty):
            bspssepy_load.loc[
                (bspssepy_load["LOADNAME"] == load_name)
                & (bspssepy_load["ID"] == load_id),
                [
                    "BSPSSEPyStatus",
                    "BSPSSEPyLastAction",
                    "BSPSSEPyLastActionTime",
                    "BSPSSEPySimulationNotes",
                    "STATUS",
                ],
            ] = [
                "Enabled",
                "Enable",
                t,
                "load successfully enabled.",
                new_status,
            ]

        if debug_print:
            bp(
                f"[SUCCESS] load '{load_name or load_id}' successfully enabled. DataFrame updated.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Update online generators to compensate for the load
        for idx, gen_row in bspssepy_gen[
            bspssepy_gen["BSPSSEPyStatus"] == 3
        ].iterrows():
            gen_bus_num = gen_row["NUMBER"]
            gen_name = gen_row["MCNAME"]
            gen_id = gen_row["ID"]

            ierr, gen_mva_base = psspy.macdat(gen_bus_num, gen_id, "MBASE")

            gen_p_opf = gen_row["POPF"]
            LERPF = gen_row["LERPF"]

            # Fix: Extract a single value instead of a DataFrame
            eff_agc_alpha = bspssepy_agc.loc[
                bspssepy_agc["Gen Name"] == gen_name, "Alpha"
            ].values[0]

            LERPF = eff_agc_alpha if LERPF == -1 else LERPF

            if not gen_row["LoadEnabledResponse"]:
                continue

            # Fix: Await the coroutine to get the actual value
            eff_load = await get_load_info(
                "TOTALACT", load=load_name, debug_print=debug_print, app=app
            )

            await asyncio.sleep(app.async_print_delay if app else 0)

            gem_p_opf_pu = (
                eff_load.real * LERPF / gen_mva_base
            )  # ✅ Now works correctly

            from fun.bspssepy.sim.bspssepy_channels import fetch_channel_value

            # Fix: Remove .values[0] from PELECChannel access
            gen_p = (
                await fetch_channel_value(
                    int(gen_row["PELECChannel"]),
                    debug_print=debug_print,
                    app=app,
                )
                * gen_mva_base
            )

            if debug_print:
                bp(
                    f"[DEBUG] Using generator model ramp-rate for generator: {gen_name} - Target Power: {gen_p_opf} MW",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            # Apply the target output power
            ierr = psspy.increment_gref(gen_bus_num, gen_id, gem_p_opf_pu)

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

        return ierr

    except KeyError as e:
        bp(f"[ERROR] Key error while enabling load: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    except Exception as e:
        bp(f"[ERROR] Unexpected error while enabling load: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def new_load(
    load_id="ZZ",
    load_name=None,
    bspssepy_load=None,
    bus_name=None,
    bus_num=None,
    element_name=None,
    element_type=None,
    power_array=[1],
    use_from_bus=True,
    t=0,
    debug_print=False,
    app=None,
):
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
        bp("[ERROR] bspssepy_load DataFrame must be provided.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    if debug_print:
        bp(
            f"[DEBUG] Starting Newload with load_id: {load_id}, LOADNAME: {load_name}, BusName: {bus_name}, bus_num: {bus_num}, ElementName: {element_name}, ElementType: {element_type}, PowerArray: {power_array}, UseFromBus: {use_from_bus}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Determine bus location if an element is provided
    if bus_name:
        if debug_print:
            bp(f"[DEBUG] Resolving bus_num for BusName: {bus_name}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        bus_num = await get_bus_info(
            bus_keys="NUMBER",
            bus_name=bus_name,
            debug_print=debug_print,
            app=app,
        )
        if bus_num is None or not bus_num:
            bp(
                f"[ERROR] Bus '{bus_name}' must resolve to a bus_num.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    elif bus_num:
        if debug_print:
            bp(f"[DEBUG] Resolving BusName for bus_num: {bus_num}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        bus_name = await get_bus_info(
            bus_keys="NAME", bus_num=bus_num, debug_print=debug_print, app=app
        )
        if bus_name is None or not bus_name:
            bp(f"[ERROR] Bus '{bus_num}' must resolve to a BusName.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    if element_name and element_type:
        if debug_print:
            bp(
                f"[DEBUG] Determining bus location for ElementName: {element_name}, ElementType: {element_type}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
        if element_type.lower() in ["gen", "generator", "g"]:
            element_row = await get_gen_info(
                ["NUMBER", "NAME"],
                gen_name=element_name,
                debug_print=debug_print,
                app=app,
            )
            if not element_row.empty and element_row is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(element_row["NUMBER"].values[0])
                if not bus_name or bus_name == None:
                    bus_name = element_row["NAME"].values[0]
                load_id = "GL"  # Generator load
        elif element_type.lower() in [
            "twtf",
            "twtransformer",
            "twtran",
            "twtrans",
            "trn",
        ]:
            element_row = await get_trn_info(
                ["FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"],
                trn_name=element_name,
                debug_print=debug_print,
                app=app,
            )
            if not element_row.empty and element_row is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(
                        element_row["FROMNUMBER"].values[0]
                        if use_from_bus
                        else element_row["TONUMBER"].values[0]
                    )
                if not bus_name or bus_name == None:
                    bus_name = (
                        element_row["FROMNAME"].values[0]
                        if use_from_bus
                        else element_row["TONAME"].values[0]
                    )
                load_id = "TL"  # Transformer load
        elif element_type.lower() in ["branch", "line", "brn"]:
            element_row = await get_brn_info(
                ["FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"],
                brn_name=element_name,
                debug_print=debug_print,
                app=app,
            )
            if not element_row.empty and element_row is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(
                        element_row["FROMNUMBER"].values[0]
                        if use_from_bus
                        else element_row["TONUMBER"].values[0]
                    )
                if not bus_name or bus_name == None:
                    bus_name = (
                        element_row["FROMNAME"].values[0]
                        if use_from_bus
                        else element_row["TONAME"].values[0]
                    )
                load_id = "BL"  # Branch load
        elif element_type.lower() in ["load"]:
            element_row = await get_load_info(
                ["NUMBER", "NAME"],
                load_name=element_name,
                debug_print=debug_print,
                app=app,
            )
            if not element_row.empty and element_row is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(element_row["NUMBER"].values[0])
                if not bus_name or bus_name == None:
                    bus_name = element_row["NAME"].values[0]
                load_id = "LL"  # load tied to another load
        elif element_type.lower() in ["bus"]:
            element_row = await get_bus_info(
                ["NUMBER", "NAME"],
                bus_name=element_name,
                debug_print=debug_print,
                app=app,
            )
            if not element_row.empty and element_row is not None:
                if not bus_num or bus_num == None:
                    bus_num = int(element_row["NUMBER"].values[0])
                if not bus_name or bus_name == None:
                    bus_name = element_row["NAME"].values[0]
                load_id = "UL"  # load tied to a bus
        else:
            bp(
                f"[ERROR] Unsupported ElementType specified: {element_type}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if not bus_num or not bus_name:
            bp(
                f"[ERROR] Element '{element_name}' of type '{element_type}' not found.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
        if debug_print:
            bp(
                f"[DEBUG] Resolved bus_num: {bus_num}, BusName: {bus_name}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
    elif bus_name:
        if debug_print:
            bp(f"[DEBUG] Resolving bus_num for BusName: {bus_name}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        bus_num = await get_bus_info(
            bus_keys="NUMBER",
            bus_name=bus_name,
            debug_print=debug_print,
            app=app,
        )
        if bus_num is None or not bus_num:
            bp(
                f"[ERROR] Bus '{bus_name}' must resolve to a bus_num.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    elif bus_num:
        if debug_print:
            bp(f"[DEBUG] Resolving BusName for bus_num: {bus_num}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        bus_name = await get_bus_info(
            bus_keys="NAME", bus_num=bus_num, debug_print=debug_print, app=app
        )
        if bus_name is None or not bus_name:
            bp(f"[ERROR] Bus '{bus_num}' must resolve to a BusName.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    else:
        bp("[ERROR] Insufficient data to determine bus location.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Generate default LOADNAME if not provided
    if not load_name:
        load_name = f"CL{element_name or bus_name}"  # Customload
        if debug_print:
            bp(f"[DEBUG] Generated default LOADNAME: {load_name}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

    # Process PowerArray inputs
    default_int, default_real, default_char = bspssepy_default_vars_fun()
    pl, ql, ip, iq, yp, yq, pf = [default_real] * 6 + [None]

    if power_array:
        if len(power_array) >= 1:
            pl = power_array[0]
        if len(power_array) >= 2:
            ql = power_array[1]
        if len(power_array) >= 3:
            ip = power_array[2]
        if len(power_array) >= 4:
            iq = power_array[3]
        if len(power_array) >= 5:
            yp = power_array[4]
        if len(power_array) >= 6:
            yq = power_array[5]
        if len(power_array) >= 7:
            pf = power_array[6]
        if debug_print:
            bp(
                f"[DEBUG] Processed PowerArray: PL={pl}, QL={ql}, IP={ip}, IQ={iq}, YP={yp}, YQ={yq}, PowerFactor={pf}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

    ierr = psspy.load_data_7(
        int(bus_num),
        load_id,
        [0, default_int, default_int, default_int, 1, 0, 0],
        [pl, ql, ip, iq, yp, yq, default_real, default_real],
        default_char,
        load_name,
    )
    if ierr != 0:
        bp(
            f"[ERROR] Failed to create load '{load_name}' at bus '{bus_name}' (bus_num: {bus_num}).",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return ierr
    if debug_print:
        bp(
            f"[DEBUG] Successfully created load in PSSE: LOADNAME={load_name}, bus_num={bus_num}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Update bspssepy_load DataFrame
    new_row = {
        "ID": load_id,
        "LOADNAME": load_name,
        "NUMBER": bus_num,
        "NAME": bus_name,
        "STATUS": 1,
        "BSPSSEPyStatus_0": "Enabled",
        "BSPSSEPyStatus": "Enabled",
        "BSPSSEPyLastAction": "Newload",
        "BSPSSEPyLastActionTime": t,
        "BSPSSEPySimulationNotes": "New load added.",
        "BSPSSEPyTiedDeviceName": element_name if element_name else None,
        "BSPSSEPyTiedDeviceType": element_type if element_type else None,
    }
    bspssepy_load = pd.concat(
        [bspssepy_load, pd.DataFrame([new_row])], axis=0, ignore_index=True
    )
    if debug_print:
        bp(
            f"[DEBUG] New load '{load_name}' added successfully at bus '{bus_name}' (bus_num: {bus_num}). DataFrame updated.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    return bspssepy_load, ierr
