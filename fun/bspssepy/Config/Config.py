# ===========================================================
#   BSPSSEPy Application - Configuration Class
# ===========================================================
#   This class handles reading configuration files and setting up
#   simulation parameters for BSPSSEPy.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================
"""
    The config class manages the loading of configuration files and setting up
    various simulation parameters for the BSPSSEPy framework.

    Attributes:
        CaseName (str): The name of the power system case.
        Ver (int): The version number of the case.
        debug_print (bool): Enables debug messages when True.
        NumberOfBuses (int): The number of buses in the system.
        VoltageFlag (int): Determines voltage monitoring behavior.
        FrequencyFlag (int): Determines frequency monitoring behavior.
        PSSEMaxIterationNewtonRaphson (int): Max iterations for power flow.
        SimulationTimeStep (float): Time step for the dynamic simulation.
        Simulationfreqfilter (float): Frequency filtering time constant.
        IgnoreCNVFile (bool): If True, regenerates the CNV file.
        IgnoreSNPFile (bool): If True, regenerates the SNP file.
        BSPSSEPyHardTimeLimit (int): Enforces a hard time limit on simulation.
        BSPSSEPyTimeStep (int): Controls time-dependent actions execution rate.
        BSPSSEPyProgressPrintTime (int): Frequency of progress messages.
"""
import os
import asyncio
from pathlib import Path
import importlib.util
import datetime
import pandas as pd
from .LoadConfig import LoadConfig
from .CSVControlPlanConfig import BSPSSEPyControlSequenceTable
from fun.bspssepy.app.app_helper_funs import bp

