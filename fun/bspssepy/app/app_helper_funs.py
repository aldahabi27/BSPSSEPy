"""This module contains helper functions for the BSPSSEPyApp GUI."""

from __future__ import annotations

import os

# from pathlib import Path
from rich.text import Text
from textual.app import App

# from textual import events
# from textual.widgets import Tree, DataTable
from textual.widgets import DataTable
import pandas as pd
import asyncio  # Used for async operations

# import time
import psse3601  # noqa: F401

# pyright: reportMissingImports=false
import psspy  # noqa: F401 pylint: disable=import-error
from fun.bspssepy.app.bspssepy_print import bspssepy_print as bp


async def get_app_dfs(
    app: App,  # the app handle
    initialize: (
        bool | None
    ) = False,  # If initialize is true, this will return
    # the DFs as if the simulation is just
    # starting (not sure if needed,
    # but will see)
):
    """
    This function will return all dataframes needed for the GUI Tables.
    Then, the returned DFs can be compared with the "displayed" tables
    and update the changes only to have faster GUI updates.

    Parameters:
        app (App): The app handle to BSPSSEPyApp
        initialize (bool, default = False): To indicate if the generated DFs
                                            are at the beginning of the
                                            simulation (reset all stuff to
                                            zero/default values - i.e. Actions
                                            status --> did not start yet)
    """

    if app is None:
        return

    round_digit = 3
    debug_print = app.debug_checkbox.value

    # Debugging information
    if debug_print:
        bp(
            "[DEBUG] Running get_app_dfs" f"with initialize = {initialize}",
            app=app,
        )

    if debug_print:
        bp("Generating shortcuts to simulation dataframes", app=app)

    # Check if the simulation has started (i.e., if `app.bspssepy` exists)
    same_sav_file = False
    if hasattr(app, "bspssepy") and app.bspssepy is not None:
        if (
            str(app.bspssepy.config.sav_file).lower().strip()
            == app.sav_file_path.lower().strip()
        ):
            same_sav_file = True

    # If the simulation has not started, use empty DataFrames
    if not same_sav_file:
        bp(
            "[INFO] New SAV File selected. Attempting to run a quick analysis"
            " to update the Tables - please wait..",
            app=app,
        )

        # pylint: disable=import-outside-toplevel
        from fun.bspssepy.app.bspssepy_app_run import run_simulation

        await run_simulation(app=app, dummy_run=True)
        await asyncio.sleep(app.async_print_delay if app else 0)

    # Create a shortcut reference
    bspssepy_sequence = app.bspssepy.sim.config.bspssepy_sequence
    bspssepy_brn = app.bspssepy.sim.bspssepy_brn
    bspssepy_bus = app.bspssepy.sim.bspssepy_bus
    bspssepy_load = app.bspssepy.sim.bspssepy_load
    bspssepy_trn = app.bspssepy.sim.bspssepy_trn
    bspssepy_gen = app.bspssepy.sim.bspssepy_gen
    bspssepy_agc = app.bspssepy.sim.bspssepy_agc
    bspssepy_ibr = app.bspssepy.sim.bspssepy_ibr

    if debug_print:
        bp("Shortcut to simulation dataframes acquired", app=app)

    # Define a function to map Action Status to emojis
    def status_to_emoji(status):
        if status == 0:
            return " 🔴 "  # Not started
        elif status == 1:
            return " ⏳ "  # Running/Loading (sand watch)
        elif status == 2:
            return " ✅ "  # Completed (green check)
        elif status == -999:
            return "⚠︎ "  # Skipped
        else:
            return " ☠️ "  # Unexpected status (error)

    def action_time_min_sec(action_time, in_sec=False):
        """
        Converts an action time in minutes to a formatted string with
        both minutes and seconds.

        If the seconds value is a whole number, it is displayed as an
        integer without decimals.

        Parameters:
            action_time (float | int): The action time in minutes.

        Returns:
            str: Formatted string in the format "X min (Ys)".
        """
        if in_sec:
            action_time = action_time / 60  # Convert to Minutes first

        total_sec = action_time * 60  # Convert to seconds

        # If seconds are whole (integer), display as int
        if total_sec.is_integer():
            sec_formatted = int(total_sec)
        else:
            sec_formatted = round(total_sec, 1)

        return f"{round(action_time, round_digit)} min ({sec_formatted}s)"

    # Define the progress_df DataFrame with mapped columns
    progress_df = pd.DataFrame(
        {
            # Initially all actions are not started
            "Progress": bspssepy_sequence["Action Status"].apply(
                status_to_emoji
            ),
            # All set to zero for now
            "Control Sequence": bspssepy_sequence["Control Sequence"],
            # Mapped from bspssepy_sequence
            "Device Type": bspssepy_sequence["Device Type"],
            # Mapped from bspssepy_sequence
            "ID Type": bspssepy_sequence["Identification Type"],
            # Mapped from bspssepy_sequence
            "ID Value": bspssepy_sequence["Identification Value"],
            # Mapped from bspssepy_sequence
            "Action Type": bspssepy_sequence["Action Type"],
            # Mapped from bspssepy_sequence
            "Action Time": bspssepy_sequence["Action Time"].apply(
                action_time_min_sec
            ),
            "Start Time": bspssepy_sequence["Start Time"].apply(
                lambda x: action_time_min_sec(x, in_sec=True)
            ),
            "End Time": bspssepy_sequence["End Time"].apply(
                lambda x: action_time_min_sec(x, in_sec=True)
            ),
            # Mapped from bspssepy_sequence
            "Action Status": bspssepy_sequence["Action Status"],
        }
    )

    agc_df = bspssepy_agc
    agc_df["Alpha"] = agc_df["Alpha"].apply(lambda x: round(x, round_digit))
    agc_df["ΔPᴳ"] = agc_df["ΔPᴳ"].apply(lambda x: round(x, round_digit))
    agc_df["Δf (Hz)"] = agc_df["Δf (Hz)"].apply(
        lambda x: round(x, round_digit)
    )
    agc_df["Δf' (Hz/s)"] = agc_df["Δf' (Hz/s)"].apply(
        lambda x: round(x, round_digit)
    )

    # this code was moved to bspssepy_meas_update.py

    # Fetch all required channel values asynchronously
    # (
    #     pelec_values,
    #     pmech_values,
    #     qelec_values,
    #     gref_values,
    #     vref_values,
    # ) = await fetch_gen_ch_val(bspssepy_gen, debug_print, app)
    # # Fetch the MVA base for each generator
    # mva_base_list = []
    # for idx, gen_row in bspssepy_gen.iterrows():
    #     gen_id = gen_row["ID"]
    #     bus_num = gen_row["NUMBER"]

    #     # Get the base MVA value
    #     ierr, gen_mva_base = psspy.macdat(bus_num, gen_id, "MBASE")

    #     if ierr == 0:
    #         if debug_print:
    #             bp(
    #                 f"[DEBUG] Retrieved MVA Base for Generator at Bus {bus_num}"
    #                 f", ID {gen_id}: {gen_mva_base} MVA",
    #                 app=app,
    #             )
    #             await asyncio.sleep(app.async_print_delay if app else 0)
    #     else:
    #         bp(
    #             f"[ERROR] Could not retrieve MVA Base for Generator at Bus"
    #             f"{bus_num}, ID {gen_id}. Error code: {ierr}",
    #             app=app,
    #         )
    #         await asyncio.sleep(app.async_print_delay if app else 0)

    #     mva_base_list.append(gen_mva_base)

    # # System_MVA_BASE = psspy.get_sbase()
    # # Convert PU to MW/MVar for each generator
    # pelec_mw = [
    #     round(pe * mb, round_digit)
    #     for pe, mb in zip(pelec_values, [100] * len(pelec_values))
    # ]
    # pelec_pu = [round(pe, round_digit) for pe in pelec_values]

    # pmech_mw = [
    #     round(pm * mb, round_digit)
    #     for pm, mb in zip(pmech_values, mva_base_list)
    # ]
    # pmech_pu = [round(pm, round_digit) for pm in pmech_values]

    # qelec_mvar = [
    #     round(qe * mb, round_digit)
    #     for qe, mb in zip(qelec_values, [100] * len(pelec_values))
    # ]
    # qelec_pu = [round(qe, round_digit) for qe in qelec_values]

    # # Handle GREF scaling (assuming it follows the same rule as power)
    # gref_mw = [
    #     round(gr * mb, round_digit)
    #     for gr, mb in zip(gref_values, mva_base_list)
    # ]
    # gref_pu = [round(gr, round_digit) for gr in gref_values]

    # # Voltage remains in PU
    # vref_pu = [round(vr, round_digit) for vr in vref_values]

    # Create the DataFrame with formatted values
    GenDF = pd.DataFrame(
        {
            "Gen Name": bspssepy_gen["MCNAME"],
            "Bus #": bspssepy_gen["NUMBER"],
            "Bus Name": bspssepy_gen["NAME"],
            "Δf": bspssepy_gen["freq"].apply(lambda x: round(x, round_digit)),
            "Pᴱ MW": bspssepy_gen["p_elec"].apply(
                lambda x: round(x, round_digit)
            ),
            "Pᴹ MW": bspssepy_gen["p_mech"].apply(
                lambda x: round(x, round_digit)
            ),
            "Qᴱ MVar": bspssepy_gen["q_elec"].apply(
                lambda x: round(x, round_digit)
            ),
            "Gᴿᴱꟳ MW": bspssepy_gen["g_ref"].apply(
                lambda x: round(x, round_digit)
            ),
            "Vᴿᴱꟳ (p.u.)": bspssepy_gen["v_ref"].apply(
                lambda x: round(x, round_digit)
            ),
        }
    )

    # pylint: disable=import-outside-toplevel
    from fun.bspssepy.sim.bspssepy_load_funs import get_load_info

    load_df_temp = await get_load_info(
        [
            "LOADNAME",
            "NUMBER",
            "NAME",
            "MVAACT",
            "ILACT",
            "YLACT",
            "LDGNACT",
            "STATUS",
        ],
        debug_print=debug_print,
        app=app,
    )

    # Create the DataFrame
    round_digit = 3
    load_df = pd.DataFrame(
        {
            "load Name": load_df_temp["LOADNAME"],
            "Bus #": load_df_temp["NUMBER"],
            "Bus Name": load_df_temp["NAME"],
            "Power Array [PL, QL, IP, IQ, YP, YQ, PG, QG]": load_df_temp.apply(
                lambda row: [
                    round(row["MVAACT"].real, round_digit),
                    round(row["MVAACT"].imag, round_digit),
                    round(row["ILACT"].real, round_digit),
                    round(row["ILACT"].imag, round_digit),
                    round(row["YLACT"].real, round_digit),
                    round(row["YLACT"].imag, round_digit),
                    round(row["LDGNACT"].real, round_digit),
                    round(row["LDGNACT"].imag, round_digit),
                ],
                axis=1,
            ),
            "Status": load_df_temp["STATUS"],
        }
    )

    from fun.bspssepy.sim.bspssepy_bus_funs import get_bus_info

    bus_df_temp = await get_bus_info(
        ["NUMBER", "NAME", "TYPE"], debug_print=debug_print, app=app
    )
    bus_status = await get_bus_info(
        ["BSPSSEPyStatus"],
        bspssepy_bus=bspssepy_bus,
        debug_print=debug_print,
        app=app,
    )

    bus_df = pd.DataFrame(
        {
            "Bus #": bus_df_temp["NUMBER"],
            "Bus Name": bus_df_temp["NAME"],
            "Type": bus_df_temp["TYPE"],
            "Status": bus_status,
        }
    )

    brn_df = pd.DataFrame(
        {
            "Branch Name": bspssepy_brn["BRANCHNAME"],
            "From Bus #": bspssepy_brn["FROMNUMBER"],
            "To Bus #": bspssepy_brn["TONUMBER"],
            "From Bus Name": bspssepy_brn["FROMNAME"],
            "To Bus Name": bspssepy_brn["TONAME"],
            "Status": bspssepy_brn["STATUS"],
        }
    )

    trn_df = pd.DataFrame(
        {
            "Trans. Name": bspssepy_trn["XFRNAME"],
            "From Bus #": bspssepy_trn["FROMNUMBER"],
            "To Bus #": bspssepy_trn["TONUMBER"],
            "From Bus Name": bspssepy_trn["FROMNAME"],
            "To Bus Name": bspssepy_trn["TONAME"],
            "Status": bspssepy_trn["STATUS"],
        }
    )

    ibr_df = bspssepy_ibr

    df = {
        "Progress": progress_df,
        "AGC": agc_df,
        "Generator": GenDF,
        "load": load_df,
        "Bus": bus_df,
        "Branch": brn_df,
        "Transformer": trn_df,
        "IBR": ibr_df,
    }

    return df


