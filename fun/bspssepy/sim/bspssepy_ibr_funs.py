"""_summary_

Raises:
    ValueError: _description_
    ValueError: _description_
    RuntimeError: _description_
    RuntimeError: _description_

Returns:
    _type_: _description_
"""

import asyncio
import pandas as pd

# pyright: reportMissingImports=false
import psspy  # noqa: F401 pylint: disable=import-error
from fun.bspssepy.sim.bspssepy_default_vars import bspssepy_default_vars_fun
from fun.bspssepy.app.app_helper_funs import bp
from fun.bspssepy.sim.bspssepy_gen_funs import GetGenInfo

from fun.bspssepy.bspssepy_dict import bspssepy_ibr_ch_mapping


async def build_bspssepy_ibr(
    ibr_config,
    bspssepy_ibr,
    sim_config,
    app,
    debug_print: bool | None = False,
) -> pd.DataFrame:
    """_summary_

    Args:
        ibr_config (_type_): _description_
        bspssepy_ibr (_type_): _description_
        app (_type_): _description_
        debug_print (bool | None, optional): _description_. Defaults to False.
    """

    if isinstance(ibr_config, list) and not (
        ibr_config is None or len(ibr_config) == 0
    ):
        # Create the IBR configuration DataFrame
        ibr_config_df = pd.DataFrame(ibr_config)

        # Rename the columns to match the expected format
        ibr_config_df = ibr_config_df.rename(
            columns={
                "IBR Name": "MCNAME",
                "IBR Type": "ibr_type",
                "GFM Flag": "gfm_flag",
                "Initial Capacity": "init_cap",
            }
        )

        # Merge ibr_config_df with bspssepy_ibr

        # Step 3: Merge on MCNAME (you could also use 'Bus Name' → 'NAME' if needed)
        bspssepy_ibr = bspssepy_ibr.merge(
            ibr_config_df[["MCNAME", "ibr_type", "gfm_flag", "init_cap"]],
            on="MCNAME",
            how="left",
        )
        # Add metadata columns
        bspssepy_ibr["BSPSSEPyStatus"] = bspssepy_ibr["STATUS"].apply(
            lambda x: "Online" if x == 1 else "Offline"
        )  # Set BSPSSEPyStatus based on STATUS
        bspssepy_ibr["BSPSSEPyStatus_0"] = bspssepy_ibr[
            "BSPSSEPyStatus"
        ]  # Initial status
        bspssepy_ibr["BSPSSEPyLastAction"] = "Initialized"
        bspssepy_ibr["BSPSSEPyLastActionTime"] = 0.0
        bspssepy_ibr["BSPSSEPySimulationNotes"] = "Initialized"

        # --> corresponding to WPCMND in machine_array_channel
        # (check the API - status(2) = 22)
        bspssepy_ibr["WPCMNDChannel"] = -1
        # --> corresponding to WQCMND in machine_array_channel
        # (check the API - status(2) = 23)
        # --> corresponding to PELEC in machine_array_channel
        # (check the API - status(2) = 2)
        bspssepy_ibr["PELECChannel"] = -1
        # --> corresponding to QELEC in machine_array_channel
        # (check the API - status(2) = 3)
        bspssepy_ibr["QELECChannel"] = -1
        # --> This is the frequency channel for the generator
        # (will be fetched from config.Channels)
        bspssepy_ibr["FChannel"] = -1

        for ibr_row_index, ibr_row in bspssepy_ibr.iterrows():
            for key in bspssepy_ibr_ch_mapping.keys():
                ierr = psspy.machine_array_channel(
                    [
                        -1,  # Next available channel
                        # status(2) --> quantity to monitor
                        bspssepy_ibr_ch_mapping[key],
                        # Bus number corresponding to machine location
                        int(ibr_row["NUMBER"]),
                    ],
                    ibr_row["ID"],  # ID of the machine
                    key + ibr_row["MCNAME"],  # Channel Identifier
                )

                if ierr != 0:
                    bp(
                        f"[ERROR] Error occured during adding channel for IBR: {ibr_row['MCNAME']} to monitor {key} with key_status number: {bspssepy_ibr_ch_mapping[key]}",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)
                else:
                    bspssepy_ibr.at[ibr_row_index, key + "Channel"] = (
                        sim_config.CurrentChannelIndex
                    )
                    if debug_print:
                        bp(
                            f"[DEBUG] Successfully added channel for IBR: {ibr_row['MCNAME']} to monitor {key} with channel index {sim_config.CurrentChannelIndex}",
                            app=app,
                        )
                        await asyncio.sleep(
                            app.async_print_delay if app else 0
                        )
                    # Increament Channel index
                    sim_config.CurrentChannelIndex += 1

        return bspssepy_ibr.copy()
    return pd.DataFrame()


