import psspy
import dyntools
import matplotlib.pyplot as plt
import plotext as pltt


def BSPSSEPyPlotFreq(SimOutputFile):
    # Use dyntools to read the output file
    chnf = dyntools.CHNF(str(SimOutputFile))

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
        plt.plot(time[::step], chandata[channel][::step], label=chanid[channel])

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