async def update_bspssepy_app_gui(
    app: App, reset_tables: bool | None = False
):

    if reset_tables:
        app.progress_table.clear(columns=True)
        app.agc_table.clear(columns=True)
        app.gen_table.clear(columns=True)
        app.load_table.clear(columns=True)
        app.bus_table.clear(columns=True)
        app.brn_table.clear(columns=True)
        app.trn_table.clear(columns=True)
        app.ibr_table.clear(columns=True)

        app.progress_table.loading = True
        app.agc_table.loading = True
        app.gen_table.loading = True
        app.load_table.loading = True
        app.bus_table.loading = True
        app.brn_table.loading = True
        app.trn_table.loading = True
        app.ibr_table.loading = True
        await asyncio.sleep(0)

    dfs = await get_app_dfs(app=app)

    # Apply only the changed values instead of resetting everything
    update_gui_tables(app, dfs)
    # app.refresh()
    # await asyncio.sleep(0)

    # bp("[INFO] GUI Tables updated with new simulation data.", app=app)

    # # Loop through all tables and reset them dynamically
    # for TableName, TableInfo in Tables.items():
    #     bp(f"[INFO] Resetting {TableName} table...", app=app)

    #     BSPSSEPyAppResetTable(
    #         BSPSSEPyDataFrame=DataFrames[TableName],
    #         TableCol=TableInfo["columns"],
    #         app=app,
    #         appTable=TableInfo["AppTable"],
    #         UseconfigOnly=False
    #     )
    # await asyncio.sleep(app.async_print_delay if app else 0)

    # Final Debugging Information
    # bp("[INFO] All tables have been reset successfully.", app=app)
    # await asyncio.sleep(app.async_print_delay if app else 0)

    if app.debug_checkbox.value:
        bp("[DEBUG] BSPSSEPyApp tables initialized.", app=app)
        # await asyncio.sleep(app.async_print_delay if app else 0)
    app.progress_table.loading = False
    app.agc_table.loading = False
    app.gen_table.loading = False
    app.load_table.loading = False
    app.bus_table.loading = False
    app.brn_table.loading = False
    app.trn_table.loading = False
    app.ibr_table.loading = False
    await asyncio.sleep(0)

    app.run_button.disabled = False


