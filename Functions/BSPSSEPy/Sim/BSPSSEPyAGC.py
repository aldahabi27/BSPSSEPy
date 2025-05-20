import numpy as np
import pandas as pd
import psse3601
import psspy
from .BSPSSEPyGenFunctions import GetGenInfo
from .BSPSSEPyChannels import FetchChannelValue, FetchChannelValuesFromOUTFile
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint
import asyncio
from dyntools import CHNF



async def FetchFrequencyFromOUTFile(OUTFile, ChannelIndex, DebugPrint=False, app=None):
    """
    Fetches frequency data from the .out file for a specific channel.

    Parameters:
        OUTFile (str): Path to the .out file.
        ChannelIndex (int): The channel index corresponding to the desired frequency data.
        DebugPrint (bool): If True, prints debug information.

    Returns:
        list: Frequency data from the specified channel.

    Notes:
        - This function extracts the entire time-series data for the given channel index.
        - It uses dyntools to read data from the .out file.
    """
    return await FetchChannelValuesFromOUTFile(OUTFile, ChannelIndex, DebugPrint, app=app)


async def FetchFrequency(ChannelIndex, OUTFile=None, DebugPrint=False, app=None):
    """
    Attempts to fetch frequency data using psspy.chnval. If it fails, falls back to dyntools.

    Parameters:
        ChannelIndex (int): Channel index for retrieving frequency data via PSSE.
        OUTFile (str, optional): Path to the .out file for fallback in case of errors.
        DebugPrint (bool): If True, prints debug information.

    Returns:
        float: The most recent frequency value.

    Notes:
        - This function first tries to fetch the data using psspy.chnval for real-time values.
        - If psspy.chnval fails, it retrieves the most recent value from the .out file.
    """
    return await FetchChannelValue(ChannelIndex, OUTFile, DebugPrint,app=app)






