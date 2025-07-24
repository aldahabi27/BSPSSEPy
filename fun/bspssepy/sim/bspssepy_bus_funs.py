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
    bus_keys,  # The key(s) for the required information of the bus
    bus=None,  # Bus identifier --> could be BusName or bus_num (optional)
    bus_name=None,  # Bus Name (optional)
    bus_num=None,  # Bus Number (optional)
    bspssepy_bus=None,  # bspssepy_bus dataFrane containing BSPSSEPy extra
    # information associated with the Bus (optional)
    debug_print=False,  # Enable detailed debug output
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
        bp(
            f"[DEBUG] Retrieving bus info for BusKeys: {bus_keys}, Bus: {bus},"
            f"BusName: {bus_name}, bus_num: {bus_num}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure BusKeys is a list
    if isinstance(bus_keys, str):
        bus_keys = [bus_keys]

    # Normalize strings to remove extra spaces
    bus_keys = [key.strip() for key in bus_keys]
    if isinstance(bus, str) and bus:
        bus_name = bus
    elif bus:
        bus_num = bus

    if bus_name is not None and bus_name:
        bus_name = bus_name.strip()

    # Separate PSSE and bspssepy_bus keys
    valid_psse_keys = bus_info_dict.keys()
    valid_bspssepy_keys = [] if bspssepy_bus is None else bspssepy_bus.columns

    # Add PSSE Keys needed for basic Bus operations
    _bus_keys = ["NAME", "NUMBER"]
    _bus_keys_psse = list(_bus_keys)
    for key in bus_keys:
        if key in valid_psse_keys and key not in _bus_keys_psse:
            _bus_keys_psse.append(key)

    if debug_print:
        bp(f"[DEBUG] Fetching PSSE data for keys: {_bus_keys_psse}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure no duplicate columns are fetched from PSSE if bspssepy_brn is provided
    if bspssepy_bus is not None and not bspssepy_bus.empty:
        # Remove overlapping keys from the PSSE fetch list
        valid_bspssepy_keys = [
            key for key in valid_bspssepy_keys if key not in _bus_keys_psse
        ]

    if debug_print:
        bp(
            f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {valid_bspssepy_keys}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Fetch PSSE data for the required keys
    psse_data = {}
    for psse_key in _bus_keys_psse:
        psse_data[psse_key] = await get_bus_info_psse(
            psse_key, debug_print=debug_print, app=app
        )

    # Combine PSSEdata and bspssepy_trn (if provided) into a single dataFrame
    if bspssepy_bus is not None and not bspssepy_bus.empty:
        valid_bspssepy_trn = bspssepy_bus[valid_bspssepy_keys]
        psse_data = pd.DataFrame(psse_data)
        combined_data = pd.concat([psse_data, valid_bspssepy_trn], axis=1)
    else:
        combined_data = pd.DataFrame(psse_data)

    if debug_print:
        bp(f"[DEBUG] Combined data:\n{combined_data}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Filter Combineddata based on TrnName, FromBus, and ToBus
    if bus_name:
        combined_data = combined_data[
            combined_data["NAME"].str.strip() == bus_name
        ]
    elif bus_num:
        combined_data = combined_data[(combined_data["NUMBER"] == bus_num)]

    if debug_print:
        bp(f"[DEBUG] Filtered data:\n{combined_data}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Handle cases based on the number of BrnKeys
    if len(bus_keys) == 1:
        key = bus_keys[0]
        return (
            combined_data[key].iloc[0]
            if len(combined_data) == 1
            else combined_data[key]
        )
    else:
        return combined_data[bus_keys]


async def get_bus_info_psse(
    abus_string,  # Requested info string - Check available strings in bus_info_dict
    debug_print=False,  # Print debug information
    app=None,
):
    """
    Retrieves specific bus information from PSSE.

    Parameters:
        abusString (str): Requested information key.
        debug_print (bool, optional): Enable detailed debug output. Default is False.

    Returns:
        list or None: A list of the requested information if found, otherwise None.
    """
    if debug_print:
        bp(
            f"[DEBUG] Requested bus information for abusString: '{abus_string}'",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Validate abusString
    if abus_string not in bus_info_dict:
        bp(
            f"[ERROR] Invalid abusString '{abus_string}'. Check bus_info_dict for valid options.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    try:
        # Fetch data type for the key
        ierr, data_type = psspy.abustypes([abus_string])
        if ierr != 0:
            bp(
                f"[ERROR] Failed to fetch data type for abusString '{abus_string}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        # Retrieve data based on type
        if data_type[0] == "I":
            ierr, data = psspy.abusint(-1, 2, [abus_string])
        elif data_type[0] == "R":
            ierr, data = psspy.abusreal(-1, 2, [abus_string])
        elif data_type[0] == "C":
            ierr, data = psspy.abuschar(-1, 2, [abus_string])
        elif data_type[0] == "X":
            ierr, data = psspy.abuscplx(-1, 2, [abus_string])
        else:
            bp(
                f"[ERROR] Unsupported data type '{data_type[0]}' for abusString '{abus_string}'.",
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
                f"[ERROR] Failed to retrieve data for abusString '{abus_string}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if debug_print:
            bp(
                f"[DEBUG] Successfully retrieved data for '{abus_string}': {data}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        return data

    except Exception as e:
        bp(f"[ERROR] Exception occurred while retrieving data: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def bus_trip(
    t,
    bspssepy_bus=None,
    bus=None,
    bus_num=None,
    bus_name=None,
    debug_print=False,
    app=None,
):
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
        bp(
            f"[DEBUG] BusTrip called with inputs:\n"
            f"  Bus: {bus}\n"
            f"  BusName: {bus_name}\n"
            f"  bus_num: {bus_num}\n"
            f"  Simulation Time: {t}s\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Identify the bus row based on name or number
    if isinstance(bus, numbers.Number):
        bus_num = bus
    else:
        bus_name = bus

    # Resolve bus_num if BusName is given
    if bus_name:
        bus_num = await get_bus_info(
            "NUMBER",
            bus=bus_name,
            bspssepy_bus=bspssepy_bus,
            debug_print=debug_print,
            app=app,
        )
    elif not bus_num:
        bp("[ERROR] Either BusName or bus_num must be provided.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    bus_row = await get_bus_info(
        bus_keys=["NAME", "NUMBER", "TYPE"],
        bus=bus_num,
        bspssepy_bus=bspssepy_bus,
        debug_print=debug_print,
        app=app,
    )

    # Ensure the bus exists in the dataFrame
    if bus_row.empty:
        bp(
            f"[ERROR] Bus with Name '{bus_name}' or Number '{bus_num}' not found.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    bus_num = bus_row["NUMBER"].iloc[0]
    bus_name = bus_row["NAME"].iloc[0]
    bus_type = bus_row["TYPE"].iloc[0]

    # Debug message with resolved values
    if debug_print:
        bp(
            f"[DEBUG] Resolved Bus details:\n"
            f"  BusName: {bus_name}\n"
            f"  bus_num: {bus_num}\n"
            f"  BusType: {bus_type}\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Change bus status in PSSE to 4 (tripped)
    ierr = psspy.bus_chng_4(
        bus_num,
        0,
        [4, default_int, default_int, default_int],
        [
            default_real,
            default_real,
            default_real,
            default_real,
            default_real,
            default_real,
            default_real,
        ],
        default_char,
    )

    if ierr != 0:
        bp(
            f"[ERROR] Failed to trip bus with Number '{bus_num}'. PSSE error code: {ierr}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return ierr

    new_type = await get_bus_info(
        "TYPE", bus=bus_num, debug_print=debug_print, app=app
    )

    if not (bspssepy_bus is None or bspssepy_bus.empty):
        # Update the bspssepy_bus dataFrame to reflect the action
        bspssepy_bus.loc[
            (bspssepy_bus["NUMBER"] == bus_num)
            & (bspssepy_bus["NAME"] == bus_name),
            [
                "BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "TYPE",
            ],
        ] = ["Tripped", "Trip", t, "Bus successfully tripped.", new_type]

    if debug_print:
        bp(
            f"[SUCCESS] Bus with Number '{bus_num}', Name '{bus_name}' successfully tripped.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    return ierr


async def bus_close(
    t,
    bspssepy_bus=None,
    bus=None,
    bus_num=None,
    bus_name=None,
    debug_print=False,
    app=None,
):
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
        bp(
            f"[DEBUG] BusClose called with inputs:\n"
            f"  Bus: {bus}\n"
            f"  BusName: {bus_name}\n"
            f"  bus_num: {bus_num}\n"
            f"  Simulation Time: {t}s\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Identify the bus row based on name or number
    if isinstance(bus, numbers.Number):
        bus_num = bus
    else:
        bus_name = bus

    # Resolve bus_num if BusName is given
    if bus_name:
        bus_num = await get_bus_info(
            "NUMBER",
            bus=bus_name,
            bspssepy_bus=bspssepy_bus,
            debug_print=debug_print,
            app=app,
        )
    elif not bus_num:
        bp("[ERROR] Either BusName or bus_num must be provided.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    bus_row = await get_bus_info(
        bus_keys=["NAME", "NUMBER", "TYPE", "BSPSSEPyType_0"],
        bus=bus_num,
        bspssepy_bus=bspssepy_bus,
        debug_print=debug_print,
        app=app,
    )

    # Ensure the bus exists in the dataFrame
    if bus_row.empty:
        bp(
            f"[ERROR] Bus with Name '{bus_name}' or Number '{bus_num}' not found.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    bus_num = bus_row["NUMBER"].iloc[0]
    # bus_num = BusRow["NUMBER"].values[0]
    bus_name = bus_row["NAME"].iloc[0]
    bus_type = bus_row["TYPE"].iloc[0]
    bus_type_0 = bus_row["BSPSSEPyType_0"].iloc[0]

    # Debug message with resolved values
    if debug_print:
        bp(
            f"[DEBUG] Resolved Bus details:\n"
            f"  BusName: {bus_name}\n"
            f"  bus_num: {bus_num}\n"
            f"  BusType: {bus_type}\n"
            f"  BusType_0: {bus_type_0}\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Change bus status in PSSE to 4 (tripped)
    ierr = psspy.bus_chng_4(
        bus_num,
        0,
        [bus_type_0, default_int, default_int, default_int],
        [
            default_real,
            default_real,
            default_real,
            default_real,
            default_real,
            default_real,
            default_real,
        ],
        default_char,
    )

    new_type = await get_bus_info(
        "TYPE",
        bus=bus_num,
        bspssepy_bus=bspssepy_bus,
        debug_print=debug_print,
        app=app,
    )

    if ierr != 0:
        bp(
            f"[ERROR] Failed to close bus with Number '{bus_num}'. PSSE error code: {ierr}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return ierr

    if not (bspssepy_bus is None or bspssepy_bus.empty):
        # Update the bspssepy_bus dataFrame to reflect the action
        bspssepy_bus.loc[
            (bspssepy_bus["NUMBER"] == bus_num)
            & (bspssepy_bus["NAME"] == bus_name),
            [
                "BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "TYPE",
            ],
        ] = ["Closed", "Close", t, "Bus successfully Closed.", new_type]

    if debug_print:
        bp(
            f"[SUCCESS] Bus with Number '{bus_num}', Name '{bus_name}' successfully closed.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    return ierr


async def change_bus_type(
    t,
    new_bus_type,
    bspssepy_bus=None,
    bus=None,
    bus_num=None,
    bus_name=None,
    debug_print=False,
    app=None,
):
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
        bp(
            f"[DEBUG] BusClose called with inputs:\n"
            f"  BusType: {new_bus_type}\n"
            f"  Bus: {bus}\n"
            f"  BusName: {bus_name}\n"
            f"  bus_num: {bus_num}\n"
            f"  Simulation Time: {t}s\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Identify the bus row based on name or number
    if isinstance(bus, numbers.Number):
        bus_num = bus
    else:
        bus_name = bus

    # Resolve bus_num if BusName is given
    if bus_name:
        bus_num = await get_bus_info(
            "NUMBER",
            bus=bus_name,
            bspssepy_bus=bspssepy_bus,
            debug_print=debug_print,
            app=app,
        )
    elif not bus_num:
        bp("[ERROR] Either BusName or bus_num must be provided.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    bus_row = await get_bus_info(
        bus_keys=["NAME", "NUMBER", "TYPE", "BSPSSEPyType_0"],
        bus=bus_num,
        bspssepy_bus=bspssepy_bus,
        debug_print=debug_print,
        app=app,
    )

    # Ensure the bus exists in the dataFrame
    if bus_row.empty:
        bp(
            f"[ERROR] Bus with Name '{bus_name}' or Number '{bus_num}' not found.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    bus_num = bus_row["NUMBER"].iloc[0]
    # bus_num = BusRow["NUMBER"].values[0]
    bus_name = bus_row["NAME"].iloc[0]
    bus_type = bus_row["TYPE"].iloc[0]
    bus_type_0 = bus_row["BSPSSEPyType_0"].iloc[0]

    # Debug message with resolved values
    if debug_print:
        bp(
            f"[DEBUG] Resolved Bus details:\n"
            f"  BusName: {bus_name}\n"
            f"  bus_num: {bus_num}\n"
            f"  BusType: {bus_type}\n"
            f"  BusType_0: {bus_type_0}\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Change bus status in PSSE to 4 (tripped)
    ierr = psspy.bus_chng_4(
        bus_num,
        0,
        [new_bus_type, default_int, default_int, default_int],
        [
            default_real,
            default_real,
            default_real,
            default_real,
            default_real,
            default_real,
            default_real,
        ],
        default_char,
    )

    new_type = await get_bus_info(
        "TYPE", bus=bus_num, debug_print=debug_print, app=app
    )

    if ierr != 0:
        bp(
            f"[ERROR] Failed to close bus with Number '{bus_num}'. PSSE error code: {ierr}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return ierr

    if not (bspssepy_bus is None or bspssepy_bus.empty):
        # Update the bspssepy_bus dataFrame to reflect the action
        bspssepy_bus.loc[
            (bspssepy_bus["NUMBER"] == bus_num)
            & (bspssepy_bus["NAME"] == bus_name),
            [
                "BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "TYPE",
            ],
        ] = (
            [
                "Closed",
                "ModifyType",
                t,
                "BusType modified successfully.",
                new_type,
            ]
            if new_type != 4
            else [
                "Tripped",
                "ModifyType",
                t,
                "BusType modified successfully.",
                new_type,
            ]
        )

    if debug_print:
        bp(
            f"[SUCCESS] Bus with Number '{bus_num}', Name '{bus_name}' successfully modified.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    return ierr