# def bp(Message, app=None, type = None):
#     """
#     Prints messages to the details_text_area in the app if available.
#     Falls back to printing in the terminal if no app is provided.

#     This function automatically handles async execution using `call_later`
#     when inside the GUI, so you don't have to use `await` explicitly.

#     Parameters:
#         Message (str): The message to print.
#         app (BSPSSEPyApp, optional): The Textual app instance (default is None).
#         # type (optional): ["d","debug"] --> will check if app.debug_checkbox.value is true, then will be displayed, otherwise skip
#     """
#     if app:
#         # debug_print = app.debug_checkbox.value

#         # if check if Message is a string
#         app.call_later(append_to_details_text_area, app.details_text_area, Message)
#     else:
#         print(Message)  # ✅ Fallback to terminal output when no GUI is available

# def BSPSSEPyAppResetTables(
#         # TableName: str | None = None,
#         app: App | None = None,
#         UseconfigOnly: bool | None = False,
# ) -> None:
#     """ This function will initialize BSPSSEPyApp Tables. This function is called when all info needed is "collected"/"built" (after simInit is run).

#     Future plan:
#         Add a functionality to update the tables (or some of them) when SAV file is selected before the Run starts.
#     """

#     app.progress_table_col = ["Progrss", "Control Sequence", "Device Type", "ID Type", "ID Value", "Action Type", "Action Time", "Action Status"]
#     app.agc_table_col = ["Gen Name", "Alpha", "ΔPᴳ"]
#     app.gen_table_col = ["Gen Name", "Bus #", "Bus Name", "Δf", "Pᴱ", "Pᴹ", "Qᴱ", "Gᴿᴱꟳ", "Vᴿᴱꟳ"]
#     app.load_table_col = ["load Name", "Bus #", "Bus Name", "Power Array", "Status"]
#     app.bus_table_col = ["Bus #", "Bus Name", "Status"]
#     app.brn_table_col = ["Branch Name", "Bus #", "Bus Name", "Status"]
#     app.trn_table_col = ["Trans. Name", "Bus #", "Bus Name", "Status"]


