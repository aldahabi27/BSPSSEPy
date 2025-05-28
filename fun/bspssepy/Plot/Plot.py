import psse3601
import psspy
import dyntools
import matplotlib.pyplot as plt
import plotext as pltt
from fun.bspssepy.config.config import config


def BSPSSEPyPlotFreq(config:config, PSSE, debug_print=False, BaseFrequency = 1):
    # Use dyntools to read the output file
    chnf = dyntools.CHNF(str(config.SimOutputFile))

    # Extract data
    short_title, chanid, chandata = chnf.get_data()

    # Debugging: Print file details and channels
    print("Short Title:", short_title)
    print("Channel IDs:", chanid)
    print("Channel Data Keys:", chandata.keys())

    # Check if data is empty
    if not chandata:
        print("The .out file was read but contains no data. Please verify the output channels in PSSE.")


    # Extract time and frequency data
    time = chandata['time']  # Time array
    frequency_channels = [ch for ch in chanid if "freq" in chanid[ch].lower()]

    # Check available frequency channels
    print("Available Frequency Channels:", frequency_channels)

    # Slice data to take every 100th point
    step = 1  # Adjust this step size as needed
    for channel in frequency_channels:
        FreqData = chandata[channel]

        # Heuristic check: If max absolute value is < 1, assume it's in p.u. and scale it
        if max(abs(x) for x in FreqData) < 1:
            FreqData = [x * BaseFrequency for x in FreqData]

        plt.plot(time[::step], FreqData[::step], label=chanid[channel])

    # Add plot labels and legend
    plt.title("Frequency Response (Reduced Points)")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.legend()
    plt.grid(True)
    plt.show()



    # Assuming 'time' and 'chandata' are available
    for channel in frequency_channels:
        pltt.plot(time[::step], chandata[channel][::step])

    pltt.title("Frequency Response (Reduced Points)")
    pltt.xlabel("Time (s)")
    pltt.ylabel("Frequency (Hz)")
    pltt.show()



# def BSPSSEPyPlotGen(config, PSSE, debug_print=False):
#     import matplotlib.pyplot as plt
#     from collections import OrderedDict
#     import dyntools
#     import numpy as np

#     # Use dyntools to read the output file
#     chnf = dyntools.CHNF(str(config.SimOutputFile))

#     # Extract data
#     short_title, chanid, chandata = chnf.get_data()

#     # Debugging: Print file details and channels
#     if debug_print:
#         print("Short Title:", short_title)
#         print("Channel IDs:", chanid)
#         print("Channel Data Keys:", chandata.keys())

#     # Check if data is empty
#     if not chandata:
#         print("The .out file was read but contains no data. Please verify the output channels in PSSE.")
#         return

#     # Time array
#     time = np.array(chandata['time'])/60  # Convert time to minutes

#     # Dynamically search for channels corresponding to quantities
#     quantities = {
#         "GREF": [],
#         "VREF": [],
#         "PELEC": [],
#         "QELEC": [],
#         "PMECH": [],
#         "Frequency": []
#     }

#     # Search for channels in chanid
#     for channel, description in chanid.items():
#         if "gref" in description.lower():
#             quantities["GREF"].append(channel)
#         elif "vref" in description.lower():
#             quantities["VREF"].append(channel)
#         elif "pelec" in description.lower():
#             quantities["PELEC"].append(channel)
#         elif "qelec" in description.lower():
#             quantities["QELEC"].append(channel)
#         elif "pmech" in description.lower():
#             quantities["PMECH"].append(channel)
#         elif "freq" in description.lower():
#             quantities["Frequency"].append(channel)

#     # Debugging: Print identified channels
#     if debug_print:
#         for key, channels in quantities.items():
#             print(f"{key} Channels: {channels}")

#     # Create a 2x3 grid of subplots
#     fig, axes = plt.subplots(2, 3, figsize=(15, 10))
#     fig.suptitle("Generator Quantities", fontsize=16)

#     # Iterate over quantities and plot on the corresponding subplot
#     for idx, (quantity, channels) in enumerate(quantities.items()):
#         row, col = divmod(idx, 3)
#         ax = axes[row, col]

#         # Plot each generator's data for the current quantity
#         for ch in channels:
#             if ch in chandata:
#                 ax.plot(time, chandata[ch], label=chanid[ch])

#         # Set plot title and labels
#         ax.set_title(quantity)
#         ax.set_xlabel("Time (min)")
#         ax.set_ylabel(quantity)
#         ax.legend()
#         ax.grid(True)

#     # Adjust layout and show the plot
#     plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for the main title
#     plt.show()


