"""_summary_"""

import pandas as pd
# pyright: reportMissingImports=false
import psspy  # noqa: F401 pylint: disable=import-error
from .bspssepy_channels import FetchChannelValue


async def bspssepy_meas_update(
    bspssepy_ibr: pd.DataFrame(),
    bspssepy_agc: pd.DataFrame(),
    bspssepy_brn: pd.DataFrame(),
    bspssepy_bus: pd.DataFrame(),
    bspssepy_gen: pd.DataFrame(),
    bspssepy_load: pd.DataFrame(),
    bspssepy_trn: pd.DataFrame(),
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

    # Updating all measurements in bspssepy_ibr dataframe
    for i_ibr_row, ibr_row in bspssepy_ibr.iterrows():
        ibr_bus_num = ibr_row["NUMBER"]
        ibr_id = ibr_row["ID"]
        ierr, ibr_base = psspy.macdat(ibr_bus_num, ibr_id, "MBASE")
        p_ch = ibr_row["PELECChannel"]
        q_ch = ibr_row["QELECChannel"]
        
        p_elec = (
            await FetchChannelValue(
                p_ch,
                debug_print=debug_print,
                app=app,
            )
            * ibr_base
        )
        
        q_elec = (
            await FetchChannelValue(
                q_ch,
                debug_print=debug_print,
                app=app,
            )
            * ibr_base
        )
        
        bspssepy_ibr.at[i_ibr_row, "PGEN"] = p_elec
        bspssepy_ibr.at[i_ibr_row, "QGEN"] = q_elec
        
        
        
    # Qelec = (
    #     await FetchChannelValue(
    #         41,
    #         debug_print=False,
    #         app=app,
    #     )
    #     * 50
    # )
    # WQCMND = (
    #     await FetchChannelValue(
    #         39,
    #         debug_print=False,
    #         app=app,
    #     )
    #     * 50
    # )
    # a = await GetGenInfo(
    #     ["NAME", "NUMBER", "MCNAME", "STATUS", "WMOD", "PGEN", "QGEN"]
    # )

    # with pd.option_context(
    #     "display.max_rows",
    #     None,  # Show all rows
    #     "display.max_columns",
    #     None,  # Show all columns
    #     "display.width",
    #     0,  # Auto-adjust width for full visibility
    #     "display.colheader_justify",
    #     "center",  # Center column headers for readability
    # ):
    #     bp(a.to_string(index=False))
    #     await asyncio.sleep(app.async_print_delay if app else 0)

    # bp([Pelec, WPCMND, Qelec, WQCMND])
    # await asyncio.sleep(app.async_print_delay if app else 0)
    return meas_updated, errors