def get_df_from_gui_tables(app: App) -> dict:
    """
    Extracts current data from the GUI tables and returns them as pandas DataFrames.

    Parameters:
        app (App): The Textual app instance.

    Returns:
        dict: A dictionary where keys are table names and values are pandas DataFrames.
    """
    debug_print = app.debug_checkbox.value

    tables = {
        "Progress": app.progress_table,
        "AGC": app.agc_table,
        "Generator": app.gen_table,
        "load": app.load_table,
        "Bus": app.bus_table,
        "Branch": app.brn_table,
        "Transformer": app.trn_table,
        "IBR": app.ibr_table,
    }

    gui_df = {}

    for table_name, table in tables.items():
        if table:
            col_names = [col.label.plain for col in table.columns.values()]

            # ✅ Extract row data using `get_row(row_key)`
            row_data = []
            for row_key in table.rows.keys():  # Iterate over row keys
                row_cells = table.get_row(
                    row_key
                )  # Fetch the row's cell data
                row_data.append([cell for cell in row_cells])  # Extract text

            # ✅ Handle case where table is empty
            if (not col_names or not row_data) and debug_print:
                bp(f"[DEBUG] Table '{table_name}' is empty.", app=app)

            gui_df[table_name] = pd.DataFrame(row_data, columns=col_names)
    return gui_df


def compare_df(df1: pd.DataFrame, df2: pd.DataFrame) -> dict:
    """
    Compares two DataFrames and returns a dictionary of changes.

    Parameters:
        df1 (pd.DataFrame): The first DataFrame (old/current GUI data).
        df2 (pd.DataFrame): The second DataFrame (new data from simulation).

    Returns:
        dict:
            - "changes": List of tuples (row_index, column_name, old_value, new_value) for modified cells.
            - "reset_required": Boolean indicating if table dimensions or column names don't match.
    """
    changes = []

    # ✅ Check if dimensions OR column names are different
    reset_required = (df1.shape != df2.shape) or (
        list(df1.columns) != list(df2.columns)
    )

    if reset_required:
        return {"changes": [], "reset_required": True}

    # ✅ Compare only if column names and shape match
    for row in range(len(df1)):
        for col in df1.columns:
            if str(df1.at[row, col]) != str(
                df2.at[row, col]
            ):  # Convert to string for comparison
                changes.append((row, col, df1.at[row, col], df2.at[row, col]))

    return {"changes": changes, "reset_required": False}