class config:
    def __init__(self, ConfigPath=None, CaseName=None, Ver=None, debug_print=None, app=None):
        pass
    async def ConfigInit(self, ConfigPath=None, CaseName=None, Ver=None, debug_print=None, app=None):
        """
        Initializes the config class with default values or loads from a configuration file.
        
        Parameters:
            ConfigPath (str): The path to the configuration file. If None, default values are used.
            CaseName (str): The name of the power system case.
            Ver (int): The version of the case.
            debug_print (bool): Enables debug messages when True.
        """

        if (debug_print is None) and app:
            debug_print = app.debug_checkbox.value

        if debug_print:
            bp("[DEBUG] Entering config Constructor...", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Default value for CaseName
        # The name of the case, which should match the case folder name. 
        # This is used to locate case-specific data files (e.g., *.sav files).
        self.CaseName = ""  # Default is an empty string, should match the name of the case folder exactly.
        
        # Default value for Ver (Version)
        # The version number derived from the .sav file name (e.g., 3Bus_Ver2.sav). If no version is specified,
        # the default value is -1. This helps identify the specific configuration version of the case.
        self.Ver = -1  # Default is -1, meaning no version specified.

        # Default value for NumberOfBuses
        # Specifies the number of buses in the system. If this value is unknown or not provided,
        # setting it to 0 will prompt the code to automatically derive this from the case data.
        # This is useful for cases where the user might not know the exact number of buses ahead of time.
        self.NumberOfBuses = 0  # Default is 0, which will trigger automatic calculation from case data.

        # Default value for BusesToMonitor_Voltage
        # This is a list of buses whose voltage is to be monitored during the simulation.
        # The user can specify specific buses (e.g., [1, 2, 3]) or use a range notation to specify a range of buses.
        # This can be used to focus on specific buses for voltage monitoring, which helps in monitoring system stability.
        self.BusesToMonitor_Voltage = []  # Default is an empty list. User can specify buses to monitor.

        # Default value for BusesToMonitor_Frequency
        # This is a list of buses whose frequency is to be monitored during the simulation.
        # Similar to voltage monitoring, this can be used to track frequency at specific buses of interest.
        self.BusesToMonitor_Frequency = []  # Default is an empty list. User can specify buses to monitor for frequency.

        # Default value for VoltageFlag
        # This flag controls how the voltage monitoring works:
        #   0: Use the buses specified in BusesToMonitor_Voltage.
        #   1: Monitor all generator buses.
        #   2: Monitor all transformer buses.
        #   3: Monitor both generator and transformer buses.
        #   4: Monitor all load buses.
        #   5: Monitor all buses.
        # This gives the user flexibility in selecting which buses to monitor for voltage.
        self.VoltageFlag = 0  # Default is 0 (use the buses specified in BusesToMonitor_Voltage).

        # Default value for FrequencyFlag
        # This flag controls how the frequency monitoring works:
        #   0: Use the buses specified in BusesToMonitor_Frequency.
        #   1: Monitor all generator buses.
        #   2: Monitor all transformer buses.
        #   3: Monitor both generator and transformer buses.
        #   4: Monitor all load buses.
        #   5: Monitor all buses.
        # This flag offers flexibility in monitoring frequency at various locations in the system.
        self.FrequencyFlag = 0  # Default is 0 (use the buses specified in BusesToMonitor_Frequency).

        # Default value for SimulationTimeStep
        # This specifies the time step for the simulation in seconds. The default value is set to 1ms (0.001 seconds),
        # which is typically used for high-resolution simulations in power systems.
        # The user can change this to smaller or larger time steps depending on the simulation accuracy needed.
        self.SimulationTimeStep = 1e-3  # Default is 1ms (0.001 seconds).

        # Default value for Simulationfreqfilter
        # This specifies the frequency filtering threshold for the simulation in seconds. The default value is
        # 4 times the SimulationTimeStep. This helps smooth out high-frequency noise during simulations.
        self.Simulationfreqfilter = 4 * self.SimulationTimeStep  # Default is 4 times the SimulationTimeStep.

        # Default value for PSSEMaxIterationNewtonRaphson
        # This specifies the maximum number of iterations allowed for the PSSE Newton-Raphson solver during power flow calculations.
        # Increasing the number may improve convergence for complex systems, but it also increases computation time.
        self.PSSEMaxIterationNewtonRaphson = 100  # Default is 100 iterations.

        # Default value for IgnoreCNVFile
        # If set to True, this forces regeneration of the CNV file, regardless of its existence.
        # The CNV file is used for system network data and is generated during the power flow analysis.
        self.IgnoreCNVFile = False  # Default is False, meaning the CNV file will be reused if it exists.

        # Default value for IgnoreSNPFile
        # If set to True, this forces regeneration of the SNP file, regardless of its existence.
        # The SNP file is used for storing system snapshot data during simulations.
        self.IgnoreSNPFile = False  # Default is False, meaning the SNP file will be reused if it exists.

        # assign debug_print to self.debug_print
        self.debug_print = debug_print

        # BSPSSEPy Hard Time Limit in minutes (ignored if BSPSSEPyHardTimeLimitFlag is False)
        self.BSPSSEPyHardTimeLimit = 1 #minutes

        # If true, BSPSSEPy will enforce a hard time limit on the simulation.
        self.BSPSSEPyHardTimeLimitFlag = True

        # BSPSSEPy Time Step in seconds
        # This timestep controls the python functions execution rate.
        # This controls AGC, control actions, and other time-dependent functions.
        # Default is 1 second.
        # Note: This is different from the simulation time step specified for dynamic modeling in PSSE.
        self.BSPSSEPyTimeStep = 1 #seconds


        # BSPSSEPyProgressPrintTime controls the frequency of progress print messages in minutes.
        self.BSPSSEPyProgressPrintTime = 1 #minutes

        # Starting from Channel 1
        self.CurrentChannelIndex = 1

        # Channels mapping for monitoring
        self.Channels = []  # Stores channel-related information for monitoring
  
        # Channels Format:
        # Each entry in the `self.Channels` list will be a dictionary containing the following keys:
        #     - "Channel Type": The type of channel (e.g., "Frequency", "Voltage", "Angle", "Current").
        #     - "Bus Number": The bus number being monitored (if applicable).
        #     - "Element Index": Index of the element being monitored (e.g., generator number, branch index).
        #     - "Element Name": Name of the element being monitored (e.g., bus name, generator name).
        #     - "Channel Index": The channel index assigned by PSSE.
        #     - "Additional Info": Any other relevant details (e.g., phase, measurement units).

        # Example:
        # self.Channels = [
        #     {
        #         "Channel Type": "Frequency",
        #         "Bus Number": 1,
        #         "Element Index": 1,
        #         "Element Name": "Bus1",
        #         "Channel Index": 10,
        #         "Additional Info": "Frequency deviation in Hz"
        #     },
        #     {
        #         "Channel Type": "Voltage",
        #         "Bus Number": 2,
        #         "Element Index": 2,
        #         "Element Name": "Bus2",
        #         "Channel Index": 11,
        #         "Additional Info": "Voltage magnitude in pu"
        #     }
        # ]

        # Default value for GeneratorConfig
        # This specifies the configuration of generators in the system. Each NBS generator (non-blackstart generator) should have the following attributes:
        #   - Generator Name: The unique name of the generator
        #   - Bus Name: Name of the associated bus
        #   - Status: Initial status of the generator ("OFF", "Cranking", etc.)
        #   - load Name: Name of the corresponding cranking load (if any)
        #   - Cranking Time: Duration of the cranking phase
        #   - Ramp Rate: Ramp-up rate
        #   - Generator Type: "NBS" (Non-Black-Start) or "BS" (Black-Start)
        #   - Cranking load Array: Power array [PL, QL, IP, IQ, YP, YQ, Power Factor]
        #
        #   For BS Generators, the status should be "ON", and the rest of the parameters are all ignored.
        self.GeneratorsConfig = []  # Default is an empty list.

        self.EnforceActionLock = True  # Flag to enforce checking action lock logic
        
        self.ControlSequenceAsIs = False
        # If True, the control sequence is executed as is without looking at action time.
        # To set this to True, EnforceActionLock must be True (to excute actions sequentially).
        # If True and EnforceActionLock is False, program will throw an error and exits.
        # If False, the program will execute the control sequence based on the action time.
        
        self.BypassTiedActions = True  # Flag to excute TiedActions with their main action. If an action is linked/tied to others, it will be executed with them.

        self.AccountForActionExecutionDelays = True  # If True, the system will adjust action timings to compensate for unforeseen execution delays (e.g., AGC frequency regulation or prolonged generator startup) while maintaining the planned time gaps.

        
        self.EnforceFrequencySafetyMargin = True  # If True, the program will enforce a safety margin on the frequency to avoid
                                     # the frequency to go below FreqSafetyMarginMin or above FreqSafetyMarginMax. 
        self.FreqSafetyMarginMin = 59.5  # Minimum frequency allowed in Hz
        self.FreqSafetyMarginMax = 60.5  # Maximum frequency allowed in Hz

        # Note: If EnforceFrequencySafetyMargin is True, the system will wait until "AGC" regulate the frequency to be within limits before executing the next action.
        #       If EnforceFrequencySafetyMargin is False, the system will execute the next action regardless of the frequency.

        self.TieActionsByExecutionTime = False  # If True, actions will be tied by their execution time. If action is also "tied" by their "values" information, they will be part of the parent 

        self.delay_agc_after_action = 0 # seconds -- delay AGC after action execution
                                        # if ~= 0, AGC internal states will be reset everytime a new action is executed

        if debug_print:
            bp("[DEBUG] Default attributes initialized.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        # await asyncio.sleep(app.async_print_delay if app else 0)

        # Define main project directory
        self.MainFolder = Path(os.getcwd())  # Current working directory

        # Define ConfigPath based on CaseName and Ver
        if CaseName is not None:
            if Ver is not None and Ver > 0:
                ConfigPath = self.MainFolder / "Case" / CaseName / f"{CaseName}_Ver{Ver}_Config.py"
            else:
                ConfigPath = self.MainFolder / "Case" / CaseName / f"{CaseName}_Config.py"
            if debug_print:
                bp(f"[DEBUG] ConfigPath derived from CaseName and Version: {ConfigPath}", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

        elif ConfigPath:
            # ConfigPath = Path(ConfigPath)
            if debug_print:
                bp(f"[DEBUG] ConfigPath provided directly: {ConfigPath}", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

        # await asyncio.sleep(app.async_print_delay if app else 0)

        if isinstance(ConfigPath, str):
            ConfigPath = Path(ConfigPath)
        

        bp(f'Attempting to load configuration file "{ConfigPath.name}"', app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

        if ConfigPath and ConfigPath.exists():
            if debug_print:
                bp("[DEBUG] Loading configuration from file...", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            await LoadConfig(self=self, ConfigPath=ConfigPath, debug_print=debug_print,app=app)
            if debug_print:
                bp("[DEBUG] Configuration file loaded successfully.", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
        else:
            if debug_print:
                bp("[DEBUG] ConfigPath not provided or file does not exist. Using default values.", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

        # at this stage, if debug_print is None, this indicates that neither ConfigFile or debug_print in the main code is set.
        if debug_print is not None:
            # Default value for debug_print
            self.debug_print = debug_print  # Default is False, set to True for debugging purposes.
            # debug_print = False
        elif self.debug_print is None:
            self.debug_print = False
            
        debug_print = self.debug_print

        # Prepare directories for the case
        self.CaseFolder = self.MainFolder / f"Case/{self.CaseName}"
        self.LogsFolder = self.CaseFolder / "Logs"
        self.SimFolder = self.CaseFolder / "Simulations"

        # Ensure all required directories exist
        await self._CreateDirectory(self.CaseFolder, "Case directory", app=app)
        await self._CreateDirectory(self.LogsFolder, "Logs directory", app=app)
        await self._CreateDirectory(self.SimFolder, "Simulations directory", app=app)
        # await asyncio.sleep(app.async_print_delay if app else 0)


        if debug_print:
            bp("[DEBUG] Required directories ensured.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Record the current system time
        self.SysTime = datetime.datetime.now()
        self.SysFormattedTime = self.SysTime.strftime("%H%M%S_%d%m%y")  # Format: hhmmss_DDMMYY

        if debug_print:
            bp(f"[DEBUG] System time recorded: {self.SysTime}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            

        # Define simulation-related file paths based on the case version.

        BaseCaseName = f"{self.CaseName}_Ver{self.Ver}" if self.Ver >= 1 else self.CaseName

        self.sav_file = self.CaseFolder / f"{BaseCaseName}.sav"
        self.DYRFile = self.CaseFolder / f"{BaseCaseName}.dyr"
        self.CNVFile = self.CaseFolder / f"{BaseCaseName}.cnv"
        self.SNPFile = self.CaseFolder / f"{BaseCaseName}.snp"
        self.LogFile = self.LogsFolder / f"{BaseCaseName}_{self.SysFormattedTime}.log"
        self.ConvCodeFile = self.CaseFolder / f"{BaseCaseName}_Conv.py"
        self.SimOutputFile = self.SimFolder / f"{BaseCaseName}_{self.SysFormattedTime}.out"
        self.CSVControlPlan = self.CaseFolder / f"{BaseCaseName}.csv"
        self.AllDevicesList = self.CaseFolder / f"{BaseCaseName}_AllDevices.csv"


        if debug_print:
            bp("[DEBUG] Simulation-related file paths defined.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            # await asyncio.sleep(app.async_print_delay if app else 0)



            
            
        # Read the CSV file into a DataFrame
        self.bspssepy_sequence = await BSPSSEPyControlSequenceTable(self.CSVControlPlan, debug_print=debug_print, app=app)
        
        self.bspssepy_sequence.insert(0, "Control Sequence", 0)
        self.bspssepy_sequence.insert(0, "Start Time", 0)
        self.bspssepy_sequence.insert(0, "End Time", 0)

        
        
        if self.TieActionsByExecutionTime:
            """
            If enabled, this logic ensures that actions occurring at the same "Action Time"
            are grouped under the first action of that time as the reference. 
            The "Tied Action" column will store the UID of the first action with that time.
            """

            # Dictionary to track the first UID for each "Action Time"
            ActionTimeToUID = {}

            for idx in self.bspssepy_sequence.index:
                action_time = self.bspssepy_sequence.at[idx, "Action Time"]
                UID = self.bspssepy_sequence.at[idx, "UID"]

                # If this Action Time was not seen before, set it as the reference UID
                if action_time not in ActionTimeToUID:
                    ActionTimeToUID[action_time] = UID  # Store this UID as the main reference
                    self.bspssepy_sequence.at[idx, "Tied Action"] = -1  # Mark main action
                else:
                    # Set "Tied Action" to reference the first action's UID
                    self.bspssepy_sequence.at[idx, "Tied Action"] = ActionTimeToUID[action_time]

        with pd.option_context(
            "display.max_rows", None,  # Show all rows
            "display.max_columns", None,  # Show all columns
            "display.width", 0,  # Auto-adjust width for full visibility
            "display.colheader_justify", "center",  # Center column headers for readability
        ):
            bp(self.bspssepy_sequence.to_string(index=False))
            await asyncio.sleep(app.async_print_delay if app else 0)


        
        
        
        
        if not self.ControlSequenceAsIs:
            # Sort by "Action Time" first, then by "Tied Action" to ensure grouped execution
            self.bspssepy_sequence: pd.DataFrame = self.bspssepy_sequence.sort_values(
                by=["Action Time", "Tied Action"], 
                ascending=[True, True],  # Ensure actions follow the planned sequence
                na_position="last"  # Put missing Tied Actions at the end
            ).reset_index(drop=True)  # Reset index after sorting
        else:
            # Create a new DataFrame to store the reordered sequence
            ReorderedSequence = []

            # Convert DataFrame to a list of dictionaries for easier manipulation
            SequenceList = self.bspssepy_sequence.to_dict(orient="records")

            # Track actions that have tied actions
            ProcessedUIDs = set()

            for action in SequenceList:
                UID = action["UID"]
                TiedAction = action["Tied Action"]

                if TiedAction != -1:
                    continue

                # Skip if already added (to avoid duplication)
                if UID in ProcessedUIDs:
                    continue
                
                
                # Add the main action first
                ReorderedSequence.append(action)
                ProcessedUIDs.add(UID)

                # Find and move tied actions immediately after their parent action
                TiedActions = [a for a in SequenceList if str(a.get("Tied Action", "")) == str(UID)]
                for tied_action in TiedActions:
                    ReorderedSequence.append(tied_action)
                    ProcessedUIDs.add(tied_action["UID"])  # Mark as processed

            # Convert back to DataFrame
            self.bspssepy_sequence = pd.DataFrame(ReorderedSequence)

        
        # bp(self.bspssepy_sequence)
        # await asyncio.sleep(app.async_print_delay if app else 0)


        # Track the control sequence number
        ControlSequenceIndex = 1  

        # Iterate over the DataFrame and assign control sequence numbers
        for idx in self.bspssepy_sequence.index:
            TiedAction = self.bspssepy_sequence.at[idx, "Tied Action"]
            
            # If it's a main action (not tied to anything)
            if TiedAction == -1:
                self.bspssepy_sequence.at[idx, "Control Sequence"] = ControlSequenceIndex
                
                # If BypassTiedActions is enabled, make tied actions share the same sequence number
                if self.BypassTiedActions:
                    TiedActions = self.bspssepy_sequence[self.bspssepy_sequence["Tied Action"] == self.bspssepy_sequence.at[idx, "UID"]]
                    for tied_idx in TiedActions.index:
                        self.bspssepy_sequence.at[tied_idx, "Control Sequence"] = ControlSequenceIndex

                # Increment sequence index for the next main action
                ControlSequenceIndex += 1

            # If BypassTiedActions is False, assign a new control sequence to each tied action
            elif not self.BypassTiedActions:
                self.bspssepy_sequence.at[idx, "Control Sequence"] = ControlSequenceIndex
                ControlSequenceIndex += 1  # Increment sequence for each action (including tied ones)

        # Debug print the final sequence
        if debug_print:
            bp("[DEBUG] Control sequence table updated with correct sequence numbers.", app=app)
            bp(self.bspssepy_sequence)
            await asyncio.sleep(app.async_print_delay if app else 0)
            
        # bp(self.bspssepy_sequence)
        # await asyncio.sleep(app.async_print_delay if app else 0)

        
        if debug_print:
            bp("[DEBUG] Control sequence table loaded.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            # await asyncio.sleep(app.async_print_delay if app else 0)


        with pd.option_context(
            "display.max_rows", None,  # Show all rows
            "display.max_columns", None,  # Show all columns
            "display.width", 0,  # Auto-adjust width for full visibility
            "display.colheader_justify", "center",  # Center column headers for readability
        ):
            bp(self.bspssepy_sequence.to_string(index=False))
            await asyncio.sleep(app.async_print_delay if app else 0)




    async def _CreateDirectory(self, directory_path, description, app=None):
        """
        Create a directory if it does not exist.

        Parameters:
        - directory_path (Path): Path of the directory to create.
        - description (str): Description of the directory for logging purposes.
        """
        if not directory_path.exists():
            directory_path.mkdir()
            bp(f"Created {description} at: {directory_path}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

            if self.debug_print:
                bp(f"[DEBUG] {description} created at: {directory_path}", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
        elif self.debug_print:
            bp(f"[DEBUG] {description} already exists: {directory_path}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)