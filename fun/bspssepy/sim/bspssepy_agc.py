import numpy as np
import pandas as pd
import psse3601
import psspy
from .bspssepy_gen_funs import GetGenInfo
from .bspssepy_channels import FetchChannelValue, FetchChannelValuesFromOUTFile
from fun.bspssepy.app.app_helper_funs import bp
import asyncio
from dyntools import CHNF



async def FetchFrequencyFromOUTFile(OUTFile, ChannelIndex, debug_print=False, app=None):
    """
    Fetches frequency data from the .out file for a specific channel.

    Parameters:
        OUTFile (str): Path to the .out file.
        ChannelIndex (int): The channel index corresponding to the desired frequency data.
        debug_print (bool): If True, prints debug information.

    Returns:
        list: Frequency data from the specified channel.

    Notes:
        - This function extracts the entire time-series data for the given channel index.
        - It uses dyntools to read data from the .out file.
    """
    return await FetchChannelValuesFromOUTFile(OUTFile, ChannelIndex, debug_print, app=app)


async def FetchFrequency(ChannelIndex, OUTFile=None, debug_print=False, app=None):
    """
    Attempts to fetch frequency data using psspy.chnval. If it fails, falls back to dyntools.

    Parameters:
        ChannelIndex (int): Channel index for retrieving frequency data via PSSE.
        OUTFile (str, optional): Path to the .out file for fallback in case of errors.
        debug_print (bool): If True, prints debug information.

    Returns:
        float: The most recent frequency value.

    Notes:
        - This function first tries to fetch the data using psspy.chnval for real-time values.
        - If psspy.chnval fails, it retrieves the most recent value from the .out file.
    """
    return await FetchChannelValue(ChannelIndex, OUTFile, debug_print,app=app)