def update_gui_tables(app: App, df: dict):
    """
    Updates GUI tables by comparing current GUI data with new DataFrames and applying only changes.
    If a table is initially empty, has different dimensions, or different columns, it gets fully reset.

    Parameters:
        app (App): The Textual app instance.
        DataFrames (dict): The new DataFrames from get_app_dfs.
    """

    debug_print = app.debug_checkbox.value

    current_gui_df = get_df_from_gui_tables(app)

    tables = {
        "Progress": app.progress_table,
        "AGC": app.agc_table,
        "Generator": app.gen_table,
        "load": app.load_table,
        "Bus": app.bus_table,
        "Branch": app.brn_table,
        "Transformer": app.trn_table,
        "IBR": app.ibr_table,
    }

    for table_name, new_df in df.items():
        if table_name in current_gui_df:

            current_df = current_gui_df[table_name]
            comparison_result = compare_df(current_df, new_df)

            table: DataTable = tables[table_name]

            # Get row and column mappings from keys
            row_keys = list(table.rows.keys())  # Extract row keys
            col_keys = {
                col.label.plain: col.key for col in table.columns.values()
            }  # Map column names to keys

            # if TableName == "Transformer":
            #     bp("Transformer Table Update Details:\n"
            #             f"CurrentDF: {CurrentDF}\n"
            #             f"NewDF: {NewDF}\n"
            #             f"ComparisonResult: {ComparisonResult}\n"
            #             f"RowKeys: {RowKeys}\n"
            #             f"ColKeys: {ColKeys}\n"
            #             )

            if comparison_result["reset_required"]:
                # Reset table if needed
                if debug_print:
                    bp(
                        f"[INFO] Resetting table {table_name} due to column or shape mismatch.",
                        app=app,
                    )
                table.clear(columns=True)

                # Add new columns
                for col in new_df.columns:
                    table.add_column(col, width=None)
                # Add new rows
                for _, row in new_df.iterrows():
                    table.add_row(
                        *[Text(str(cell), justify="center") for cell in row]
                    )

            else:

                # Apply only changed values with correct row and column keys
                for (
                    row_idx,
                    col_name,
                    old_value,
                    new_value,
                ) in comparison_result["changes"]:
                    if row_idx < len(row_keys) and col_name in col_keys:
                        row_key = row_keys[row_idx]  # Get actual RowKey
                        col_key = col_keys[col_name]  # Get actual ColumnKey

                        # Measure the new content width
                        new_text = Text(str(new_value), justify="center")
                        new_content_width = len(
                            str(new_value)
                        )  # Estimate content width
                        current_col = table.columns[col_key]

                        # Check if new content exceeds column width
                        if new_content_width > current_col.width:
                            # Rebuild the entire table with adjusted column widths
                            if debug_print:
                                bp(
                                    f"[INFO] Column '{col_name}' is too small. Resizing...",
                                    app=app,
                                )

                            # Clear & re-add table with resized columns
                            columns = list(new_df.columns)
                            table.clear(columns=True)

                            # Rebuild columns with increased width
                            for col in columns:
                                # Find max width between content and column name
                                max_content_width = max(
                                    len(str(val)) for val in new_df[col]
                                )  # Find max content width
                                col_name_width = len(
                                    str(col)
                                )  # Get column name width
                                final_width = (
                                    max(max_content_width, col_name_width) + 0
                                )  # Ensure padding

                                table.add_column(
                                    col, width=final_width
                                )  # Add column with adjusted width

                            # Re-add rows with updated content
                            for _, row in new_df.iterrows():
                                table.add_row(
                                    *[
                                        Text(str(cell), justify="center")
                                        for cell in row
                                    ]
                                )

                            # app.call_later(lambda: Table.refresh())
                            # app.call_later(lambda: Table.post_message(events.Idle()))  # Force recalculation

                            return  # Exit loop early since table was rebuilt

                        # If content fits, just update normally
                        if debug_print:
                            bp(
                                f"Updating: row_key={row_key}, col_key={col_key}, old={old_value}, new={new_value}",
                                app=app,
                            )

                        # CurrentScrollX = Table.scroll_x
                        # CurrentScrollY = Table.scroll_y
                        # # Table.move_cursor(row=row_idx)
                        # Table.update_cell(row_key, col_key, NewText)
                        # app.call_later(lambda: Table.move_cursor(row=row_idx))
                        # put in call later
                        # Table.scroll_x = CurrentScrollX
                        # Table.scroll_y = CurrentScrollY

                        current_scroll_x = table.scroll_x
                        current_scroll_y = table.scroll_y

                        # Update the cell
                        table.update_cell(row_key, col_key, new_text)

                        # bp(f"moving cursor to row: {row_idx} on Table: {TableName}")

                        # Use call_later to move the cursor after the update
                        app.call_later(lambda: table.move_cursor(row=row_idx))

                        # Restore scroll position after the cursor move
                        app.call_later(
                            lambda: setattr(
                                table, "scroll_x", current_scroll_x
                            )
                        )
                        app.call_later(
                            lambda: setattr(
                                table, "scroll_y", current_scroll_y
                            )
                        )

            # Force table refresh
            # app.call_later(lambda: Table.refresh())

    # Refresh UI
    # asyncio.sleep(0)
    # app.refresh()


