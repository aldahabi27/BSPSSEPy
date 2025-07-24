"""_summary_"""

import pandas as pd

# pyright: reportMissingImports=false
import psspy  # noqa: F401 pylint: disable=import-error
from .bspssepy_channels import fetch_channel_value


async def bspssepy_meas_update(
    bspssepy_ibr: pd.DataFrame(),
    bspssepy_agc: pd.DataFrame(),
    bspssepy_brn: pd.DataFrame(),
    bspssepy_bus: pd.DataFrame(),
    bspssepy_gen: pd.DataFrame(),
    bspssepy_load: pd.DataFrame(),
    bspssepy_trn: pd.DataFrame(),
    old_freq_dev: list[float],
    time_step=1.0,
    app=None,
    debug_print: bool | None = False,
) -> tuple[int, list]:
    """
    This function will update all the measurements for all elements in the
    provided pd.DataFrames.

    Args:
        bspssepy_ibr (pd.DataFrame): Contains all IBR information.
        bspssepy_agc (pd.DataFrame): Contains all AGC related information.
        bspssepy_brn (pd.DataFrame): Contains all branches information.
        bspssepy_bus (pd.DataFrame): Contains all buses information.
        bspssepy_gen (pd.DataFrame): Contains all generators information.
        bspssepy_load (pd.DataFrame): Contains all load information.
        bspssepy_trn (pd.DataFrame): Contains all transformers information.
        app (Textual App | None, optional): app instance to update the GUI
                                            if available.
        debug_print (bool | None, optional): Flag to print debug msgs.
                                             Defaults to False.

    Returns:
        tuple[int, list]:
            meas_updated (int): flag to indicate that the measurements are
                                updated successfully.
                                0: Failed to update any measurement.
                                1: Some measurements were updated
                                   successfully.
                                2: All measurements were updated successfully.
            errors (list): List containing any error being encountered while
                           updating the measurements.
    """

    # Initialize the return values
    meas_updated = 2
    errors = []

    s_base = psspy.sysmva()
    ierr, freq_base = psspy.base_frequency()
    # Updating all measurements in bspssepy_ibr dataframe
    for i_ibr_row, ibr_row in bspssepy_ibr.iterrows():
        ibr_bus_num = ibr_row["NUMBER"]
        ibr_id = ibr_row["ID"]
        ierr, ibr_base = psspy.macdat(ibr_bus_num, ibr_id, "MBASE")
        p_ch = ibr_row["PELECChannel"]
        q_ch = ibr_row["QELECChannel"]
        soc_ch = ibr_row["SOCChannel"]

        p_elec = (
            await fetch_channel_value(
                p_ch,
                debug_print=debug_print,
                app=app,
            )
            * s_base
        )

        q_elec = (
            await fetch_channel_value(
                q_ch,
                debug_print=debug_print,
                app=app,
            )
            * s_base
        )
        soc = (
            await fetch_channel_value(
                soc_ch,
                debug_print=debug_print,
                app=app,
            )
            * ibr_base
        )
        bspssepy_ibr.at[i_ibr_row, "PGEN"] = p_elec
        bspssepy_ibr.at[i_ibr_row, "QGEN"] = q_elec
        bspssepy_ibr.at[i_ibr_row, "curr_cap"] = soc

    """    
    Qelec = (
        await FetchChannelValue(
            41,
            debug_print=False,
            app=app,
        )
        * 50
    )
    WQCMND = (
        await FetchChannelValue(
            39,
            debug_print=False,
            app=app,
        )
        * 50
    )
    a = await GetGenInfo(
        ["NAME", "NUMBER", "MCNAME", "STATUS", "WMOD", "PGEN", "QGEN"]
    )

    with pd.option_context(
        "display.max_rows",
        None,  # Show all rows
        "display.max_columns",
        None,  # Show all columns
        "display.width",
        0,  # Auto-adjust width for full visibility
        "display.colheader_justify",
        "center",  # Center column headers for readability
    ):
        bp(a.to_string(index=False))
        await asyncio.sleep(app.async_print_delay if app else 0)

    bp([Pelec, WPCMND, Qelec, WQCMND])
    await asyncio.sleep(app.async_print_delay if app else 0)
    """

    # Updating Generator Measurements
    for i_gen_row, gen_row in bspssepy_gen.iterrows():
        gen_bus_num = gen_row["NUMBER"]
        gen_id = gen_row["ID"]
        ierr, gen_base = psspy.macdat(gen_bus_num, gen_id, "MBASE")
        pe_ch = gen_row["PELECChannel"]
        pm_ch = gen_row["PMECHChannel"]
        qe_ch = gen_row["QELECChannel"]
        gref_ch = gen_row["GREFChannel"]
        vref_ch = gen_row["VREFChannel"]
        freq_ch = gen_row["FChannel"]

        p_elec = (
            await fetch_channel_value(
                pe_ch,
                debug_print=debug_print,
                app=app,
            )
            * s_base
        )
        p_mech = (
            await fetch_channel_value(
                pm_ch,
                debug_print=debug_print,
                app=app,
            )
            * gen_base
        )

        q_elec = (
            await fetch_channel_value(
                qe_ch,
                debug_print=debug_print,
                app=app,
            )
            * s_base
        )

        g_ref = (
            await fetch_channel_value(
                gref_ch,
                debug_print=debug_print,
                app=app,
            )
            * gen_base
        )

        v_ref = await fetch_channel_value(
            vref_ch,
            debug_print=debug_print,
            app=app,
        )

        freq = (
            await fetch_channel_value(
                freq_ch,
                debug_print=debug_print,
                app=app,
            )
            * freq_base
        )

        bspssepy_gen.at[i_gen_row, "p_elec"] = p_elec
        bspssepy_gen.at[i_gen_row, "p_mech"] = p_mech
        bspssepy_gen.at[i_gen_row, "q_elec"] = q_elec
        bspssepy_gen.at[i_gen_row, "g_ref"] = g_ref
        bspssepy_gen.at[i_gen_row, "v_ref"] = v_ref
        bspssepy_gen.at[i_gen_row, "freq"] = freq

    # Updating AGC Measurements
    agc_gen = len(bspssepy_gen[bspssepy_gen["AGCAlpha"] > 0])
    agc_gen_active = len(
        bspssepy_gen[
            (bspssepy_gen["BSPSSEPyStatus"] == 3)
            & (bspssepy_gen["AGCAlpha"] > 0)
        ]
    )

    if agc_gen > 0:
        bspssepy_gen.loc[
            bspssepy_gen["BSPSSEPyStatus"] == 3, "EffectiveAGCAlpha"
        ] = bspssepy_gen["AGCAlpha"] * (agc_gen / agc_gen_active)
    else:
        bspssepy_gen["EffectiveAGCAlpha"] = (
            0  # No active generators, so set to zero
        )

    for i_agc_row, agc_row in bspssepy_agc.iterrows():
        gen_name = agc_row["Gen Name"]
        if gen_name == "avg_freq":
            # Skip the average frequency row
            continue
        bspssepy_agc.at[i_agc_row, "Alpha"] = bspssepy_gen.loc[
            bspssepy_gen["MCNAME"] == gen_name, "EffectiveAGCAlpha"
        ].values[0]

        freq_dev = bspssepy_gen.loc[
            bspssepy_gen["MCNAME"] == gen_name, "freq"
        ].values[0]
        bspssepy_agc.at[i_agc_row, "Δf (Hz)"] = freq_dev

        # Calculate the rate of frequency deviation
        current_gen_freq_dev_rate = (
            abs(old_freq_dev[i_agc_row] - freq_dev) / time_step
        )

        bspssepy_agc.at[i_agc_row, "Δf' (Hz/s)"] = current_gen_freq_dev_rate

        old_freq_dev[i_agc_row] = freq_dev

    # Since all gens freq are updated, we can update the average frequency
    avg_freq = 0
    avg_freq_rate = 0
    sys_H = 0
    for _, gen_row in bspssepy_gen.iterrows():
        if gen_row["BSPSSEPyStatus"] == 3:
            avg_freq += gen_row["freq"] * gen_row["H"]
            avg_freq_rate += (
                bspssepy_agc.loc[
                    bspssepy_agc["Gen Name"] == gen_row["MCNAME"],
                    "Δf' (Hz/s)",
                ].values[0]
                * gen_row["H"]
            )
            sys_H += gen_row["H"]
    avg_freq /= sys_H if sys_H > 0 else -999
    avg_freq_rate /= sys_H if sys_H > 0 else -999
    bspssepy_agc.loc[bspssepy_agc["Gen Name"] == "avg_freq", "Δf (Hz)"] = (
        avg_freq
    )
    bspssepy_agc.loc[bspssepy_agc["Gen Name"] == "avg_freq", "Δf' (Hz/s)"] = (
        avg_freq_rate
    )

    return meas_updated, errors, old_freq_dev
