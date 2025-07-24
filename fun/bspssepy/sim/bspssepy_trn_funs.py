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


async def get_trn_info(
    trn_keys,  # The key(s) for the required information of the Trn
    trn_name=None,  # Trn Name (optional)
    from_bus=None,  # From Bus Number or Name (optional)
    to_bus=None,  # To Bus Number or Name (optional)
    bspssepy_trn=None,  # bspssepy_trn DataFrame containing BSPSSEBy extra information associated with the Trn (optional)
    debug_print=False,  # Enable detailed debug output
    app=None,
):
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
        bp(
            f"[DEBUG] Retrieving Two-Winding Transformer info for TrnKeys: {trn_keys}, TrnName: {trn_name}, FromBus: {from_bus}, ToBus: {to_bus}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure TrnKeys is a list
    if isinstance(trn_keys, str):
        trn_keys = [trn_keys]

    # Normalize strings to remove extra spaces
    trn_keys = [key.strip() for key in trn_keys]
    if trn_name:
        trn_name = trn_name.strip()
    if not isinstance(from_bus, (int, float)) and from_bus:
        from_bus = from_bus.strip()
        from_bus_key = "FROMNAME"
    elif isinstance(from_bus, (int, float)) and from_bus:
        from_bus_key = "FROMNUMBER"

    if not isinstance(to_bus, (int, float)) and to_bus:
        to_bus = to_bus.strip()
        to_bus_key = "TONAME"
    elif isinstance(to_bus, (int, float)) and to_bus:
        to_bus_key = "TONUMBER"

    # Separate PSSE and bspssepy_trn keys
    valid_psse_keys = trn_info_dict.keys()
    valid_bspssepy_keys = [] if bspssepy_trn is None else bspssepy_trn.columns

    # Add PSSE Keys needed for basic branch operations
    _trn_keys = ["XFRNAME", "FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"]
    _trn_keys_psse = list(_trn_keys)
    for key in trn_keys:
        if key in valid_psse_keys and key not in _trn_keys_psse:
            _trn_keys_psse.append(key)

    if debug_print:
        bp(f"[DEBUG] Fetching PSSE data for keys: {_trn_keys_psse}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure no duplicate columns are fetched from PSSE if bspssepy_brn is provided
    if bspssepy_trn is not None and not bspssepy_trn.empty:
        # Remove overlapping keys from the PSSE fetch list
        valid_bspssepy_keys = [
            key for key in valid_bspssepy_keys if key not in _trn_keys_psse
        ]

    if debug_print:
        bp(
            f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {valid_bspssepy_keys}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Fetch PSSE data for the required keys
    psse_data = {}
    for psse_key in _trn_keys_psse:
        psse_data[psse_key] = await get_trn_info_psse(
            psse_key, debug_print=debug_print, app=app
        )

    # Combine PSSEData and bspssepy_trn (if provided) into a single DataFrame
    if bspssepy_trn is not None and not bspssepy_trn.empty:
        valid_bspssepy_trn = bspssepy_trn[valid_bspssepy_keys]
        psse_data_df = pd.DataFrame(psse_data)
        combined_data = pd.concat([psse_data_df, valid_bspssepy_trn], axis=1)
    else:
        combined_data = pd.DataFrame(psse_data)

    if debug_print:
        bp(f"[DEBUG] Combined Data:\n{combined_data}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Filter CombinedData based on TrnName, FromBus, and ToBus
    if trn_name:
        combined_data = combined_data[
            combined_data["XFRNAME"].str.strip() == trn_name
        ]
    elif from_bus and to_bus:
        if isinstance(from_bus, (int, float)):
            from_bus_key = "FROMNUMBER"
        else:
            from_bus_key = "FROMNAME"
        if isinstance(to_bus, (int, float)):
            to_bus_key = "TONUMBER"
        else:
            to_bus_key = "TONAME"

        combined_data = combined_data[
            (combined_data[from_bus_key] == from_bus)
            & (combined_data[to_bus_key] == to_bus)
        ]

    if debug_print:
        bp(f"[DEBUG] Filtered Data:\n{combined_data}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Handle cases based on the number of BrnKeys
    if len(trn_keys) == 1:
        Key = trn_keys[0]
        return (
            combined_data[Key].iloc[0]
            if len(combined_data) == 1
            else combined_data[Key]
        )
    else:
        return combined_data[trn_keys]


async def get_trn_info_psse(
    atrn_string,  # Requested Info string - Check available strings in trn_info_dict
    trn_entry=1,  # 1 entry for each Trn, 2 --> two-way entry (each Trn in both directions)
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
        bp(
            f"[DEBUG] Requested Trn information for atrnString: '{atrn_string}'",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        bp(f"[DEBUG] TrnEntry: {trn_entry}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Check if atrnString exists in trn_info_dict
    if atrn_string not in trn_info_dict:
        bp(
            f"[ERROR] Invalid atrnString '{atrn_string}'. Check trn_info_dict for valid options.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Determine subsystem and entry flag
    atrn_sid = -1  # Assume entire system unless specified
    atrn_flag = 2  # Default flag for all Two-Winding Transformers

    # Set up the query parameters
    parameters = {
        "sid": atrn_sid,
        "flag": atrn_flag,
        "entry": trn_entry,
        "string": [atrn_string],
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
    ierr, data_type = psspy.atrntypes([atrn_string])
    if ierr != 0:
        bp(
            f"[ERROR] Failed to fetch data type for atrnString '{atrn_string}'. PSSE error code: {ierr}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Retrieve data based on the type
    try:
        if data_type[0] == "I":  # Integer data
            ierr, data = psspy.atrnint(**parameters)
        elif data_type[0] == "R":  # Real data
            ierr, data = psspy.atrnreal(**parameters)
        elif data_type[0] == "C":  # Character data
            ierr, data = psspy.atrnchar(**parameters)
        elif data_type[0] == "X":  # Complex data
            ierr, data = psspy.atrncplx(**parameters)
        else:
            bp(
                f"[ERROR] Unsupported data type '{data_type[0]}' for atrnString '{atrn_string}'.",
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
                f"[ERROR] Failed to retrieve data for atrnString '{atrn_string}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if debug_print:
            bp(
                f"[DEBUG] Successfully retrieved data for '{atrn_string}': {data}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
        return data

    except Exception as e:
        bp(
            f"[ERROR] Exception occurred while retrieving TW-trn data: {e}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def trn_trip(
    t,
    bspssepy_trn=None,
    trn_id=None,
    trn_name=None,
    trn_from_bus=None,
    trn_to_bus=None,
    debug_print=False,
    app=None,
):
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
        bp(
            f"[DEBUG] TrnTrip called with inputs:\n"
            f"  TrnID: {trn_id}\n"
            f"  TrnName: {trn_name}\n"
            f"  FromBus: {trn_from_bus}\n"
            f"  ToBus: {trn_to_bus}\n"
            f"  Simulation Time: {t}s\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Resolve TrnName if only bus info is provided
    if not trn_name and (trn_from_bus and trn_to_bus):
        trn_name = await get_trn_info(
            trn_keys=["XFRNAME"],
            from_bus=trn_from_bus,
            to_bus=trn_to_bus,
            bspssepy_trn=bspssepy_trn,
            debug_print=debug_print,
            app=app,
        )
        if not trn_name:
            bp(
                f"[ERROR] Could not identify Trn between buses {trn_from_bus} and {trn_to_bus}.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

    # Fetch Trn details
    trn_row = await get_trn_info(
        trn_keys=["FROMNUMBER", "TONUMBER", "ID", "STATUS", "XFRNAME"],
        trn_name=trn_name,
        bspssepy_trn=bspssepy_trn,
        debug_print=debug_print,
        app=app,
    )

    if trn_row is None or len(trn_row) == 0:
        bp(
            f"[ERROR] Trn not found for ID={trn_id}, Name={trn_name}, "
            f"FromBus={trn_from_bus}, ToBus={trn_to_bus}.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Extract Trn information
    trn_from_bus = trn_row["FROMNUMBER"].iloc[0]
    trn_to_bus = trn_row["TONUMBER"].iloc[0]
    trn_id = trn_row["ID"].iloc[0]
    trn_name = trn_row["XFRNAME"].iloc[0]
    trn_status = trn_row["STATUS"].iloc[0]

    # Debug message with resolved values
    if debug_print:
        bp(
            f"[DEBUG] Resolved Trn details:\n"
            f"  TrnID: {trn_id}\n"
            f"  TrnName: {trn_name}\n"
            f"  FromBus: {trn_from_bus}\n"
            f"  ToBus: {trn_to_bus}\n"
            f"  Status: {'Closed' if trn_status == 1 else 'Tripped'}\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Check if the Trn is already tripped
    if trn_status != 1:
        bp(f"[INFO] Trn '{trn_name}' is already tripped.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0

    # Attempt to trip the Trn
    try:
        if debug_print:
            bp(
                f"[DEBUG] Attempting to trip Two-Winding Transformer '{trn_name}' between buses {trn_from_bus} and {trn_to_bus}.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        ierr = psspy.dist_branch_trip(trn_from_bus, trn_to_bus, trn_id)

        if ierr != 0:
            bp(
                f"[ERROR] Failed to trip Trn '{trn_name}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return ierr

        # Ensure proper matching for FromBus and ToBus in bspssepy_trn
        from_bus_condition = bspssepy_trn["FROMNUMBER"].apply(str) == str(
            trn_from_bus
        )
        to_bus_condition = bspssepy_trn["TONUMBER"].apply(str) == str(
            trn_to_bus
        )
        id_condition = bspssepy_trn["ID"] == trn_id

        new_status = await get_trn_info(
            "STATUS", trn_name=trn_name, debug_print=debug_print, app=app
        )

        if not (bspssepy_trn is None or bspssepy_trn.empty):
            # Update the bspssepy_trn DataFrame
            bspssepy_trn.loc[
                from_bus_condition & to_bus_condition & id_condition,
                [
                    "BSPSSEPyStatus",
                    "BSPSSEPyLastAction",
                    "BSPSSEPyLastActionTime",
                    "BSPSSEPySimulationNotes",
                    "STATUS",
                ],
            ] = [
                "Tripped",
                "Trip",
                t,
                "TW-Trn successfully tripped.",
                new_status,
            ]

        if debug_print:
            bp(
                f"[SUCCESS] Successfully tripped Two-Winding Transformer '{trn_name}'. Updated bspssepy_trn DataFrame.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        return ierr

    except KeyError as e:
        bp(f"[ERROR] Missing key during TrnTrip operation: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    except Exception as e:
        bp(f"[ERROR] Unexpected error during TrnTrip: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def trn_close(
    t,
    bspssepy_trn=None,
    bspssepy_bus=None,
    trn_id=None,
    trn_name=None,
    trn_from_bus=None,
    trn_to_bus=None,
    called_by_gen=False,
    debug_print=False,
    app=None,
):
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
        bp(
            f"[DEBUG] TrnClose called with inputs:\n"
            f"  TrnID: {trn_id}\n"
            f"  TrnName: {trn_name}\n"
            f"  FromBus: {trn_from_bus}\n"
            f"  ToBus: {trn_to_bus}\n"
            f"  Simulation Time: {t}s\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Resolve TrnName if only bus info is provided
    if not trn_name and (trn_from_bus and trn_to_bus):
        trn_name = await get_trn_info(
            trn_keys=["XFRNAME"],
            from_bus=trn_from_bus,
            to_bus=trn_to_bus,
            bspssepy_trn=bspssepy_trn,
            debug_print=debug_print,
            app=app,
        )
        if not trn_name:
            bp(
                f"[ERROR] Could not identify Trn between buses {trn_from_bus} and {trn_to_bus}.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

    # Fetch Trn details
    trn_row = await get_trn_info(
        trn_keys=[
            "FROMNUMBER",
            "TONUMBER",
            "ID",
            "STATUS",
            "XFRNAME",
            "GenControlled",
        ],
        trn_name=trn_name,
        bspssepy_trn=bspssepy_trn,
        debug_print=debug_print,
        app=app,
    )

    if trn_row is None or len(trn_row) == 0:
        bp(
            f"[ERROR] Trn not found for ID={trn_id}, Name={trn_name}, FromBus={trn_from_bus}, ToBus={trn_to_bus}.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Extract Trn information
    trn_from_bus = trn_row["FROMNUMBER"].iloc[0]
    trn_to_bus = trn_row["TONUMBER"].iloc[0]
    trn_id = trn_row["ID"].iloc[0]
    trn_name = trn_row["XFRNAME"].iloc[0]
    trn_status = trn_row["STATUS"].iloc[0]
    trn_gen_controlled = trn_row["GenControlled"].values[0]

    if debug_print:
        bp(
            f"[DEBUG] Resolved Trn details:\n"
            f"  TrnID: {trn_id}\n"
            f"  TrnName: {trn_name}\n"
            f"  FromBus: {trn_from_bus}\n"
            f"  ToBus: {trn_to_bus}\n"
            f"  Status: {'Closed' if trn_status == 1 else 'Tripped'}\n"
            f"  GenControlled: {trn_gen_controlled}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Check if the Trn is already closed
    if trn_status == 1:
        bp(f"[INFO] Trn '{trn_name}' is already closed.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0

    # Ensure both buses are operational
    if (called_by_gen & trn_gen_controlled) or not trn_gen_controlled:
        try:

            from_bus_type = await get_bus_info(
                bus_keys="TYPE",
                bus_num=trn_from_bus,
                debug_print=debug_print,
                app=app,
            )
            to_bus_type = await get_bus_info(
                bus_keys="TYPE",
                bus_num=trn_to_bus,
                debug_print=debug_print,
                app=app,
            )

            if from_bus_type == 4:  # Tripped
                if debug_print:
                    bp(
                        f"[DEBUG] FromBus {trn_from_bus} is tripped. Attempting to close it.",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = await bus_close(
                    t,
                    bspssepy_bus=bspssepy_bus,
                    bus_num=trn_from_bus,
                    debug_print=debug_print,
                    app=app,
                )
                if ierr != 0:
                    bp(
                        f"[ERROR] Failed to close FromBus {trn_from_bus}. Aborting Trn close.",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    return ierr

            if to_bus_type == 4:  # Tripped
                if debug_print:
                    bp(
                        f"[DEBUG] ToBus {trn_to_bus} is tripped. Attempting to close it.",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = await bus_close(
                    t,
                    bspssepy_bus=bspssepy_bus,
                    bus_num=trn_to_bus,
                    debug_print=debug_print,
                    app=app,
                )
                if ierr != 0:
                    bp(
                        f"[ERROR] Failed to close ToBus {trn_to_bus}. Aborting Trn close.",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    return ierr

            if debug_print:
                bp(
                    f"[DEBUG] Attempting to close Two-Winding Transformer '{trn_name}' between buses {trn_from_bus} and {trn_to_bus}.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            # Attempt to close the Trn
            ierr = psspy.dist_branch_close(trn_from_bus, trn_to_bus, trn_id)
            if ierr != 0:
                bp(
                    f"[ERROR] Failed to close Trn '{trn_name}'. PSSE error code: {ierr}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
                return ierr

            # Update the bspssepy_trn DataFrame
            from_bus_condition = bspssepy_trn["FROMNUMBER"].apply(str) == str(
                trn_from_bus
            )
            to_bus_condition = bspssepy_trn["TONUMBER"].apply(str) == str(
                trn_to_bus
            )
            id_condition = bspssepy_trn["ID"] == trn_id

            new_status = await get_trn_info(
                "STATUS", trn_name=trn_name, debug_print=debug_print, app=app
            )

            if not (bspssepy_trn is None or bspssepy_trn.empty):
                bspssepy_trn.loc[
                    from_bus_condition & to_bus_condition & id_condition,
                    [
                        "BSPSSEPyStatus",
                        "BSPSSEPyLastAction",
                        "BSPSSEPyLastActionTime",
                        "BSPSSEPySimulationNotes",
                        "STATUS",
                    ],
                ] = [
                    "Closed",
                    "Close",
                    t,
                    "Trn successfully closed.",
                    new_status,
                ]

            if debug_print:
                bp(
                    f"[SUCCESS] Successfully closed Trn '{trn_name}'. Updated bspssepy_trn DataFrame.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            return ierr

        except Exception as e:
            bp(f"[ERROR] Unexpected error during TrnClose: {e}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

    else:
        bp(
            f"[ERROR] This transformer is tied to a generator. Don't attempt to close it manually. It can be controlled through GenEnable function to model generator phases.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return -999