async def bspssepy_app_reset_tables(
    app: App,  # The Textual app instance needed for UI updates
    use_config_only: bool = False,  # Flag to determine if only configuration-based columns should be used
) -> None:
    """
    Initializes and resets all BSPSSEPyApp tables.

    This function is called when all required simulation data is collected (e.g., after `simInit` is run).
    If the simulation has not started yet (`app.bspssepy` is not generated), it initializes the tables
    with empty DataFrames.

    Future plan:
        - Add functionality to update tables (or some of them) when a SAV file is selected before the Run starts.

    Parameters:
        app (textual.app.App): The Textual app instance required for UI updates.
        UseconfigOnly (bool, optional): If True, only predefined columns will be used without computing additional data.

    Returns:
        None

    Notes:
        - Uses a dictionary for cleaner, scalable table reset handling.
        - Calls `BSPSSEPyAppResetTable` for each table dynamically.
        - If `app.bspssepy` is not initialized, resets tables with empty data.
        - Debug information is logged via `bp` when `app.debug_checkbox.value` is `True`.
    """

    from fun.bspssepy.sim.bspssepy_channels import fetch_channel_value

    if app is None:
        # bp("[ERROR] App instance is missing.", app=app)
        return

    round_digit = 3

    debug_print = app.debug_checkbox.value
    # Create a shortcut reference
    bspssepy_sequence = app.bspssepy.sim.config.bspssepy_sequence
    bspssepy_brn = app.bspssepy.sim.bspssepy_brn
    bspssepy_bus = app.bspssepy.sim.bspssepy_bus
    bspssepy_load = app.bspssepy.sim.bspssepy_load
    bspssepy_trn = app.bspssepy.sim.bspssepy_trn
    bspssepy_gen = app.bspssepy.sim.bspssepy_gen
    bspssepy_agc = app.bspssepy.sim.bspssepy_agc
    bspssepy_ibr = app.bspssepy.sim.bspssepy_ibr

    # Debugging information
    if app.debug_checkbox.value:
        bp("[DEBUG] Resetting all BSPSSEPyApp tables...", app=app)

    # Check if the simulation has started (i.e., if `app.bspssepy` exists)
    sim_started = hasattr(app, "bspssepy") and app.bspssepy is not None

    # If the simulation has not started, use empty DataFrames
    if not sim_started:
        bp(
            "[INFO] No active simulation detected. Initializing tables with empty DataFrames.",
            app=app,
        )

    # Retrieve or initialize DataFrames
    if sim_started:
        # Define the progress_df DataFrame with mapped columns
        progress_df = pd.DataFrame(
            {
                "Progress": [" 🔴"]
                * len(
                    bspssepy_sequence
                ),  # Initially all actions are not started
                "Control Sequence": [0]
                * len(bspssepy_sequence),  # All set to zero for now
                "Device Type": bspssepy_sequence[
                    "Device Type"
                ],  # Mapped from bspssepy_sequence
                "ID Type": bspssepy_sequence[
                    "Identification Type"
                ],  # Mapped from bspssepy_sequence
                "ID Value": bspssepy_sequence[
                    "Identification Value"
                ],  # Mapped from bspssepy_sequence
                "Action Type": bspssepy_sequence[
                    "Action Type"
                ],  # Mapped from bspssepy_sequence
                "Action Time": bspssepy_sequence[
                    "Action Time"
                ],  # Mapped from bspssepy_sequence
                "Action Status": bspssepy_sequence[
                    "Action Status"
                ],  # Mapped from bspssepy_sequence
            }
        )

        agc_df = bspssepy_agc

        # # Fetch all required channel values asynchronously
        pelec_values, pmech_values, qelec_values, gref_values, vref_values = (
            await fetch_gen_ch_val(bspssepy_gen, debug_print, app)
        )

        # ✅ Apply rounding to all numeric lists
        pelec_values = [round(val, round_digit) for val in pelec_values]
        pmech_values = [round(val, round_digit) for val in pmech_values]
        qelec_values = [round(val, round_digit) for val in qelec_values]
        gref_values = [round(val, round_digit) for val in gref_values]
        vref_values = [round(val, round_digit) for val in vref_values]

        gen_df = pd.DataFrame(
            {
                "Gen Name": bspssepy_gen["MCNAME"],
                "Bus #": bspssepy_gen["NUMBER"],
                "Bus Name": bspssepy_gen["NAME"],
                "Δf": bspssepy_gen["freq"],
                "Pᴱ": pelec_values,
                "Pᴹ": pmech_values,
                "Qᴱ": qelec_values,
                "Gᴿᴱꟳ": gref_values,
                "Vᴿᴱꟳ": vref_values,
            }
        )

        from fun.bspssepy.sim.bspssepy_load_funs import get_load_info

        load_df_temp = await get_load_info(
            [
                "LOADNAME",
                "NUMBER",
                "NAME",
                "MVAACT",
                "ILACT",
                "YLACT",
                "LDGNACT",
                "STATUS",
            ],
            debug_print=debug_print,
            app=app,
        )
        # bp(load_df_temp, app=app)
        # Create the DataFrame
        load_df = pd.DataFrame(
            {
                "load Name": load_df_temp["LOADNAME"],
                "Bus #": load_df_temp["NUMBER"],
                "Bus Name": load_df_temp["NAME"],
                "Power Array [PL, QL, IP, IQ, YP, YQ, PG, QG]": load_df_temp.apply(
                    lambda row: [
                        round(row["MVAACT"].real, round_digit),
                        round(row["MVAACT"].imag, round_digit),
                        round(row["ILACT"].real, round_digit),
                        round(row["ILACT"].imag, round_digit),
                        round(row["YLACT"].real, round_digit),
                        round(row["YLACT"].imag, round_digit),
                        round(row["LDGNACT"].real, round_digit),
                        round(row["LDGNACT"].imag, round_digit),
                    ],
                    axis=1,
                ),
                "Status": load_df_temp["STATUS"],
            }
        )

        from fun.bspssepy.sim.bspssepy_bus_funs import get_bus_info

        bus_df_temp = await get_bus_info(
            ["NUMBER", "NAME", "TYPE"], debug_print=debug_print, app=app
        )
        bus_status = await get_bus_info(
            ["BSPSSEPyStatus"],
            bspssepy_bus=bspssepy_bus,
            debug_print=debug_print,
            app=app,
        )

        bus_df = pd.DataFrame(
            {
                "Bus #": bus_df_temp["NUMBER"],
                "Bus Name": bus_df_temp["NAME"],
                "Type": bus_df_temp["TYPE"],
                "Status": bus_status,
            }
        )

        brn_df = pd.DataFrame(
            {
                "Branch Name": bspssepy_brn["BRANCHNAME"],
                "From Bus #": bspssepy_brn["FROMNUMBER"],
                "To Bus #": bspssepy_brn["TONUMBER"],
                "From Bus Name": bspssepy_brn["FROMNAME"],
                "To Bus Name": bspssepy_brn["TONAME"],
                "Status": bspssepy_brn["STATUS"],
            }
        )

        trn_df = pd.DataFrame(
            {
                "Trans. Name": bspssepy_trn["XFRNAME"],
                "From Bus #": bspssepy_trn["FROMNUMBER"],
                "To Bus #": bspssepy_trn["TONUMBER"],
                "From Bus Name": bspssepy_trn["FROMNAME"],
                "To Bus Name": bspssepy_trn["TONAME"],
                "Status": bspssepy_trn["STATUS"],
            }
        )

        ibr_df = bspssepy_ibr

        # TrnDF = pd.DataFrame()
    else:
        progress_df = pd.DataFrame()
        agc_df = pd.DataFrame()
        gen_df = pd.DataFrame()
        load_df = pd.DataFrame()
        bus_df = pd.DataFrame()
        brn_df = pd.DataFrame()
        trn_df = pd.DataFrame()
        ibr_df = pd.DataFrame()

    df = {
        "Progress": progress_df,
        "AGC": agc_df,
        "Generator": gen_df,
        "load": load_df,
        "Bus": bus_df,
        "Branch": brn_df,
        "Transformer": trn_df,
        "IBR": ibr_df,
    }

    # Dictionary to map table names, column structures, and app table objects
    tables = {
        "Progress": {
            "columns": [
                "Progress",
                "Control Sequence",
                "Device Type",
                "ID Type",
                "ID Value",
                "Action Type",
                "Action Time",
                "Action Status",
            ],
            "AppTable": app.progress_table,
        },
        "AGC": {
            "columns": ["Gen Name", "Alpha", "ΔPᴳ", "Δf"],
            "AppTable": app.agc_table,
        },
        "Generator": {
            "columns": [
                "Gen Name",
                "Bus #",
                "Bus Name",
                "Δf",
                "Pᴱ",
                "Pᴹ",
                "Qᴱ",
                "Gᴿᴱꟳ",
                "Vᴿᴱꟳ",
            ],
            "AppTable": app.gen_table,
        },
        "load": {
            "columns": [
                "load Name",
                "Bus #",
                "Bus Name",
                "Power Array [PL, QL, IP, IQ, YP, YQ, PG, QG]",
                "Status",
            ],
            "AppTable": app.load_table,
        },
        "Bus": {
            "columns": ["Bus #", "Bus Name", "Type", "Status"],
            "AppTable": app.bus_table,
        },
        "Branch": {
            "columns": [
                "Branch Name",
                "From Bus #",
                "To Bus #",
                "From Bus Name",
                "To Bus Name",
                "Status",
            ],
            "AppTable": app.brn_table,
        },
        "Transformer": {
            "columns": [
                "Trans. Name",
                "From Bus #",
                "To Bus #",
                "From Bus Name",
                "To Bus Name",
                "Status",
            ],
            "AppTable": app.trn_table,
        },
        "IBR": {
            "columns": [
                "ID",
                "MCNAME",
                "NAME",
                "NUMBER",
                "STATUS",
                "PGEN",
                "QGEN",
                "WMOD",
                "ibr_type",
                "gfm_flag",
                "init_cap",
                "BSPSSEPyStatus",
                "BSPSSEPyStatus_0",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
            ],
            "AppTable": app.ibr_table,
        },
    }

    # Loop through all tables and reset them dynamically
    for table_name, table_info in tables.items():
        bp(f"[INFO] Resetting {table_name} table...", app=app)

        bspssepy_app_reset_table(
            bspssepy_df=df[table_name],
            table_col=table_info["columns"],
            app=app,
            appTable=table_info["AppTable"],
            use_config_only=use_config_only,
        )
        # await asyncio.sleep(app.async_print_delay if app else 0)

    # Final Debugging Information
    bp("[INFO] All tables have been reset successfully.", app=app)
    # await asyncio.sleep(app.async_print_delay if app else 0)

    if app.debug_checkbox.value:
        bp("[DEBUG] BSPSSEPyApp tables initialized.", app=app)
        # await asyncio.sleep(app.async_print_delay if app else 0)


