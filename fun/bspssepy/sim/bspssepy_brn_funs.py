# BSPSSEPy Branch Functions
# This Python module contains all 'Branch' related functions for the BSPSSEPy framework:
#
# 1. GetBranchInfo: Retrieves specific information about branches based on user-specified keys, either from PSSE or bspssepy_brn DataFrame.
#    - Handles cases for single/multiple keys and specific/all branches.
#
# 2. GetBranchInfoPSSE: Fetches branch-related data directly from PSSE using the PSSE library. This function is called by GetBranchInfo.
#
# 3. BranchTrip: Trips a branch based on its ID, name, or bus connections and updates the bspssepy_brn DataFrame.
#
# 4. BranchClose: Closes a branch based on its ID, name, or bus connections and updates the bspssepy_brn DataFrame.
#
# This module ensures dynamic interaction with PSSE for real-time data, while allowing extended tracking and simulation-specific metadata updates through the bspssepy_brn DataFrame.
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
from .bspssepy_bus_funs import *
from fun.bspssepy.bspssepy_dict import *
from fun.bspssepy.app.app_helper_funs import bp
import asyncio

# from fun.bspssepy.bspssepy_funs_dict import *


async def get_brn_info(
    brn_keys,  # The key(s) for the required information of the Branch
    brn_name=None,  # Branch Name (optional)
    from_bus=None,  # From Bus Number or Name (optional)
    to_bus=None,  # To Bus Number or Name (optional)
    bspssepy_brn=None,  # bspssepy_brn DataFrame containing BSPSSEPy extra information associated with the branch (optional)
    debug_print=False,
    app=None,
):  # Enable detailed debug output
    """
    Retrieves information about branches based on the specified keys.

    This function fetches the requested data from both PSSE and the bspssepy_brn DataFrame, providing flexibility
    for dynamic and pre-stored data retrieval. Handles multiple cases based on the input parameters:

    Case 1: Single key for a specific branch -> Returns a single value (str, int, float, or list).
    Case 2: Multiple keys for a specific branch -> Returns a pandas Series with the requested keys.
    Case 3: Single key for all branches -> Returns a pandas Series containing values for all branches.
    Case 4: Multiple keys for all branches -> Returns a pandas Series for all branches with the requested keys.

    Arguments:
        BrnKeys (str or list of str): The key(s) for the required information. Valid keys include PSSE keys and
                                         bspssepy_brn columns.
        BranchName (str, optional): Name of the branch to filter. Defaults to None.
        FromBus (str or int, optional): "From Bus" Number or Name. Defaults to None.
        ToBus (str or int, optional): "To Bus" Number or Name. Defaults to None.
        bspssepy_brn (pd.DataFrame, optional): The bspssepy_brn DataFrame containing branch data. Defaults to None.
        debug_print (bool, optional): Enable detailed debug output. Defaults to False.

    Returns:
        Depending on the input case:
            - Case 1: Single value corresponding to the requested key for a specific branch.
            - Case 2: pandas Series with the requested keys for a specific branch.
            - Case 3: pandas Series with values for all branches for the requested key.
            - Case 4: pandas Series for all branches with the requested keys.

    Notes:
        - Input strings (e.g., BrnKeys, BranchName, FromBus, ToBus) are normalized by stripping extra spaces.
        - The function combines PSSE and bspssepy_brn data if both are available for comprehensive results.
        - Filtering logic is applied based on BranchName, FromBus, and ToBus.
    """
    # Debug logging
    if debug_print:
        bp(
            f"[DEBUG] Retrieving branch info for BrnKeys: {brn_keys}, BranchName: {brn_name}, FromBus: {from_bus}, ToBus: {to_bus}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure BrnKeys is a list
    if isinstance(brn_keys, str):
        brn_keys = [brn_keys]

    # Normalize strings to remove extra spaces
    brn_keys = [key.strip() for key in brn_keys]
    if brn_name:
        brn_name = brn_name.strip()
    if isinstance(from_bus, str) and from_bus:
        from_bus = from_bus.strip()
        from_bus_key = "FROMNAME"
    else:
        from_bus_key = "FROMNUMBER"

    if isinstance(to_bus, str) and to_bus:
        to_bus = to_bus.strip()
        to_bus_key = "TONAME"
    else:
        to_bus_key = "TONUMBER"

    # Separate PSSE and bspssepy_brn keys
    valid_psse_keys = brn_info_dict.keys()
    valid_bspssepy_keys = [] if bspssepy_brn is None else bspssepy_brn.columns

    # Add PSSE Keys needed for basic branch operations
    _brn_keys = ["BRANCHNAME", "FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME"]
    _brn_keys_psse = list(_brn_keys)
    for key in brn_keys:
        if key in valid_psse_keys and key not in _brn_keys_psse:
            _brn_keys_psse.append(key)

    if debug_print:
        bp(f"[DEBUG] Fetching PSSE data for keys: {_brn_keys_psse}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Ensure no duplicate columns are fetched from PSSE if bspssepy_brn is provided
    if bspssepy_brn is not None and not bspssepy_brn.empty:
        # Remove overlapping keys from the PSSE fetch list
        valid_bspssepy_keys = [
            key for key in valid_bspssepy_keys if key not in _brn_keys_psse
        ]

    if debug_print:
        bp(
            f"[DEBUG] Adjusted BSPSSEPy keys to fetch: {valid_bspssepy_keys}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Fetch PSSE data for the required keys
    psse_data = {}
    for psse_key in _brn_keys_psse:
        psse_data[psse_key] = await get_brn_info_psse(
            psse_key, debug_print=debug_print, app=app
        )

    # Combine PSSEData and bspssepy_brn (if provided) into a single DataFrame
    if bspssepy_brn is not None and not bspssepy_brn.empty:
        valid_bspssepy_brn = bspssepy_brn[valid_bspssepy_keys]
        psse_data = pd.DataFrame(psse_data)
        combined_data = pd.concat([psse_data, valid_bspssepy_brn], axis=1)
    else:
        combined_data = pd.DataFrame(psse_data)

    if debug_print:
        bp(f"[DEBUG] Combined Data:\n{combined_data}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Filter CombinedData based on BranchName, FromBus, and ToBus
    if brn_name:
        combined_data = combined_data[
            combined_data["BRANCHNAME"].str.strip() == brn_name
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
    if len(brn_keys) == 1:
        key = brn_keys[0]
        return (
            combined_data[key].iloc[0]
            if len(combined_data) == 1
            else combined_data[key]
        )
    else:
        return combined_data[brn_keys]


async def get_brn_info_psse(
    abrn_string,  # Requested Info string - Check available strings in brn_info_dict
    branch_entry=1,  # 1 entry for each branch, 2 --> two-way entry (each branch in both directions)
    debug_print=False,  # Print debug information
    app=None,
):
    """
    This function returns the requested information about the branch of interest.
    If no branch is specified, it will return the information about all branches.

    Arguments:
        abrnString: str
            Requested Info string - Check available strings in brn_info_dict.
        BranchEntry: int
            1 entry for each branch, 2 --> two-way entry (each branch in both directions).
        # BranchName: str
        #     Branch Name (optional).
        # FromBus: str or int
        #     From Bus Number or Name (optional).
        # ToBus: str or int
        #     To Bus Number or Name (optional).
        debug_print: bool
            Print debug information (default = False).

    Returns:
        list or None:
            A list of the requested information if found, otherwise None.

    Notes:
        # - If no branch is specified, information about all branches is returned.
        # - To select a branch, use either BranchName or (FromBus and ToBus). If multiple branches
        #   connect the two buses, use the branch name.
    """

    if debug_print:
        bp(
            f"[DEBUG] Requested branch information for abrnString: '{abrn_string}'",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        bp(
            f"[DEBUG] BranchEntry: {branch_entry}", app=app
        )  # , BranchName: {BranchName}, FromBus: {FromBus}, ToBus: {ToBus}")
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Check if abrnString exists in brn_info_dict
    if abrn_string not in brn_info_dict:
        bp(
            f"[ERROR] Invalid abrnString '{abrn_string}'. Check brn_info_dict for valid options.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Determine subsystem and entry flag
    abrnSID = -1  # Assume entire system unless specified
    abrnFlag = 2  # Default flag for all branches

    # Set up the query parameters
    parameters = {
        "sid": abrnSID,
        "flag": abrnFlag,
        "entry": branch_entry,
        "string": [abrn_string],
    }

    # # Filter branches based on provided parameters
    # if BranchName:
    #     parameters['BRANCHNAME'] = BranchName
    #     if debug_print:
    #         bp(f"[DEBUG] Filtering branches by BranchName: {BranchName}")
    # elif FromBus and ToBus:
    #     parameters['FROMBUS'] = FromBus
    #     parameters['TO'] = ToBus
    #     if debug_print:
    #         bp(f"[DEBUG] Filtering branches by FromBus: {FromBus} and ToBus: {ToBus}")

    # Fetch the data type for the requested string
    ierr, data_type = psspy.abrntypes([abrn_string])
    if ierr != 0:
        bp(
            f"[ERROR] Failed to fetch data type for abrnString '{abrn_string}'. PSSE error code: {ierr}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Retrieve data based on the type
    try:
        if data_type[0] == "I":  # Integer data
            ierr, data = psspy.abrnint(**parameters)
        elif data_type[0] == "R":  # Real data
            ierr, data = psspy.abrnreal(**parameters)
        elif data_type[0] == "C":  # Character data
            ierr, data = psspy.abrnchar(**parameters)
        elif data_type[0] == "X":  # Complex data
            ierr, data = psspy.abrncplx(**parameters)
        else:
            bp(
                f"[ERROR] Unsupported data type '{data_type[0]}' for abrnString '{abrn_string}'.",
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
                f"[ERROR] Failed to retrieve data for abrnString '{abrn_string}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

        if debug_print:
            bp(
                f"[DEBUG] Successfully retrieved data for '{abrn_string}': {data[0]}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
        return data

    except Exception as e:
        bp(f"[ERROR] Exception occurred while retrieving data: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def brn_trip(
    t,
    bspssepy_brn,
    brn_id=None,
    brn_name=None,
    brn_from_bus=None,
    brn_to_bus=None,
    debug_print=False,
    app=None,
):
    """
    Trips a branch based on its ID, name, or bus connection and updates extended info columns.

    Arguments:
        t: float
            Current simulation time.
        bspssepy_brn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy branch data.
        BranchID: str or int
            The unique ID of the branch (optional).
        BranchName: str
            The name of the branch (optional).
        BranchFromBus: int or str
            The "from" bus number or name (optional).
        BranchToBus: int or str
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
            f"[DEBUG] BranchTrip called with inputs:\n"
            f"  BranchID: {brn_id}\n"
            f"  BranchName: {brn_name}\n"
            f"  FromBus: {brn_from_bus}\n"
            f"  ToBus: {brn_to_bus}\n"
            f"  Simulation Time: {t}s\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Resolve BranchName if only bus info is provided
    if not brn_name and (brn_from_bus and brn_to_bus):
        brn_name = await get_brn_info(
            brn_keys=["BRANCHNAME"],
            from_bus=brn_from_bus,
            to_bus=brn_to_bus,
            bspssepy_brn=bspssepy_brn,
            debug_print=debug_print,
            app=app,
        )
        if not brn_name:
            bp(
                f"[ERROR] Could not identify branch between buses {brn_from_bus} and {brn_to_bus}.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
    # Fetch branch details
    brn_row = await get_brn_info(
        brn_keys=["FROMNUMBER", "TONUMBER", "ID", "STATUS", "BRANCHNAME"],
        brn_name=brn_name,
        bspssepy_brn=bspssepy_brn,
        debug_print=debug_print,
        app=app,
    )

    if brn_row is None or len(brn_row) == 0:
        bp(
            f"[ERROR] Branch not found for ID={brn_id}, Name={brn_name}, "
            f"FromBus={brn_from_bus}, ToBus={brn_to_bus}.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Extract branch information
    brn_from_bus = brn_row["FROMNUMBER"].iloc[0]
    brn_to_bus = brn_row["TONUMBER"].iloc[0]
    brn_id = brn_row["ID"].iloc[0]
    brn_name = brn_row["BRANCHNAME"].iloc[0]
    brn_status = int(brn_row["STATUS"].iloc[0])

    # Debug message with resolved values
    if debug_print:
        bp(
            f"[DEBUG] Resolved branch details:\n"
            f"  BranchID: {brn_id}\n"
            f"  BranchName: {brn_name}\n"
            f"  FromBus: {brn_from_bus}\n"
            f"  ToBus: {brn_to_bus}\n"
            f"  Status: {'Closed' if brn_status == 1 else 'Tripped'}\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Check if the branch is already tripped
    if brn_status != 1:
        bp(f"[INFO] Branch '{brn_name}' is already tripped.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0

    # Attempt to trip the branch
    try:
        if debug_print:
            bp(
                f"[DEBUG] Attempting to trip branch '{brn_name}' between buses {brn_from_bus} and {brn_to_bus}.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        ierr = psspy.dist_branch_trip(brn_from_bus, brn_to_bus, brn_id)

        if ierr != 0:
            bp(
                f"[ERROR] Failed to trip branch '{brn_name}'. PSSE error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return ierr

        # Ensure proper matching for FromBus and ToBus in bspssepy_brn
        from_bus_condition = bspssepy_brn["FROMNUMBER"].apply(str) == str(
            brn_from_bus
        )
        to_bus_condition = bspssepy_brn["TONUMBER"].apply(str) == str(
            brn_to_bus
        )
        id_condition = bspssepy_brn["ID"] == brn_id

        new_status = await get_brn_info(
            "STATUS", brn_name=brn_name, debug_print=debug_print, app=app
        )

        if not (bspssepy_brn is None or bspssepy_brn.empty):
            # Update the bspssepy_brn DataFrame
            bspssepy_brn.loc[
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
                "Branch successfully tripped.",
                new_status,
            ]

        if debug_print:
            bp(
                f"[SUCCESS] Successfully tripped branch '{brn_name}'. Updated bspssepy_brn DataFrame.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)

        return ierr

    except KeyError as e:
        bp(f"[ERROR] Missing key during BranchTrip operation: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None
    except Exception as e:
        bp(f"[ERROR] Unexpected error during BranchTrip: {e}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None


async def brn_close(
    t,
    bspssepy_brn=None,
    bspssepy_bus=None,
    brn_id=None,
    brn_name=None,
    brn_from_bus=None,
    brn_to_bus=None,
    called_by_gen=False,
    debug_print=False,
    app=None,
):
    """
    Closes a branch based on its ID, name, or bus connection and updates extended info columns.

    Arguments:
        t: float
            Current simulation time.
        bspssepy_brn: pd.DataFrame
            The pandas DataFrame containing BSPSSEPy branch data.
        BranchID: str or int
            The unique ID of the branch (optional).
        BranchName: str
            The name of the branch (optional).
        BranchFromBus: int or str
            The "from" bus number or name (optional).
        BranchToBus: int or str
            The "to" bus number or name (optional).
        debug_print: bool
            Enable detailed debug output (default = False).

    Returns:
        int:
            ierr: The status of the action applied (ierr = 0 --> success!).
    """
    if debug_print:
        bp(
            f"[DEBUG] BranchClose called with inputs:\n"
            f"  BranchID: {brn_id}\n"
            f"  BranchName: {brn_name}\n"
            f"  FromBus: {brn_from_bus}\n"
            f"  ToBus: {brn_to_bus}\n"
            f"  Simulation Time: {t}s\n",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Resolve BranchName if only bus info is provided
    if not brn_name and (brn_from_bus and brn_to_bus):
        brn_name = await get_brn_info(
            brn_keys=["BRANCHNAME"],
            from_bus=brn_from_bus,
            to_bus=brn_to_bus,
            bspssepy_brn=bspssepy_brn,
            debug_print=debug_print,
            app=app,
        )
        if not brn_name:
            bp(
                f"[ERROR] Could not identify branch between buses {brn_from_bus} and {brn_to_bus}.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

    # Fetch branch details
    brn_row = await get_brn_info(
        brn_keys=[
            "FROMNUMBER",
            "TONUMBER",
            "ID",
            "STATUS",
            "BRANCHNAME",
            "GenControlled",
        ],
        brn_name=brn_name,
        bspssepy_brn=bspssepy_brn,
        debug_print=debug_print,
        app=app,
    )

    if brn_row is None or len(brn_row) == 0:
        bp(
            f"[ERROR] Branch not found for ID={brn_id}, Name={brn_name}, "
            f"FromBus={brn_from_bus}, ToBus={brn_to_bus}.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return None

    # Extract branch information
    brn_from_bus = int(brn_row["FROMNUMBER"].iloc[0])
    brn_to_bus = int(brn_row["TONUMBER"].iloc[0])
    brn_id = brn_row["ID"].iloc[0]
    brn_name = brn_row["BRANCHNAME"].iloc[0]
    brn_status = int(brn_row["STATUS"].iloc[0])
    brn_gen_controlled = brn_row["GenControlled"].values[0]

    if debug_print:
        bp(
            f"[DEBUG] Resolved branch details:\n"
            f"  BranchID: {brn_id}\n"
            f"  BranchName: {brn_name}\n"
            f"  FromBus: {brn_from_bus}\n"
            f"  ToBus: {brn_to_bus}\n"
            f"  Status: {'Closed' if brn_status == 1 else 'Tripped'}\n"
            f"  GenControlled: {brn_gen_controlled}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Check if the branch is already closed
    if brn_status == 1:
        bp(f"[INFO] Branch '{brn_name}' is already closed.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        return 0

    # Ensure both buses are operational
    if (called_by_gen & brn_gen_controlled) or not brn_gen_controlled:
        try:
            from_bus_type = await get_bus_info(
                bus_keys="TYPE",
                bus_num=brn_from_bus,
                debug_print=debug_print,
                app=app,
            )
            to_bus_type = await get_bus_info(
                bus_keys="TYPE",
                bus_num=brn_to_bus,
                debug_print=debug_print,
                app=app,
            )

            if from_bus_type == 4:  # Tripped
                if debug_print:
                    bp(
                        f"[DEBUG] FromBus {brn_from_bus} is tripped. Attempting to close it.",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = await bus_close(
                    t,
                    bus_num=brn_from_bus,
                    bspssepy_bus=bspssepy_bus,
                    debug_print=debug_print,
                    app=app,
                )
                if ierr != 0:
                    bp(
                        f"[ERROR] Failed to close FromBus {brn_to_bus}. Aborting Trn close.",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    return ierr

            if to_bus_type == 4:  # Tripped
                if debug_print:
                    bp(
                        f"[DEBUG] ToBus {brn_to_bus} is tripped. Attempting to close it.",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = await bus_close(
                    t,
                    bus_num=brn_to_bus,
                    bspssepy_bus=bspssepy_bus,
                    debug_print=debug_print,
                    app=app,
                )
                if ierr != 0:
                    bp(
                        f"[ERROR] Failed to close ToBus {brn_to_bus}. Aborting Trn close.",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    return ierr

            if debug_print:
                bp(
                    f"[DEBUG] Attempting to close branch '{brn_name}' between buses {brn_from_bus} and {brn_to_bus}.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)

            ierr = psspy.dist_branch_close(brn_from_bus, brn_to_bus, brn_id)

            if ierr != 0:
                bp(
                    f"[ERROR] Failed to close branch '{brn_name}'. PSSE error code: {ierr}",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
                return ierr

            new_status = await get_brn_info(
                "STATUS",
                brn_name=brn_name,
                debug_print=debug_print,
                app=app,
            )

            # Ensure proper matching for FromBus and ToBus in bspssepy_brn
            from_bus_condition = bspssepy_brn["FROMNUMBER"].apply(str) == str(
                brn_from_bus
            )
            to_bus_condition = bspssepy_brn["TONUMBER"].apply(str) == str(
                brn_to_bus
            )
            id_condition = bspssepy_brn["ID"] == brn_id

            if not (bspssepy_brn is None or bspssepy_brn.empty):
                # Update the bspssepy_brn DataFrame
                bspssepy_brn.loc[
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
                    "Branch successfully closed.",
                    new_status,
                ]

            if debug_print:
                bp(
                    f"[SUCCESS] Successfully closed branch '{brn_name}'. Updated bspssepy_brn DataFrame.",
                    app=app,
                )
                await asyncio.sleep(app.async_print_delay if app else 0)
            return ierr

        except KeyError as e:
            bp(
                f"[ERROR] Missing key during BranchClose operation: {e}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None
        except Exception as e:
            bp(f"[ERROR] Unexpected error during BranchClose: {e}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            return None

    else:
        bp(
            f"[ERROR] This branch is tied to a generator. Don't attempt to close it manually. It can be controlled through GenEnable function to model generator phases.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        return -999