async def ibr_enable(
    bspssepy_ibr: pd.DataFrame,
    t: int,
    action: dict,
    ibr_name: str | None = None,
    ibr_index: int | None = None,
    debug_print: bool | None = False,
    app=None,
    config=None,
):
    """_summary_

    Args:
        bspssepy_ibr (pd.DataFrame): _description_
        t (int): _description_
        action (dict): _description_
        ibr_name (str | None, optional): _description_. Defaults to None.
        ibr_index (int | None, optional): _description_. Defaults to None.
        debug_print (bool | None, optional): _description_. Defaults to False.
        app (_type_, optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_
        ValueError: _description_
        RuntimeError: _description_
        RuntimeError: _description_

    Returns:
        _type_: _description_
    """
    if debug_print:
        bp(
            f"[DEBUG] Running ibr_enable function for action: {action}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    if ibr_name is None and ibr_index is None:
        raise ValueError("Either ibr_name or ibr_index must be provided.")

    if ibr_name is None:
        ibr_name = bspssepy_ibr.iloc[ibr_index]["MCNAME"]

    # we control the IBR by name
    # get all info needed to enable the IBR
    ibr_row_df = bspssepy_ibr[bspssepy_ibr["MCNAME"] == ibr_name]
    if ibr_row_df.empty:
        raise ValueError(
            f"IBR with name '{ibr_name}' not found in bspssepy_ibr DataFrame."
        )

    curr_status = await GetGenInfo(
        "STATUS", GenName=ibr_name, debug_print=debug_print, app=app
    )

    if curr_status != 0:
        bp(
            f"IBR '{ibr_name}' is already enabled at bus "
            f"{ibr_row_df['NUMBER'].values[0]} with ID "
            f"{ibr_row_df['ID'].values[0]}. Current status: {curr_status}",
            app=app,
        )
        return 0

    ibr_bus_num = ibr_row_df["NUMBER"].values[0]
    ibr_id = ibr_row_df["ID"].values[0]
    _i, _r, _c = bspssepy_default_vars_fun()
    ierr = psspy.machine_chng_5(
        ibr_bus_num,
        ibr_id,
        [1] + [_i] * 6,
        [_r] * 17,
        [_c] * 2,
    )

    if ierr != 0:
        if debug_print:
            bp(
                f"[DEBUG] Error enabling IBR '{ibr_name}' at bus {ibr_bus_num}"
                f" with ID {ibr_id}. Error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
        raise RuntimeError(
            f"Failed to enable IBR '{ibr_name}' at bus {ibr_bus_num}"
            f" with ID {ibr_id}. Error code: {ierr}"
        )

    new_status = await GetGenInfo(
        "STATUS", GenName=ibr_name, debug_print=debug_print, app=app
    )

    # here
    if new_status != 1:
        bp(
            f"Failed to enable IBR '{ibr_name}' at bus {ibr_bus_num} "
            f"with ID {ibr_id}. Status is {new_status}.",
            app=app,
        )
        raise RuntimeError(
            f"Failed to enable IBR '{ibr_name}' at bus {ibr_bus_num} "
            f"with ID {ibr_id}. Status is {new_status}."
        )

    if not (bspssepy_ibr is None or bspssepy_ibr.empty):
        # Update the bspssepy_ibr DataFrame
        ibr_name_cond = bspssepy_ibr["MCNAME"] == ibr_name
        ibr_bus_num_cond = bspssepy_ibr["NUMBER"] == ibr_bus_num
        ibr_id_cond = bspssepy_ibr["ID"] == ibr_id
        bspssepy_ibr.loc[
            ibr_name_cond & ibr_bus_num_cond & ibr_id_cond,
            [
                "BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "STATUS",
            ],
        ] = ["Online", "Enable", t, "IBR successfully enabled.", new_status]

    if debug_print:
        bp(
            f"[SUCCESS] Successfully enabled IBR '{ibr_name}' at bus "
            f"{ibr_bus_num} with ID {ibr_id}. Updated bspssepy_ibr DataFrame.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
    return ierr


async def ibr_disable(
    bspssepy_ibr: pd.DataFrame,
    t: int,
    action: dict | None = None,
    ibr_name: str | None = None,
    ibr_index: int | None = None,
    debug_print: bool | None = False,
    app=None,
) -> int:
    """_summary_

    Args:
        bspssepy_ibr (pd.DataFrame): _description_
        t (int): _description_
        action (dict): _description_
        ibr_name (str | None, optional): _description_. Defaults to None.
        ibr_index (int | None, optional): _description_. Defaults to None.
        debug_print (bool | None, optional): _description_. Defaults to False.
        app (_type_, optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_
        ValueError: _description_
        RuntimeError: _description_
        RuntimeError: _description_

    Returns:
        _type_: _description_
    """
    if debug_print:
        bp(
            f"[DEBUG] Running ibr_disable function for action: {action}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    if ibr_name is None and ibr_index is None:
        raise ValueError("Either ibr_name or ibr_index must be provided.")

    if ibr_name is None:
        ibr_name = bspssepy_ibr.iloc[ibr_index]["MCNAME"]

    # we control the IBR by name
    # get all info needed to enable the IBR
    ibr_row_df = bspssepy_ibr[bspssepy_ibr["MCNAME"] == ibr_name]
    if ibr_row_df.empty:
        raise ValueError(
            f"IBR with name '{ibr_name}' not found in bspssepy_ibr DataFrame."
        )

    curr_status = await GetGenInfo(
        "STATUS", GenName=ibr_name, debug_print=debug_print, app=app
    )

    if curr_status != 1:
        bp(
            f"IBR '{ibr_name}' is already disabled at bus "
            f"{ibr_row_df['NUMBER'].values[0]} with ID "
            f"{ibr_row_df['ID'].values[0]}. Current status: {curr_status}",
            app=app,
        )
        return 0
    ibr_bus_num = ibr_row_df["NUMBER"].values[0]
    ibr_id = ibr_row_df["ID"].values[0]
    _i, _r, _c = bspssepy_default_vars_fun()
    ierr = psspy.machine_chng_5(
        ibr_bus_num,
        ibr_id,
        [0] + [_i] * 6,
        [_r] * 17,
        [_c] * 2,
    )

    if ierr != 0:
        if debug_print:
            bp(
                f"[DEBUG] Error disabling IBR '{ibr_name}' at bus "
                f"{ibr_bus_num} with ID {ibr_id}. Error code: {ierr}",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
        raise RuntimeError(
            f"Failed to disable IBR '{ibr_name}' at bus {ibr_bus_num}"
            f" with ID {ibr_id}. Error code: {ierr}"
        )

    new_status = await GetGenInfo(
        "STATUS", GenName=ibr_name, debug_print=debug_print, app=app
    )
    # here
    if new_status != 0:
        bp(
            f"Failed to disable IBR '{ibr_name}' at bus {ibr_bus_num} "
            f"with ID {ibr_id}. Status is 0.",
            app=app,
        )
        raise RuntimeError(
            f"Failed to disable IBR '{ibr_name}' at bus {ibr_bus_num} "
            f"with ID {ibr_id}. Status is {new_status}."
        )

    if not (bspssepy_ibr is None or bspssepy_ibr.empty):
        # Update the bspssepy_ibr DataFrame
        ibr_name_cond = bspssepy_ibr["MCNAME"] == ibr_name
        ibr_bus_num_cond = bspssepy_ibr["NUMBER"] == ibr_bus_num
        ibr_id_cond = bspssepy_ibr["ID"] == ibr_id
        bspssepy_ibr.loc[
            ibr_name_cond & ibr_bus_num_cond & ibr_id_cond,
            [
                "BSPSSEPyStatus",
                "BSPSSEPyLastAction",
                "BSPSSEPyLastActionTime",
                "BSPSSEPySimulationNotes",
                "STATUS",
            ],
        ] = ["Online", "Enable", t, "IBR successfully enabled.", new_status]

    if debug_print:
        bp(
            f"[SUCCESS] Successfully enabled IBR '{ibr_name}' at bus "
            f"{ibr_bus_num} with ID {ibr_id}. Updated bspssepy_ibr DataFrame.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
    return ierr


async def ibr_update(
    bspssepy_ibr,
    t,
    action,
    ibr_name,
    config,
    debug_print=False,
    app=None,
):
    """
    This function will update the output "power" of the IBR device.
    The function will require the following information as input:

    Parameters:
        ibr_name: IBR name of interest
        bspssepy_ibr: The dataframe containing ibr data.
        t: The current simulation time
        action: The action dictionary entry that has all required information
                about the IBR and its latest status. This action element needs
                to be updated to keep track of the progress of the action
                requested, to tell the main program when the action is
                completed.
        debug_print (bool, optional): Enable detailed debug output.
                                      Defaults to False.
    Returns:
        UpdatedActionStatus: The updated Action Status of the generator.
    """

    if debug_print:
        bp(
            f"[DEBUG] Running ibr_update function for action: {action}",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    values: dict = config.bspssepy_sequence.at[
        action["BSPSSEPySequenceRowIndex"], "Values"
    ]
    # bp(f"values Type = {type(values)}"
    #         f"values Content:\n{values}")
    # await asyncio.sleep(app.async_print_delay if app else 0)

    ibr_p_set_point = values["P"] if "P" in values else None
    ibr_q_set_point = values["Q"] if "Q" in values else None

    ibr_row_df = bspssepy_ibr[bspssepy_ibr["MCNAME"] == ibr_name]
    if ibr_row_df.empty:
        raise ValueError(
            f"IBR with name '{ibr_name}' not found in bspssepy_ibr DataFrame."
        )

    ibr_bus_num = ibr_row_df["NUMBER"].values[0]
    ibr_id = ibr_row_df["ID"].values[0]
    _i, _r, _c = bspssepy_default_vars_fun()

    ierr, ibr_mva_base = psspy.macdat(ibr_bus_num, ibr_id, "MBASE")
    # GenTargetPower = BSPSSEPyGenRow["POPF"].values[0]
    ibr_p_set_point_pu = ibr_p_set_point / ibr_mva_base

    # Set the IBR output real power to
    ierr = psspy.change_pref(ibr_bus_num, ibr_id, ibr_p_set_point_pu)

    if ierr != 0:
        bp(
            f"[ERROR] Error occured when setting IBR: {ibr_name} output real "
            f"power to ibr_p_set_point: {ibr_p_set_point}. System will exit.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)
        if app:
            raise Exception("Error in ibr_update function!")
        else:
            SystemExit(0)

    if debug_print:
        bp(
            f"[DEBUG] Successfully set IBR: {ibr_name} output real power to "
            f"ibr_p_set_point: {ibr_p_set_point}.",
            app=app,
        )
        await asyncio.sleep(app.async_print_delay if app else 0)

    bp(f"IBR: '{ibr_name}' Set-point updated.", app=app)
    await asyncio.sleep(app.async_print_delay if app else 0)

    ibr_row_df["BSPSSEPyLastAction"] = "Update Set-point"
    ibr_row_df["BSPSSEPyLastActionTime"] = t
    ibr_row_df["BSPSSEPySimulationNotes"] = (
        f"Updated Set-point to {ibr_p_set_point}"
    )

    # Write the row back to the DataFrame
    bspssepy_ibr.loc[bspssepy_ibr["MCNAME"] == ibr_name, :] = ibr_row_df
    update_action_status = 2

    return update_action_status