def bspssepy_app_reset_table(
    bspssepy_df: pd.DataFrame,  # DataFrame containing the source data for the table
    table_col: list[
        str
    ],  # List of column names to be displayed in the table (can include computed columns)
    app: App,  # The Textual app instance (needed for UI updates)
    appTable: DataTable,  # The specific table widget in the GUI to be updated (e.g., app.MyTable)
    use_config_only: (
        bool | None
    ) = False,  # Flag to determine if only configuration-based columns should be used
) -> None:
    """
    Resets and updates a Textual DataTable using the provided DataFrame.

    Parameters:
        BSPSSEPyDataFrame (pd.DataFrame): The DataFrame containing the source data.
        TableCol (list of str): List of column names to include in the table.
            - This list may contain columns that are not in BSPSSEPyDataFrame but will be computed dynamically.
        app (textual.app.App): The Textual app instance required for UI updates.
        appTable (textual.widgets.DataTable): The specific table widget to be updated.
        UseconfigOnly (bool, optional): If True, only predefined columns will be used without computing additional data.

    Returns:
        None

    Notes:
        - The function clears the table, reinitializes columns, and inserts updated rows.
        - If a requested column is not in the DataFrame, it is handled dynamically (e.g., status icons).
        - This function should be called in an async context or a worker to avoid blocking the UI.
    """

    # Ensure required parameters are provided
    if app is None or appTable is None:
        bp("[ERROR] App instance or table reference is missing.", app=app)
        return

    if bspssepy_df is None or table_col is None:
        bp("[ERROR] DataFrame or TableCol list is missing.", app=app)
        return

    # Clear existing table data before updating
    appTable.clear(columns=True)

    # Debugging information
    if app.debug_checkbox.value:
        bp(
            f"[DEBUG] Resetting table {appTable.id} with columns: {table_col}",
            app=app,
        )

    # Add columns to the table
    for col in table_col:
        appTable.add_column(
            col
        )  # No need to set justify here, we do it per cell
    # Debugging information
    if app.debug_checkbox.value:
        bp(
            f"[DEBUG] Added columns: {table_col} (content will be centered)",
            app=app,
        )

    # Populate the table with rows from the DataFrame
    for _, row in bspssepy_df.iterrows():
        row_data = []

        for col in table_col:
            if col in bspssepy_df.columns:
                cell_value = row[col]  # Get the original value
            else:
                cell_value = (
                    ""  # Default empty value for unknown computed columns
                )

            # Convert value to `Text` object with center alignment
            row_data.append(Text(str(cell_value), justify="center"))

        # Add the row to the table
        appTable.add_row(*row_data)
    # Force a UI refresh to reflect changes
    app.call_later(appTable.refresh)
    # app.refresh()

    bp("[INFO] Table successfully reset and updated.", app=app)

    # Debugging information
    if app.debug_checkbox.value:
        bp("[DEBUG] Table update completed.", app=app)