async def AGCControl(
        BSPSSEPyGen: pd.DataFrame,
        BSPSSEPyAGCDF: pd.DataFrame,
        Channels,
        OUTFile=None,
        UseOutFile=False,
        TimeStep=1.0,
        AGCTimeConstant=60.0,
        Deadband=0.001, # in Hz
        DebugPrint: bool | None = False,
        app=None,
        BaseFrequency = 1,
        FrequencyRegulated: bool | None = False,
        old_freq_dev: float | None = 0,  # Δf[k-1] (Hz)
        ):
    """
    Perform Automatic Generation Control (AGC) using frequency deviation data.

    Parameters:
        BSPSSEPyGen (pd.DataFrame): DataFrame containing generator data with the following columns:
            - "AGC Participation Factor"
            - "Bus Number"
            - "Generator Name"
        BSPSSEPyAGCDF (pd.DataFrame): DataFrame containing summary of AGC status per generator, mainly used
        for GUI updates and tracking of actions.
        Channels (list): List of channel mappings (from Config.Channels).
        OUTFile (str, optional): Path to the .out file for fallback frequency data retrieval.
        UseOutFile (bool): If True, always uses the .out file for frequency retrieval.
        TimeStep (float): Simulation time step in seconds.
        AGCTimeConstant (float): Time constant for the first-order AGC adjustment in seconds.
        Deadband (float): Deadband for AGC action in Hz.
        DebugPrint (bool): If True, prints detailed debug information.

    Returns:
        pd.DataFrame: Updated DataFrame with adjusted generator setpoints.
    """
    
    # Build a mapping of bus numbers to frequency channel indices
    FrequencyChannels = {
        channel["Bus Number"]: channel["Channel Index"]
        for channel in Channels
        if channel["Channel Type"] == "Frequency"
    }

    if DebugPrint:
        bsprint("[DEBUG] Frequency Channels Mapping:", FrequencyChannels, app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)


    # Fetch frequency deviations for all generators
    GeneratorFrequencies = []
    gen_freq_dev_rate = []
    # bsprint(BSPSSEPyGen["BSPSSEPyStatus"])
    for _, GeneratorRow in BSPSSEPyGen.iterrows():
        BusNumber = GeneratorRow['NUMBER']
        ChannelIndex = FrequencyChannels.get(BusNumber, None)
        # bsprint(BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF["Gen Name"] == GeneratorRow["MCNAME"]])
        # await asyncio.sleep(app.bsprintasynciotime if app else 0)

        if GeneratorRow["BSPSSEPyStatus"] == 3:    
            if ChannelIndex is not None:
                # Use either the `.out` file or `psspy.chnval` based on the UseOutFile flag
                if UseOutFile and OUTFile:
                    FrequencyDeviationPU = await FetchFrequencyFromOUTFile(OUTFile, ChannelIndex, DebugPrint, app=app)[-1]
                else:
                    FrequencyDeviationPU = await FetchFrequency(ChannelIndex, OUTFile if not UseOutFile else None, DebugPrint,app=app)

                # Handle NaN values (no AGC action if frequency is NaN)
                if np.isnan(FrequencyDeviationPU):
                    bsprint("[WARNING] NAN frequency deviation detected. NO AGC Action will be taken.", app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                    return BSPSSEPyGen, BSPSSEPyAGCDF, FrequencyRegulated, old_freq_dev
                
                # Scale the frequency to Hz if BaseFrequency is not 1
                FrequencyDeviation = FrequencyDeviationPU * BaseFrequency
                BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF["Gen Name"] == GeneratorRow["MCNAME"], "Δf (Hz)"] = FrequencyDeviation
                # Retrieve the row index of the generator
                row_index = BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF["Gen Name"] == GeneratorRow["MCNAME"]].index[0]
                # Calculate the rate of frequency deviation
                
                current_gen_freq_dev_rate = abs(old_freq_dev[row_index]-FrequencyDeviation)/TimeStep
                gen_freq_dev_rate.append(current_gen_freq_dev_rate)
                
                BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF["Gen Name"] == GeneratorRow["MCNAME"], "Δf' (Hz/s)"] = current_gen_freq_dev_rate
                
                
                GeneratorFrequencies.append(FrequencyDeviationPU)
                
                old_freq_dev[row_index] = FrequencyDeviation
            else:
                if DebugPrint:
                    bsprint(f"[DEBUG] No frequency channel for Bus {BusNumber}. Skipping this bus.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                # GeneratorFrequencies.append(0.0)
        else:
            # Set the corresponding alpha to 0 in my BSPSSEPyAGCDF dataframe --> for GUI purposes here
            BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF["Gen Name"] == GeneratorRow["MCNAME"], "Alpha"] = 0
            BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF["Gen Name"] == GeneratorRow["MCNAME"], "Δf (Hz)"] = 0
            BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF["Gen Name"] == GeneratorRow["MCNAME"], "Δf' (Hz/s)"] = 0
            if DebugPrint:
                bsprint(f"[DEBUG] Generator {GeneratorRow['MCNAME']} at Bus {GeneratorRow['NUMBER']} is not in service. The frequency reading won't be used.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
    

    # Calculate the average system frequency deviation
    AverageFrequencyDeviation = np.mean(GeneratorFrequencies)
    if DebugPrint:
        bsprint(f"[DEBUG] Average Frequency Deviation: {AverageFrequencyDeviation:.6f} p.u.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    
    # Calculate the rate of average system frequency deviation
    avg_gen_freq_dev_rate = np.mean(gen_freq_dev_rate)
    
    



    # Skip AGC adjustment if frequency deviation is within the deadband
    if (abs(AverageFrequencyDeviation) < Deadband/BaseFrequency) and (avg_gen_freq_dev_rate < Deadband):
        FrequencyRegulated = True
        if DebugPrint:
            bsprint(f"[DEBUG] Frequency deviation {AverageFrequencyDeviation*BaseFrequency:.6f} Hz is within deadband (±{Deadband}). No AGC action.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        return BSPSSEPyGen, BSPSSEPyAGCDF, FrequencyRegulated, old_freq_dev

    # **Calculate Effective AGC Alpha (Scaling by Active Generators)**
    TotalGens = len(BSPSSEPyGen[BSPSSEPyGen["AGCAlpha"] > 0])
    ActiveGens = len(BSPSSEPyGen[(BSPSSEPyGen["BSPSSEPyStatus"] == 3) & (BSPSSEPyGen["AGCAlpha"] > 0)])  # Count only ON generators

    if ActiveGens > 0:
        BSPSSEPyGen.loc[BSPSSEPyGen["BSPSSEPyStatus"] == 3, "EffectiveAGCAlpha"] = (
            BSPSSEPyGen["AGCAlpha"] * (TotalGens / ActiveGens)
        )
    else:
        BSPSSEPyGen["EffectiveAGCAlpha"] = 0  # No active generators, so set to zero

    if DebugPrint:
        bsprint(f"[DEBUG] Effective AGC Alpha Scaling: TotalGens={TotalGens}, ActiveGens={ActiveGens}", app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    
    # **Adjust Each Generator's Setpoint**
    for idx, GeneratorRow in BSPSSEPyGen[BSPSSEPyGen["BSPSSEPyStatus"] == 3].iterrows():
        EffectiveAGCAlpha = GeneratorRow.get("EffectiveAGCAlpha", 0)
        EffectiveBias = GeneratorRow.get("EffectiveBias", 0)
            
        if EffectiveAGCAlpha > 0:
            CurrentSetpoint = await GetGenInfo("PGEN", GenName=GeneratorRow["MCNAME"], DebugPrint=DebugPrint, app=app)

            # Compute AGC adjustment based on frequency deviation
            Adjustment = -EffectiveAGCAlpha * AverageFrequencyDeviation * EffectiveBias * (TimeStep / AGCTimeConstant)
            NewSetpoint = max(0, CurrentSetpoint + Adjustment)  # Ensure non-negative setpoint

            if DebugPrint:
                bsprint(f"[DEBUG] Generator {GeneratorRow['MCNAME']} at Bus {GeneratorRow['NUMBER']}:", app=app)
                bsprint(f"        Current Setpoint={CurrentSetpoint:.2f} MW, Adjustment={Adjustment:.2f} MW, New Setpoint={NewSetpoint:.2f} MW", app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            # Update generator setpoint in PSSE
            GeneratorName = GeneratorRow["MCNAME"]
            GeneratorID = GeneratorRow["ID"]
            BusNumber = GeneratorRow["NUMBER"]

            # Set the corresponding alpha to EffectiveAGCAlpha in my BSPSSEPyAGCDF dataframe --> for GUI purposes here
            BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF["Gen Name"] == GeneratorRow["MCNAME"], "Alpha"] = EffectiveAGCAlpha

            ierr, GeneratorMVA_Base = psspy.macdat(BusNumber, GeneratorID, 'MBASE')
            if ierr == 0 and DebugPrint:
                bsprint(f"[DEBUG] Retrieved MVA Base for Generator at Bus {BusNumber}, ID {GeneratorID}: {GeneratorMVA_Base} MVA", app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            elif ierr != 0:
                bsprint(f"[ERROR] Could not retrieve MVA Base for Generator at Bus {BusNumber}, ID {GeneratorID}. Error code: {ierr}", app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            Adjustment_pu = Adjustment / GeneratorMVA_Base
            ierr = psspy.increment_gref(BusNumber, GeneratorID, Adjustment)  # Apply AGC adjustment

            if ierr == 0:
                BSPSSEPyGen.at[idx, "PGEN"] = NewSetpoint
                BSPSSEPyAGCDF.loc[BSPSSEPyAGCDF['Gen Name']==GeneratorName, 'ΔPᴳ'] = NewSetpoint
                if DebugPrint:
                    bsprint(f"[DEBUG] Successfully updated {GeneratorName} setpoint - AGC.")
            elif ierr != 0:
                bsprint(f"[ERROR] Updating setpoint for Generator {GeneratorName} (ID = {GeneratorID}) at Bus {BusNumber}, ierr={ierr}", app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)


    if DebugPrint:
        bsprint("[DEBUG] AGC Control completed.", app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    return BSPSSEPyGen, BSPSSEPyAGCDF, FrequencyRegulated, old_freq_dev