def BSPSSEPyPlotGen(config, PSSE, debug_print=False, BaseFrequency = 1):
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    from collections import OrderedDict
    import dyntools
    import numpy as np

    # Finish the simulation
    psspy.delete_all_plot_channels()  # Clean up channels (optional)    

    # Use dyntools to read the output file
    chnf = dyntools.CHNF(str(config.SimOutputFile))

    chnf.csvout(outfile=str(config.SimOutputFile), csvfile=str(config.SimOutputFile).replace(".out", ".csv"))

    
    # Extract data
    short_title, chanid, chandata = chnf.get_data()

    # Debugging: Print file details and channels
    if debug_print:
        print("Short Title:", short_title)
        print("Channel IDs:", chanid)
        print("Channel Data Keys:", chandata.keys())

    # Check if data is empty
    if not chandata:
        print("The .out file was read but contains no data. Please verify the output channels in PSSE.")
        return

    # Time array
    time = np.array(chandata['time']) / 60  # Convert time to minutes

    # Dynamically search for channels corresponding to quantities
    quantities = {
        "GREF": [],
        "VREF": [],
        "PELEC": [],
        "QELEC": [],
        "PMECH": [],
        "Frequency": [],
        "Voltage Magnitude": []
    }

    # Search for channels in chanid
    for channel, description in chanid.items():
        if "gref" in description.lower():
            quantities["GREF"].append(channel)
        elif "vref" in description.lower():
            quantities["VREF"].append(channel)
        elif "pelec" in description.lower():
            quantities["PELEC"].append(channel)
        elif "qelec" in description.lower():
            quantities["QELEC"].append(channel)
        elif "pmech" in description.lower():
            quantities["PMECH"].append(channel)
        elif "freq" in description.lower():
            quantities["Frequency"].append(channel)
        elif "volt" in description.lower():  # Adjust as per actual descriptions
            quantities["Voltage Magnitude"].append(channel)

    # Debugging: Print identified channels
    if debug_print:
        for key, channels in quantities.items():
            print(f"{key} Channels: {channels}")

    # Create a 3-row grid: 2x3 for existing plots, 1x3 for voltage magnitudes
    fig = plt.figure(figsize=(9, 9))
    fig.suptitle("Generator Quantities and Voltage Magnitudes", fontsize=16)

    # Use GridSpec to define layout
    gs = GridSpec(3, 3, figure=fig, height_ratios=[1, 1, 0.5])  # Allocate less height for the bottom plot

    # Iterate over quantities and plot on the corresponding subplot
    axes = []
    for idx, (quantity, channels) in enumerate(list(quantities.items())[:-1]):  # Exclude "Voltage Magnitude"
        row, col = divmod(idx, 3)
        ax = fig.add_subplot(gs[row, col])  # Use GridSpec for positioning
        axes.append(ax)

        # Plot each generator's data for the current quantity
        for ch in channels:
            if ch in chandata:
                data = np.array(chandata[ch])  # Convert to numpy array for efficiency
                
                # Apply BaseFrequency scaling to frequency channels only
                if quantity == "Frequency":
                    if np.max(np.abs(data)) < 1:  # If data is in pu, scale it
                        data *= BaseFrequency

                ax.plot(time, data, label=chanid[ch])

        # Set plot title and labels
        ax.set_title(quantity)
        ax.set_xlabel("Time (min)")
        ax.set_ylabel(quantity)
        ax.legend()
        ax.grid(True)

    # Plot all voltage magnitudes on the last row (1x3 big subplot)
    voltage_ax = fig.add_subplot(gs[2, :])  # Span the entire bottom row

    for ch in quantities["Voltage Magnitude"]:
        if ch in chandata and len(chandata[ch]) == len(time):  # Ensure time and data lengths match
            voltage_ax.plot(time, chandata[ch], label=chanid[ch])
        else:
            print(f"Skipping channel {ch} due to mismatched data length.")

    voltage_ax.set_title("Voltage Magnitudes")
    voltage_ax.set_xlabel("Time (min)")
    voltage_ax.set_ylabel("Voltage (pu)")
    voltage_ax.legend()
    voltage_ax.grid(True)

    # Adjust layout and show the plot
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for the main title
    plt.show()


import os
import csv
import numpy as np
import dyntools
from pathlib import Path
from typing import Union


def bspssepy_export_to_csv(
    output_file: Union[str, os.PathLike, Path],
    debug_print: bool = False
) -> None:
    """
    Extracts data from a PSS/E .out file and exports it to a CSV file.

    Parameters:
        output_file (str | os.PathLike | Path): Path to the .out file.
        debug_print (bool): If True, prints debugging information.

    Output:
        - A CSV file is created in the same directory as the .out file.
        - The first column contains 'time' (in seconds).
        - Subsequent columns contain all available simulation channels.
    """
    output_path = Path(output_file)  # Ensure it's a Path object

    # Ensure the file exists
    if not output_path.exists() or output_path.suffix != ".out":
        print(f"ERROR: File not found or incorrect format: {output_path}")
        return

    # Define the CSV output file path (same directory, different extension)
    csv_file = output_path.with_suffix(".csv")

    # load the .out file using dyntools
    chnf = dyntools.CHNF(str(output_path))
    short_title, chan_id, chan_data = chnf.get_data()

    # Debugging output
    if debug_print:
        print(f"Exporting Data to: {csv_file}")
        print(f"Short Title: {short_title}")
        print(f"Channel IDs: {chan_id}")
        print(f"Channel Data Keys: {chan_data.keys()}")

    # Ensure there's data to export
    if not chan_data:
        print("ERROR: The .out file was read but contains no data.")
        return

    # Extract time column (ensure it's in seconds)
    time = np.array(chan_data['time'])  

    # Write the extracted data to CSV
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Create headers (Time + Channel Names)
        headers = ["time (s)"] + [chan_id[ch] for ch in chan_id.keys() if ch != 'time']
        writer.writerow(headers)

        # Write simulation data
        for i in range(len(time)):
            row = [time[i]] + [chan_data[ch][i] for ch in chan_id.keys() if ch != 'time']
            writer.writerow(row)

    print(f"✅ Export successful! Data saved to: {csv_file}")


# Example Usage:
# bspssepy_export_to_csv("C:/path/to/your/output_file.out", debug_print=True)