# def BSPSSEPyAppUpdateTables(*args, app=None) -> None:
#     """This function will update the BSPSSEPyApp Tables using the available data-frames and by calling PSSE functions to collect new measurements (mainly from channels)"""


# async def GetLoadInfoPSSE(LoadNames: list(str), debug_print, app):
# "Write a function that calls bspssepy_load"


async def fetch_gen_ch_val(bspssepy_gen, debug_print, app):
    """
    Asynchronously fetches channel values for all generators in bspssepy_gen.

    Parameters:
        bspssepy_gen (pd.DataFrame): Generator DataFrame.
        debug_print (bool): Enables debugging messages if True.
        app (textual.app.App): The Textual app instance.

    Returns:
        Tuple of lists: (pelec_values, pmech_values, qelec_values, gref_values, vref_values)
    """

    async def fetch_row_channels(row):
        from fun.bspssepy.sim.bspssepy_channels import fetch_channel_value

        """
        Fetches channel values for a single generator row asynchronously.
        """
        return (
            await fetch_channel_value(
                int(row["PELECChannel"]), debug_print=debug_print, app=app
            ),
            await fetch_channel_value(
                int(row["PMECHChannel"]), debug_print=debug_print, app=app
            ),
            await fetch_channel_value(
                int(row["QELECChannel"]), debug_print=debug_print, app=app
            ),
            await fetch_channel_value(
                int(row["GREFChannel"]), debug_print=debug_print, app=app
            ),
            await fetch_channel_value(
                int(row["VREFChannel"]), debug_print=debug_print, app=app
            ),
        )

    # Use `asyncio.gather()` to fetch all generator data in parallel
    results = await asyncio.gather(
        *(fetch_row_channels(row) for _, row in bspssepy_gen.iterrows())
    )

    # Unpack results into separate lists
    pelec_values, pmech_values, qelec_values, gref_values, vref_values = zip(
        *results
    )

    return (
        list(pelec_values),
        list(pmech_values),
        list(qelec_values),
        list(gref_values),
        list(vref_values),
    )


def progress_bar_update(
    progress_bar, current_time, total_time, App=None, label=None
):
    """
    Updates the progress bar based on the current simulation time.

    Parameters:
        ProgressBar (ProgressBar): The ProgressBar widget to update.
        CurrentTime (int | float): The current simulation time in seconds.
        TotalTime (int | float): The total simulation time in seconds (set only once).
        App (BSPSSEPyApp, optional): The main Textual app instance for UI updates.
        label (Label, optional): The label to display the current simulation time.
    """

    # Ensure TotalTime is greater than 0 to avoid division errors
    if total_time <= 0:
        return

    # Calculate progress percentage
    progress_percentage = min(
        (current_time / total_time) * 100, 100
    )  # Cap at 100%

    progress_bar.update(
        total=100, progress=progress_percentage
    )  # Update the progress bar

    # Format the time display with hours, minutes, and seconds
    hours = current_time // 3600
    minutes = (current_time % 3600) // 60
    seconds = current_time % 60

    if hours > 0:
        time_display = f"t = {int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        time_display = f"t = {int(minutes)}m {int(seconds)}s"
    else:
        time_display = f"t = {int(seconds)}s"

    # Format the time display
    # TimeDisplay = f"t = {int(CurrentTime)}s" if CurrentTime < 60 else f"t = {int(CurrentTime//60)}m {int(CurrentTime%60)}s"

    # # ✅ Schedule UI updates to prevent lagging
    # if App:
    #     App.call_later(append_to_details_text_area, App.details_text_area, f"Progress: {ProgressPercentage}%")

    if label:
        App.call_later(
            label.update, time_display
        )  # ✅ Properly schedules label update


def add_sav_files_to_tree(parent_node, folder_path):
    """
    Recursively scans the given folder and adds .sav files as leaves
    and subfolders as expandable nodes in the tree.

    Parameters:
        ParentNode (Tree.Node): The parent node where items will be added.
        FolderPath (str): The path of the folder to scan.
    """
    try:
        # Get a sorted list of all items (files & directories) in the folder
        for entry in sorted(
            os.scandir(folder_path), key=lambda E: E.name.lower()
        ):
            if entry.is_dir():
                # If it's a folder, add it as a node and recurse into it
                folder_node = parent_node.add(entry.name, expand=False)
                add_sav_files_to_tree(folder_node, entry.path)
            elif entry.is_file() and entry.name.endswith(".sav"):
                # If it's a .sav file, add it as a leaf
                parent_node.add_leaf(entry.name)
    except PermissionError:
        pass  # If permission is denied, just skip that folder