async def AGCControl(
        bspssepy_gen: pd.DataFrame,
        bspssepy_agc: pd.DataFrame,
        Channels,
        OUTFile=None,
        UseOutFile=False,
        TimeStep=1.0,
        AGCTimeConstant=60.0,
        Deadband=0.001, # in Hz
        debug_print: bool | None = False,
        app=None,
        BaseFrequency = 1,
        FrequencyRegulated: bool | None = False,
        old_freq_dev: float | None = 0,  # Δf[k-1] (Hz)
        ):
    """
    Perform Automatic Generation Control (AGC) using frequency deviation data.

    Parameters:
        bspssepy_gen (pd.DataFrame): DataFrame containing generator data with the following columns:
            - "AGC Participation Factor"
            - "Bus Number"
            - "Generator Name"
        bspssepy_agc (pd.DataFrame): DataFrame containing summary of AGC status per generator, mainly used
        for GUI updates and tracking of actions.
        Channels (list): List of channel mappings (from config.Channels).
        OUTFile (str, optional): Path to the .out file for fallback frequency data retrieval.
        UseOutFile (bool): If True, always uses the .out file for frequency retrieval.
        TimeStep (float): Simulation time step in seconds.
        AGCTimeConstant (float): Time constant for the first-order AGC adjustment in seconds.
        Deadband (float): Deadband for AGC action in Hz.
        debug_print (bool): If True, prints detailed debug information.

    Returns:
        pd.DataFrame: Updated DataFrame with adjusted generator setpoints.
    """
    
    # Build a mapping of bus numbers to frequency channel indices
    FrequencyChannels = {
        channel["Bus Number"]: channel["Channel Index"]
        for channel in Channels
        if channel["Channel Type"] == "Frequency"
    }

    if debug_print:
        bp("[DEBUG] Frequency Channels Mapping:", FrequencyChannels, app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)


    # Fetch frequency deviations for all generators
    GeneratorFrequencies = []
    gen_freq_dev_rate = []
    # bp(bspssepy_gen["BSPSSEPyStatus"])
    for _, gen_row in bspssepy_gen.iterrows():
        bus_num = gen_row['NUMBER']
        ChannelIndex = FrequencyChannels.get(bus_num, None)
        # bp(bspssepy_agc.loc[bspssepy_agc["Gen Name"] == gen_row["MCNAME"]])
        # await asyncio.sleep(app.async_print_delay if app else 0)

        if gen_row["BSPSSEPyStatus"] == 3:    
            if ChannelIndex is not None:
                # Use either the `.out` file or `psspy.chnval` based on the UseOutFile flag
                if UseOutFile and OUTFile:
                    FrequencyDeviationPU = await FetchFrequencyFromOUTFile(OUTFile, ChannelIndex, debug_print, app=app)[-1]
                else:
                    FrequencyDeviationPU = await FetchFrequency(ChannelIndex, OUTFile if not UseOutFile else None, debug_print,app=app)

                # Handle NaN values (no AGC action if frequency is NaN)
                if np.isnan(FrequencyDeviationPU):
                    bp("[WARNING] NAN frequency deviation detected. NO AGC Action will be taken.", app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                    return bspssepy_gen, bspssepy_agc, FrequencyRegulated, old_freq_dev
                
                # Scale the frequency to Hz if BaseFrequency is not 1
                FrequencyDeviation = FrequencyDeviationPU * BaseFrequency
                bspssepy_agc.loc[bspssepy_agc["Gen Name"] == gen_row["MCNAME"], "Δf (Hz)"] = FrequencyDeviation
                # Retrieve the row index of the generator
                row_index = bspssepy_agc.loc[bspssepy_agc["Gen Name"] == gen_row["MCNAME"]].index[0]
                # Calculate the rate of frequency deviation
                
                current_gen_freq_dev_rate = abs(old_freq_dev[row_index]-FrequencyDeviation)/TimeStep
                gen_freq_dev_rate.append(current_gen_freq_dev_rate)
                
                bspssepy_agc.loc[bspssepy_agc["Gen Name"] == gen_row["MCNAME"], "Δf' (Hz/s)"] = current_gen_freq_dev_rate
                
                
                GeneratorFrequencies.append(FrequencyDeviationPU)
                
                old_freq_dev[row_index] = FrequencyDeviation
            else:
                if debug_print:
                    bp(f"[DEBUG] No frequency channel for Bus {bus_num}. Skipping this bus.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                # GeneratorFrequencies.append(0.0)
        else:
            # Set the corresponding alpha to 0 in my bspssepy_agc dataframe --> for GUI purposes here
            bspssepy_agc.loc[bspssepy_agc["Gen Name"] == gen_row["MCNAME"], "Alpha"] = 0
            bspssepy_agc.loc[bspssepy_agc["Gen Name"] == gen_row["MCNAME"], "Δf (Hz)"] = 0
            bspssepy_agc.loc[bspssepy_agc["Gen Name"] == gen_row["MCNAME"], "Δf' (Hz/s)"] = 0
            if debug_print:
                bp(f"[DEBUG] Generator {gen_row['MCNAME']} at Bus {gen_row['NUMBER']} is not in service. The frequency reading won't be used.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
    

    # Calculate the average system frequency deviation
    AverageFrequencyDeviation = np.mean(GeneratorFrequencies)
    if debug_print:
        bp(f"[DEBUG] Average Frequency Deviation: {AverageFrequencyDeviation:.6f} p.u.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    
    # Calculate the rate of average system frequency deviation
    avg_gen_freq_dev_rate = np.mean(gen_freq_dev_rate)
    
    



    # Skip AGC adjustment if frequency deviation is within the deadband
    if (abs(AverageFrequencyDeviation) < Deadband/BaseFrequency) and (avg_gen_freq_dev_rate < Deadband):
        FrequencyRegulated = True
        if debug_print:
            bp(f"[DEBUG] Frequency deviation {AverageFrequencyDeviation*BaseFrequency:.6f} Hz is within deadband (±{Deadband}). No AGC action.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        return bspssepy_gen, bspssepy_agc, FrequencyRegulated, old_freq_dev

    # **Calculate Effective AGC Alpha (Scaling by Active Generators)**
    TotalGens = len(bspssepy_gen[bspssepy_gen["AGCAlpha"] > 0])
    ActiveGens = len(bspssepy_gen[(bspssepy_gen["BSPSSEPyStatus"] == 3) & (bspssepy_gen["AGCAlpha"] > 0)])  # Count only ON generators

    if ActiveGens > 0:
        bspssepy_gen.loc[bspssepy_gen["BSPSSEPyStatus"] == 3, "EffectiveAGCAlpha"] = (
            bspssepy_gen["AGCAlpha"] * (TotalGens / ActiveGens)
        )
    else:
        bspssepy_gen["EffectiveAGCAlpha"] = 0  # No active generators, so set to zero

    if debug_print:
        bp(f"[DEBUG] Effective AGC Alpha Scaling: TotalGens={TotalGens}, ActiveGens={ActiveGens}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    
    # **Adjust Each Generator's Setpoint**
    for idx, gen_row in bspssepy_gen[bspssepy_gen["BSPSSEPyStatus"] == 3].iterrows():
        EffectiveAGCAlpha = gen_row.get("EffectiveAGCAlpha", 0)
        EffectiveBias = gen_row.get("EffectiveBias", 0)
            
        if EffectiveAGCAlpha > 0:
            CurrentSetpoint = await GetGenInfo("PGEN", GenName=gen_row["MCNAME"], debug_print=debug_print, app=app)

            # Compute AGC adjustment based on frequency deviation
            Adjustment = -EffectiveAGCAlpha * AverageFrequencyDeviation * EffectiveBias * (TimeStep / AGCTimeConstant)
            NewSetpoint = max(0, CurrentSetpoint + Adjustment)  # Ensure non-negative setpoint

            if debug_print:
                bp(f"[DEBUG] Generator {gen_row['MCNAME']} at Bus {gen_row['NUMBER']}:", app=app)
                bp(f"        Current Setpoint={CurrentSetpoint:.2f} MW, Adjustment={Adjustment:.2f} MW, New Setpoint={NewSetpoint:.2f} MW", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            # Update generator setpoint in PSSE
            GeneratorName = gen_row["MCNAME"]
            gen_id = gen_row["ID"]
            bus_num = gen_row["NUMBER"]

            # Set the corresponding alpha to EffectiveAGCAlpha in my bspssepy_agc dataframe --> for GUI purposes here
            bspssepy_agc.loc[bspssepy_agc["Gen Name"] == gen_row["MCNAME"], "Alpha"] = EffectiveAGCAlpha

            ierr, gen_mva_base = psspy.macdat(bus_num, gen_id, 'MBASE')
            if ierr == 0 and debug_print:
                bp(f"[DEBUG] Retrieved MVA Base for Generator at Bus {bus_num}, ID {gen_id}: {gen_mva_base} MVA", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            elif ierr != 0:
                bp(f"[ERROR] Could not retrieve MVA Base for Generator at Bus {bus_num}, ID {gen_id}. Error code: {ierr}", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            Adjustment_pu = Adjustment / gen_mva_base
            ierr = psspy.increment_gref(bus_num, gen_id, Adjustment)  # Apply AGC adjustment

            if ierr == 0:
                bspssepy_gen.at[idx, "PGEN"] = NewSetpoint
                bspssepy_agc.loc[bspssepy_agc['Gen Name']==GeneratorName, 'ΔPᴳ'] = NewSetpoint
                if debug_print:
                    bp(f"[DEBUG] Successfully updated {GeneratorName} setpoint - AGC.")
            elif ierr != 0:
                bp(f"[ERROR] Updating setpoint for Generator {GeneratorName} (ID = {gen_id}) at Bus {bus_num}, ierr={ierr}", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)


    if debug_print:
        bp("[DEBUG] AGC Control completed.", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    return bspssepy_gen, bspssepy_agc, FrequencyRegulated, old_freq_dev

