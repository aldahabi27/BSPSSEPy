# ===========================================================
#   BSPSSEPy Application - Simulation Class
# ===========================================================
#   This module handles the execution of dynamic power system 
#   simulations using PSSE. It sets up system elements, initializes
#   simulation parameters, and executes simulation runs.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================

import psse3601
import psspy
import sys
import os

from .bspssepy_brn_funs import *
from .bspssepy_bus_funs import *
from .bspssepy_default_vars import *
from .bspssepy_gen_funs import *
from .bspssepy_load_funs import *
from .bspssepy_trn_funs import *
from fun.bspssepy.bspssepy_dict import *
from fun.bspssepy.bspssepy_funs_dict import *
from .bspssepy_agc import *
from .bspssepy_channels import GetAvgFrequency
from fun.bspssepy.app.app_helper_funs import bp, ProgressBarUpdate
import asyncio


class sim:
    """
    The sim class handles the execution of the power system simulation.
    It initializes system elements, sets up monitoring channels, 
    and runs dynamic simulation cases using PSSE.

    Attributes:
        config (config): The simulation configuration object.
        PSSE (PSSE): The PSSE instance used for simulation operations.
        debug_print (bool): Enables debug messages when True.
        EnforceActionLock (bool): Ensures sequential action execution.
        ActionInProgress (bool): Tracks if an action is currently executing.
        Action (dict): Stores details of the currently executing action.
        bspssepy_brn (pd.DataFrame): DataFrame containing branch information.
        bspssepy_bus (pd.DataFrame): DataFrame containing bus information.
        bspssepy_load (pd.DataFrame): DataFrame containing load information.
        bspssepy_trn (pd.DataFrame): DataFrame containing transformer information.
        bspssepy_gen (pd.DataFrame): DataFrame containing generator information.
    """

    def __init__(self):
        pass
    async def SimInit(self, config=None, PSSE=None, debug_print=None, app = None):
        """
        Initializes the simulation environment by setting up system elements 
        and preparing the dynamic simulation parameters.

        Parameters:
            config (config, optional): The simulation configuration object.
            PSSE (PSSE, optional): The PSSE instance used for executing the simulation.
            debug_print (bool, optional): Enables debug messages when True.
        
        This function performs the following initialization steps:
            - Loads system elements such as buses, branches, transformers, generators, and loads.
            - Initializes the PSSE dynamic simulation environment.
            - Sets up tracking variables for control sequence execution.
        
        Notes:
            - This function must be called before running the simulation.
            - After initialization, the system can be set up for black start using `sim.SetBlackStart()`.
            - The main simulation execution is handled via `sim.Run()`.
        """
        if (debug_print is None) and app:
            debug_print = app.debug_checkbox.value


        # ==========================
        #  Assign Configuration and Debug Mode
        # ==========================
        self.PSSE = PSSE
        self.config = config

        # If debug_print is not explicitly set, use the value from config
        if debug_print is None:
            debug_print = config.debug_print
        

        self.debug_print = debug_print

        if self.debug_print:
            bp("[DEBUG] Simulation initialization started.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        
        # ==========================
        #  Get the system Base Frequency
        # ==========================
        ierr, self.BaseFrequency = psspy.base_frequency()
        if self.debug_print:
            bp(f"[DEBUG] System Base Frequency: {self.BaseFrequency}.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  load System Elements
        # ==========================
        # This function retrieves system components from PSSE and initializes monitoring channels.
        await self.GetAllElements(app=app)
        
        # ==========================
        #  Initialize Dynamic Simulation
        # ==========================
        # This function sets up simulation parameters and prepares the PSSE environment.
        await self.InitializeDynamicSimulation(app=app)
        
        # ==========================
        #  Action Tracking Variables
        # ==========================
        self.EnforceActionLock = self.config.EnforceActionLock  # Ensures sequential execution of actions.
        self.ActionInProgress = False  # Flag to track if an action is currently in progress.
        
        # Dictionary to store details of the currently executing action.
        self.Action = {
            "ElementName": None,      # Name of the device being acted upon
            "ElementType": None,      # Type of the device (Bus, Branch, Transformer, etc.)
            "Action": None,           # Action being performed (Enable, Disable, Trip, Close, etc.)
            "ActionStartTime": None,  # Time when the action started
            "ActionEndTime": None,    # Time when the action ended
        }
        
        self.DashBoardStyle = 0 # this is the basic output format 
        # self.DashBoardStyle = 1 # this is the rich output format (nice interface with tables and progress bar)

        # if self.DashBoardStyle == 1:
            

        if self.debug_print:
            bp("[DEBUG] Simulation initialization completed.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # With this, sim initialization is complete!
        # To setup black start, call sim.SetBlackStart()
        # To run the simulation, call sim.Run()



    async def InitializeDynamicSimulation(self,app=None):
        """
        Initializes the PSSE dynamic simulation environment.

        This function sets up the dynamic simulation parameters, disables frequency dependence models,
        configures output formats, and initializes the system state for the first time.

        Parameters:
            None (uses self attributes for configuration)

        This function performs the following steps:
            - Retrieves default PSSE integer, real, and character values.
            - Configures dynamic simulation solution parameters.
            - Disables frequency-dependent network models.
            - Sets the output format for channel data storage.
            - Starts the simulation output file.
            - Initializes generator power threshold settings.
        
        Notes:
            - This function must be called after `self.GetAllElements()`.
            - PSSE's `set_genpwr` function is used to enable power monitoring with a threshold.
            - Uses `self.config` attributes to dynamically set simulation constraints.
        """

        if self.debug_print:
            bp("[DEBUG] Setting up dynamic simulation parameters...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Retrieve Default PSSE Values
        # ==========================
        from .bspssepy_default_vars import bspssepy_default_vars_fun
        default_int, default_real, default_char = bspssepy_default_vars_fun()

        # ==========================
        #  Start Output File
        # ==========================
        psspy.strt_2([0,0],str(self.config.SimOutputFile))

        # ==========================
        #  Configure Dynamic Simulation Parameters
        # ==========================
        psspy.dynamics_solution_param_2([
            self.config.PSSEMaxIterationNewtonRaphson,  # Max iterations for network solution
                default_int,  # Number of monitored channels
                default_int,  # Number of state variables used
                default_int,  # Next available location in the CON array
                default_int,  # Next available location in the STATE array
                default_int,  # Next available location in the VAR array
                default_int,  # Next available location in the ICON and CHRICN arrays
                default_int,  # Next available location in the channel arrays
            ],
            [
                default_real,  # Acceleration factor for network solution
                default_real,  # Convergence tolerance for network solution
                self.config.SimulationTimeStep,  # Simulation Time step (DELT)
                self.config.Simulationfreqfilter,  # Filter time constant for bus frequency deviations
                default_real,  # Intermediate simulation mode time step threshold
                default_real,  # Large (island frequency) mode time step threshold
                default_real,  # Large (island frequency) mode acceleration factor
                default_real,  # Large (island frequency) mode convergence tolerance
            ])

        if self.debug_print:
            bp("[DEBUG] Dynamic simulation parameters set successfully.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
                
        # ==========================
        #  Disable Frequency Dependence Models
        # ==========================
        # This prevents PSSE from dynamically adjusting network parameters based on frequency variations.
        psspy.set_netfrq(0)
        if self.debug_print:
            bp("[DEBUG] Frequency dependence models disabled.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)


        # ==========================
        #  Configure Channel Output Format
        # ==========================
        # Sets the output format for monitoring data:
        #   - 0: Old OUT format (default)
        #   - 1: New OUTX format (for improved data handling in modern PSSE versions)
        psspy.set_chnfil_type(0)
        if self.debug_print:
            bp("[DEBUG] Channel file type set to old format.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Reinitialize Simulation Output File
        # ==========================
        # This is necessary to ensure the simulation starts from a clean state.
        psspy.strt_2([0, 0], str(self.config.SimOutputFile))
        if self.debug_print:
            bp(f"[DEBUG] Dynamic simulation initialized. Output file: {self.config.SimOutputFile}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Set Generator Power Threshold
        # ==========================
        # Enables power monitoring for generators with a minimum threshold.
        ierr = psspy.set_genpwr(0, 0.01)
        if ierr == 0:
            bp("[SUCCESS] set_genpwr enabled with a threshold of 0.01 MW.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        else:
            bp(f"[ERROR] Failed to enable set_genpwr. Error code: {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)


    async def GetAllElements(self,app=None):
        """
        Retrieves and initializes all system elements from PSSE.

        This function collects data for different power system elements (buses, branches, transformers, generators, loads)
        and initializes data frames for storing this information. It also sets up voltage and frequency monitoring channels.

        Parameters:
            None (uses self attributes for configuration)

        This function performs the following steps:
            - Retrieves data from PSSE for:
                - Branches
                - Buses
                - Loads
                - Transformers
                - Generators
            - Initializes additional metadata columns in each data frame.
            - Sets up voltage and frequency monitoring channels.
            - Configures solution parameters for the Newton-Raphson method.

        Notes:
            - This function must be called before running the simulation.
            - Uses `self.config` attributes to dynamically define system elements.
        """

        if self.debug_print:
            bp("[DEBUG] Generating BSPSSEPy Elements DataFrames...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Retrieve and Initialize Branch Information
        # ==========================
        # Get data from PSSE for basic branch information
        bspssepy_brn = await get_brn_info(BrnKeys=["ID", "BRANCHNAME", "FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME", "STATUS"],
            debug_print=self.debug_print,
            app=app
        )

        if self.debug_print:
            bp(f"[DEBUG] Retrieved branch info from PSSE:\n{bspssepy_brn}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Add metadata columns
        bspssepy_brn["BSPSSEPyStatus"] = bspssepy_brn["STATUS"].apply(
            lambda x: "Closed" if x == 1 else "Tripped"
        )
        bspssepy_brn["BSPSSEPyStatus_0"] = bspssepy_brn["BSPSSEPyStatus"]  # Initial status when the simulation is started
        bspssepy_brn["BSPSSEPyLastAction"] = "Initialized"
        bspssepy_brn["BSPSSEPyLastActionTime"] = 0.0  # Default time as 0.0
        bspssepy_brn["BSPSSEPySimulationNotes"] = "Initialized"
        bspssepy_brn["GenControlled"] = False

        # Assign to the class attribute
        self.bspssepy_brn = bspssepy_brn

        if self.debug_print:
            bp("[DEBUG] bspssepy_brn DataFrame initialized.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(self.bspssepy_brn,app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Retrieve and Initialize Bus Information
        # ==========================
        # Retrieve necessary bus information from PSSE
        bspssepy_bus = await get_bus_info(BusKeys=["NUMBER", "NAME", "TYPE"], debug_print=self.debug_print,app=app)

        if self.debug_print:
            bp(f"[DEBUG] Retrieved bus info from PSSE:\n{bspssepy_bus}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Add metadata columns
        bspssepy_bus["BSPSSEPyType_0"] = bspssepy_bus["TYPE"]  # Same info of TYPE
        bspssepy_bus["BSPSSEPyStatus"] = bspssepy_bus["TYPE"].apply(lambda x: "Tripped" if x == 4 else "Closed")  # Set BSPSSEPyStatus based on BSPSSEPyType
        bspssepy_bus["BSPSSEPyLastAction"] = "Initialized"
        bspssepy_bus["BSPSSEPyLastActionTime"] = 0.0  # Default initialization time
        bspssepy_bus["BSPSSEPySimulationNotes"] = "Initialized"

        # Assign to class attribute
        self.bspssepy_bus = bspssepy_bus

        if self.debug_print:
            bp("[DEBUG] bspssepy_bus DataFrame initialized.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(self.bspssepy_bus,app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)


        # ==========================
        #  Retrieve and Initialize load Information
        # ==========================
        # Retrieve necessary load information from PSSE
        bspssepy_load = await get_load_info(load_keys=["ID", "LOADNAME", "NUMBER", "NAME", "STATUS"], debug_print=self.debug_print,app=app)

        if self.debug_print:
            bp(f"[DEBUG] Retrieved load info from PSSE:\n{bspssepy_load}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Add metadata columns
        bspssepy_load["BSPSSEPyStatus"] = bspssepy_load["STATUS"].apply(lambda x: "Enabled" if x == 1 else "Disabled") # Set BSPSSEPyStatus based on STATUS
        bspssepy_load["BSPSSEPyStatus_0"] = bspssepy_load["BSPSSEPyStatus"]  # Initial status
        bspssepy_load["BSPSSEPyLastAction"] = "Initialized"
        bspssepy_load["BSPSSEPyLastActionTime"] = 0.0  # Default initialization time
        bspssepy_load["BSPSSEPySimulationNotes"] = "Initialized"
        
        # Initialize columns for tied device information - Important for "Custom loads" that are created for BSPSSEPy Simulations
        bspssepy_load["BSPSSEPyTiedDeviceName"] = None  # Placeholder for tied device name
        bspssepy_load["BSPSSEPyTiedDeviceType"] = None  # Placeholder for tied device type

        # Assign to class attribute
        self.bspssepy_load = bspssepy_load

        if self.debug_print:
            bp("[DEBUG] bspssepy_load DataFrame initialized.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(self.bspssepy_load,app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Retrieve and Initialize Transformer Information
        # ==========================
        # Get data from PSSE for basic Two-Winding Transformer Information
        bspssepy_trn = await GetTrnInfo(TrnKeys=["ID", "XFRNAME", "FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME", "STATUS"], debug_print=self.debug_print,app=app)
       
        if self.debug_print:
            bp(f"[DEBUG] Retrieved transformer info from PSSE:\n{bspssepy_trn}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Add metadata columns
        bspssepy_trn["BSPSSEPyStatus"] = bspssepy_trn["STATUS"].apply(lambda x: "Closed" if x == 1 else "Tripped")  # Set BSPSSEPyStatus based on STATUS
        bspssepy_trn["BSPSSEPyStatus_0"] = bspssepy_trn["BSPSSEPyStatus"]  # Initial status
        bspssepy_trn["BSPSSEPyLastAction"] = "Initialized"
        bspssepy_trn["BSPSSEPyLastActionTime"] = 0.0
        bspssepy_trn["BSPSSEPySimulationNotes"] = "Initialized"
        bspssepy_trn["GenControlled"] = False

        # Assign to class attribute
        self.bspssepy_trn = bspssepy_trn

        if self.debug_print:
            bp("[DEBUG] bspssepy_trn DataFrame initialized.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(bspssepy_trn,app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Set Up Voltage and Frequency Monitoring Channels
        # ==========================
        self.config = await SetupVoltageFrequencyChannels(self.config, debug_print=self.debug_print, app=app)
        

        # ==========================
        #  Configure Newton-Raphson Solution Parameters
        # ==========================
        # This line sets the max number of iterations for the Newton-Raphson method (ITMXN) to PSSEMaxIterationNewtonRaphson
        bp(f"Setting max iterations for Newton-Raphson method to {self.config.PSSEMaxIterationNewtonRaphson}",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        
        default_int, default_real, default_char = bspssepy_default_vars_fun()
        ierr = psspy.solution_parameters_5(
            [default_int if i != 1 else self.config.PSSEMaxIterationNewtonRaphson for i in range(9)],
            [default_real for _ in range(21)]
        )

        if ierr == 0:
            bp("Settings updated successfully!",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        else:
            bp(f"[ERROR] Error configuring Newton-Raphson method. Error code = {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                raise Exception("Error In GetAllElements function!")
            else:
                sys.exit(1)
        

        # ==========================
        #  Retrieve and Initialize Generator Information
        # ==========================
        bspssepy_gen = await GetGenInfo(
            GenKeys=["ID", "MCNAME", "NAME", "NUMBER", "STATUS", "PGEN", "QGEN"],
            debug_print=self.debug_print,app=app)
        
        # Extend generator data with additional modeling details
        self.bspssepy_gen, self.bspssepy_load = await ExtendBSPSSEPyGenDataFrame(
            bspssepy_gen=bspssepy_gen,
            bspssepy_bus=self.bspssepy_bus,
            ConfigTable=self.config.GeneratorsConfig,
            SimConfig=self.config,
            bspssepy_load=self.bspssepy_load,
            bspssepy_trn=self.bspssepy_trn,
            bspssepy_brn=self.bspssepy_brn,
            config=self.config,
            debug_print=self.debug_print,
            app=app
        )

        if self.debug_print:
            bp("[DEBUG] bspssepy_gen DataFrame initialized.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(self.bspssepy_gen,app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)



        bp("Creating bspssepy_agc dataframe", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

        # Create the DataFrame
        bspssepy_agc = pd.DataFrame({
            "Gen Name": bspssepy_gen["MCNAME"],      # Generator name (string)
            "Alpha": bspssepy_gen["AGCAlpha"],       # AGC Alpha values (float)
            "ΔPᴳ": [0] * len(bspssepy_gen),          # Initialize ΔPᴳ with zeros
            "Δf (Hz)": [0] * len(bspssepy_gen),      # Initialize Δf with zeros
            "Δf' (Hz/s)": [0] * len(bspssepy_gen)    # Initialize Δf' (rate of Δf)
        })

        # Explicitly set the column data types
        bspssepy_agc = bspssepy_agc.astype({
            "Gen Name": str,      # Ensure "Gen Name" is a string
            "Alpha": float,       # "Alpha" should be float for numerical operations
            "ΔPᴳ": float,         # Ensure ΔPᴳ is float (not int)
            "Δf (Hz)": float,     # Ensure Δf (Hz) is float (not int)
            "Δf' (Hz/s)": float,  # Ensure Δf' (Hz/s) is float (not int)
        })

        
        self.bspssepy_agc = bspssepy_agc
        if self.debug_print:
            bp("[DEBUG] bspssepy_agc DataFrame initialized.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp(self.bspssepy_agc,app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

            
        bp("[SUCCESS] All elements retrieved successfully and the data frames are initialized.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        


    async def SetBlackStart(self,app=None):
        """
        Configures the system for a black-start scenario by disabling all loads,
        tripping all branches and two-winding transformers, and handling generators.

        A black-start scenario involves restarting the power system without relying on
        an external power grid. In this function:
        
        - **All branches and transformers are tripped** to isolate components.
        - **All loads are disabled** to prevent premature power draw.
        - **Black-start generators remain operational**, while non-black-start generators
        are handled using a controlled startup sequence.
        
        Parameters:
            None (uses self attributes for configuration)

        This function performs the following steps:
            - Trips all branches in the system.
            - Trips all two-winding transformers.
            - Disables all loads.
            - Leaves black-start generators operational while handling non-black-start generators.
            - Reinitializes the simulation.

        Notes:
            - This function must be called before starting a black-start sequence.
            - Non-black-start generators will not be manually disabled, as their associated transformers
            and branches are already tripped.
            - After execution, the system is fully prepared for black-start restoration.
        """

        if self.debug_print:
            bp("[DEBUG] Configuring system for black-start scenario...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Trip All Branches
        # ==========================
        bp("Tripping all branches...",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        for BranchRowIndex, BranchrowDF in self.bspssepy_brn.iterrows():
            BranchName = BranchrowDF['BRANCHNAME']
            if self.debug_print:
                bp(f"[DEBUG] Attempting to trip branch: {BranchName}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            await BrnTrip(t = 0, bspssepy_brn=self.bspssepy_brn, BranchName=BranchName, debug_print=self.debug_print,app=app)
            if self.debug_print:
                bp(f"[DEBUG] Successfully tripped branch: {BranchName}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Trip All Two-Winding Transformers
        # ==========================
        bp("Tripping all two-winding transformers...",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        for TrnRowIndex, TrnrowDF in self.bspssepy_trn.iterrows():
            TrnName = TrnrowDF['XFRNAME']
            if self.debug_print:
                bp(f"[DEBUG] Attempting to trip two-winding transformer: {TrnName}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            await TrnTrip(t=0, bspssepy_trn=self.bspssepy_trn, TrnName=TrnName, debug_print=self.debug_print, app=app)
            if self.debug_print:
                bp(f"[DEBUG] Successfully tripped two-winding transformer: {TrnName}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

        # ==========================
        #  Disable All Loads
        # ==========================
        bp("Disabling all loads...",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        for LoadRowIndex, LoadrowDF in self.bspssepy_load.iterrows():
            LOADNAME = LoadrowDF['LOADNAME']
            if self.debug_print:
                bp(f"[DEBUG] Attempting to disable load: {LOADNAME}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            await LoadDisable(t=0, bspssepy_load=self.bspssepy_load, LOADNAME=LOADNAME, debug_print=self.debug_print,app=app)
            if self.debug_print:
                bp(f"[DEBUG] Successfully disabled load: {LOADNAME}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

        
        # ==========================
        #  Generator Handling
        # ==========================
        # No need to manually disable generators, as transformers/branches are already tripped.
        # These transformers/branches will be re-enabled through GenEnable function as needed.

        # ==========================
        #  Reinitialize Simulation
        # ==========================
        bp("Reinitializing simulation...",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)
        psspy.strt_2([0, 0], str(self.config.SimOutputFile))

        
        bp("[SUCCESS] Black-start scenario configured successfully.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    
    
    async def Run(self,app=None):
        """
        Executes the dynamic simulation in fixed time steps until completion.

        This function runs the simulation dynamically by processing time-based actions 
        defined in `self.config.bspssepy_sequence`. It continuously checks if actions need 
        to be executed and updates the system state accordingly.

        Parameters:
            None (uses self attributes for configuration)

        This function performs the following steps:
            - Initializes simulation variables and flags.
            - Iterates through the defined control sequence, executing actions at the specified times.
            - Enforces action execution constraints (e.g., enforcing sequence locking).
            - Checks and maintains system frequency within the safety margins.
            - Calls appropriate functions to modify system elements dynamically.
            - Continues execution until `EndSimulationFlag` is set to `True`.

        Notes:
            - The function handles black-start generators separately to avoid disruptions.
            - Uses `self.config.BSPSSEPyHardTimeLimitFlag` to enforce a maximum simulation time.
            - The function runs in a loop, incrementing time steps until all actions are completed.
        """


        self.BSPSSEPyDashbaoard = None
        
        
        # ==========================
        #  Initialize Simulation Variables
        # ==========================
        self.EndSimulationFlag = False  # Main loop exit condition
        CurrentSimTime = 0  # Current simulation time in seconds
        LastPrintedTime = 0  # Controls how frequently messages are printed
        self.Actions = []  # Initialize a list to store multiple action dictionaries
        AllActionsExecuted = False  # A flag to exit the simulation when all actions are executed and the freuqnecy is regulated back to nominal value!
        FrequencyRegulated = False
        old_freq_dev = [0.0] * (len(self.bspssepy_gen)+1)  # Initialize the rate of frequency deviation Δf' (Hz/s) (last element is for the average)
        bp("Starting dynamic simulation...",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

        
        # Track the time shift due to execution delays
        self.TimeShift = 0  
        
        
        # ==========================
        #  Main Simulation Loop
        # ==========================
        while not self.EndSimulationFlag:
            # Keep track if CurrentSimTime cycle is already accounted for in "self.TimeShift"
            AccountedForDelay = False
            AllActionsExecuted = True #Always assume we are done!
            
            CurrentSimTime >= self.config.BSPSSEPyHardTimeLimit*60
            if app:
                ProgressBarUpdate(app.top_bar_progress_bar, CurrentSimTime, self.config.BSPSSEPyHardTimeLimit*60, App=app, label=app.top_bar_progress_bar_label)
                await asyncio.sleep(0)

            # await asyncio.sleep(0.1)
            # bp(f"t = {CurrentSimTime}")
            # bp(pd.DataFrame(self.Actions))
            # await asyncio.sleep(app.async_print_delay if app else 0)
            
            
            if self.debug_print:
                bp(f"[DEBUG] Current Simulation Time: {CurrentSimTime}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"[DEBUG] Actions before cleanup: {self.Actions}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            # Remove completed tasks from self.Actions
            # ActionStatus: 0 -> Not Started, 1 -> In Progress, 2 -> Completed
            self.Actions = [action for action in self.Actions if action["ActionStatus"] != 2]

            if self.debug_print:
                bp(f"[DEBUG] Actions after cleanup: {self.Actions}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)


            # ==========================
            #  Check for New Actions
            # ==========================
            # Iterate over bspssepy_sequence to check for new actions
            for RowIndex, Row in self.config.bspssepy_sequence.iterrows():
                action_time = (Row["Action Time"] * 60) + self.TimeShift  # Convert to seconds + Apply time shift

                # Check if ControlSequenceAsIs Flag is enabled --> ignore action-time 
                if self.config.ControlSequenceAsIs:
                    # ==========================
                    #  Enforce Action Locking
                    # ==========================
                    if not self.EnforceActionLock:
                        if app:
                            # Need a code to perform this request, for now, it will simply ignore it.
                            self.EnforceActionLock = True
                            bp('[WARNING] "EnforceActionLock" is set to False while "ControlSequenceAsIs" is True. "EnforceActionLock" has been overridden to True.', app=app)
                            await asyncio.sleep(app.async_print_delay if app else 0)
                        else:
                            if str.lower(input("EnforceActionLock is False and ControlSequenceAsIs is True. EnforceActionLock Should be True. Overridde?  [y/n]:")) in ["y", "yes", "ok", "true", "t", "1"]:
                                self.EnforceActionLock = True
                            else:
                                bp('[ERROR] Since ControlSequenceAsIs is enabled, EnforceActionLock must be enabled. Exiting...',app=app)
                                await asyncio.sleep(app.async_print_delay if app else 0)
                                if app:
                                    raise Exception("Error in sim.Run function!")
                                else:
                                    sys.exit(0)

                    # Add new actions if they are not already in the queue
                    if (not any(action["ElementIDValue"] == Row["Identification Value"] for action in self.Actions)) and (Row["Action Status"] not in [2,-999]):
                        if self.debug_print:
                            bp("[DEBUG] ControlSequenceAsIs is enabled. Skipping action-time validation.",app=app)
                            await asyncio.sleep(app.async_print_delay if app else 0)
                        if self.EnforceActionLock and any(action["ActionStatus"] in [0, 1] for action in self.Actions):                            
                            if self.debug_print:
                                bp("[DEBUG] EnforceActionLock active. Skipping new action due to ongoing actions.",app=app)
                                await asyncio.sleep(app.async_print_delay if app else 0)
                            continue

                        # Add action to queue
                        NewAction = {
                            "UID": Row["UID"],
                            "ElementIDValue": Row["Identification Value"],
                            "ElementIDType": Row["Identification Type"],
                            "ElementType": Row["Device Type"],
                            "Action": Row["Action Type"],
                            "StartTime": action_time,
                            "EndTime": -1,
                            "ActionStatus": Row["Action Status"],  # 0: Not started, 1: In progress, 2: Completed
                            "BSPSSEPySequenceRowIndex": RowIndex,  # Add the row index
                        }
                        self.Actions.append(NewAction)
                        
                        # Check if self.config.BypassTiedActions is True → Add all tied actions linked to the current action
                        if self.config.BypassTiedActions:
                            TiedActions = self.config.bspssepy_sequence[self.config.bspssepy_sequence["Tied Action"] == Row["UID"]]
                            for _, tied_row in TiedActions.iterrows():
                                # Ensure tied action is not already in the execution queue
                                if not any(action["UID"] == tied_row["UID"] for action in self.Actions):
                                    TiedAction = {
                                        "UID": tied_row["UID"],
                                        "ElementIDValue": tied_row["Identification Value"],
                                        "ElementIDType": tied_row["Identification Type"],
                                        "ElementType": tied_row["Device Type"],
                                        "Action": tied_row["Action Type"],
                                        "StartTime": action_time,  # Same start time as parent action
                                        "EndTime": -1,
                                        "ActionStatus": tied_row["Action Status"],  # 0: Not started, 1: In progress, 2: Completed
                                        "BSPSSEPySequenceRowIndex": tied_row.name,  # Row index
                                    }
                                    self.Actions.append(TiedAction)

                                    if self.debug_print:
                                        bp(f"[DEBUG] Added tied action alongside parent: {TiedAction}", app=app)
                                        await asyncio.sleep(app.async_print_delay if app else 0)
                        

                        if self.debug_print:
                            bp(f"[DEBUG] Added new action: {NewAction}",app=app)
                            await asyncio.sleep(app.async_print_delay if app else 0)
                
                
                
                else: # ControlSequenceAsIs Flag is disabled --> Standard time-based execution
                    # ==========================
                    #  Handle Time-Based Execution
                    # ==========================

                    # Check if the action should start and is not already added to self.Actions
                    if (CurrentSimTime >= action_time) and (not any(action["ElementIDValue"] == Row["Identification Value"] for action in self.Actions)) and (Row["Action Status"] not in [2,-999]):

                        # If EnforceActionLock is true and an action is already in progress, skip adding new actions
                        if self.EnforceActionLock and any(action["ActionStatus"] in [0, 1] for action in self.Actions):
                            if self.debug_print:
                                bp("[DEBUG] EnforceActionLock active. Skipping new action due to ongoing actions.",app=app)
                                await asyncio.sleep(app.async_print_delay if app else 0)
                            continue

                        # Add the new action to self.Actions
                        NewAction = {
                            "UID": Row["UID"],
                            "ElementIDValue": Row["Identification Value"],
                            "ElementIDType": Row["Identification Type"],
                            "ElementType": Row["Device Type"],
                            "Action": Row["Action Type"],
                            "StartTime": action_time,
                            "EndTime": -1,
                            "ActionStatus": Row["Action Status"],  # 0: Not started, 1: In progress, 2: Completed
                            "BSPSSEPySequenceRowIndex": RowIndex,  # Add the row index
                        }
                        self.Actions.append(NewAction)

                        # Check if self.config.BypassTiedActions is True → Add all tied actions linked to the current action
                        if self.config.BypassTiedActions:
                            TiedActions = self.config.bspssepy_sequence[self.config.bspssepy_sequence["Tied Action"] == Row["UID"]]
                            for _, tied_row in TiedActions.iterrows():
                                # Ensure tied action is not already in the execution queue
                                if not any(action["UID"] == tied_row["UID"] for action in self.Actions):
                                    TiedAction = {
                                        "UID": tied_row["UID"],
                                        "ElementIDValue": tied_row["Identification Value"],
                                        "ElementIDType": tied_row["Identification Type"],
                                        "ElementType": tied_row["Device Type"],
                                        "Action": tied_row["Action Type"],
                                        "StartTime": action_time,  # Same start time as parent action
                                        "EndTime": -1,
                                        "ActionStatus": tied_row["Action Status"],  # 0: Not started, 1: In progress, 2: Completed
                                        "BSPSSEPySequenceRowIndex": tied_row.name,  # Row index
                                    }
                                    self.Actions.append(TiedAction)

                                    if self.debug_print:
                                        bp(f"[DEBUG] Added tied action alongside parent: {TiedAction}", app=app)
                                        await asyncio.sleep(app.async_print_delay if app else 0)

                        
                        if self.debug_print:
                            bp(f"[DEBUG] Added new action: {NewAction}",app=app)
                            await asyncio.sleep(app.async_print_delay if app else 0)
            
            # for RowIndex, Row in self.config.bspssepy_sequence.iterrows():
            if any(Row["Action Status"] not in [2,-999] for RowIndex, Row in self.config.bspssepy_sequence.iterrows()):
                # we still have some actions to do!
                AllActionsExecuted = False
                    
                    
            # ==========================
            #  Execute Actions
            # ==========================
            for action in self.Actions:
                if self.debug_print:
                    bp(f"[DEBUG] Processing action: {action}",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)

                if action["ActionStatus"] != 2:  # Action is pending or in progress
                    # Handle frequency safety margin if enabled
                    if self.config.EnforceFrequencySafetyMargin:
                        AvgFreq = await GetAvgFrequency(self.bspssepy_gen, self.config.Channels, debug_print=self.debug_print)
                        if (self.config.FreqSafetyMarginMin - AvgFreq) > 1e-3 or (AvgFreq - self.config.FreqSafetyMarginMax) > 1e-3:
                            if self.debug_print:
                                bp(f"[DEBUG] Frequency deviation detected. Action delayed. (f_avg = {AvgFreq} Hz)", app=app)
                                await asyncio.sleep(app.async_print_delay if app else 0)
                            
                            if self.config.AccountForActionExecutionDelays and not AccountedForDelay:
                                self.TimeShift += self.config.BSPSSEPyTimeStep # Increment by self.config.BSPSSEPyTimeStep
                                AccountedForDelay = True
                            continue  # Skip this action for now


                    
                    # Determine action function          
                    ElementType = device_type_mapping[action["ElementType"].lower()]
                    ElementIDType = identification_type_mapping[action["ElementIDType"].lower()]
                    ElementIDValue = action["ElementIDValue"]
                    ElementActionType = action_type_mapping[action["Action"].lower()].lower()

                    if self.debug_print:
                        # bp(f"[DEBUG] Preparing to execute: ElementType={ElementType}, ElementIDType={ElementIDType}, ElementIDValue={ElementIDValue}, ActionType={ElementActionType}",app=app)
                        # await asyncio.sleep(app.async_print_delay if app else 0)
                        bp(f"[DEBUG] Preparing to execute action: {ElementActionType} on {ElementType} ({ElementIDType}: {ElementIDValue})",app=app)
                        await asyncio.sleep(app.async_print_delay if app else 0)


                    # Determine the function to call based on element type and action type
                    if ElementType in ElementTypeFunctionMapping and ElementActionType in ElementTypeFunctionMapping[ElementType]:
                        ActionFunction = ElementTypeFunctionMapping[ElementType][ElementActionType]

                        if self.debug_print:
                            bp(f"[DEBUG] Calling function {ActionFunction} for ElementIDValue={ElementIDValue}",app=app)
                            await asyncio.sleep(app.async_print_delay if app else 0)

                        # Map the identification type to the correct argument name
                        ElementArgumentName = id_type_mapping[ElementIDType][ElementType]

                        # Create the keyword argument dictionary
                        kwargs = {
                            ElementArgumentName                             :ElementIDValue,
                            "t"                                             :CurrentSimTime,
                            bspssepy_df_arg_mapping[ElementType]   :getattr(self, bspssepy_df_arg_mapping[ElementType]),
                            "debug_print"                                    :self.debug_print,
                            "app"                                           :app
                            }

                        # Add 'bspssepy_bus' to 'kwargs' if `ElementType` is "BRN" or "TRN"
                        if ElementType in ["BRN", "TRN"]:
                            kwargs["bspssepy_bus"] = self.bspssepy_bus

                        if ElementType in ["LOAD"]:
                            kwargs["bspssepy_gen"] = self.bspssepy_gen
                            kwargs["bspssepy_agc"] = self.bspssepy_agc
                        
                        # Add the following to 'kwargs' if 'ElementType' is "GEN"
                        if ElementType == "GEN":
                            kwargs["action"] = action
                            kwargs["bspssepy_brn"] = self.bspssepy_brn
                            kwargs["bspssepy_trn"] = self.bspssepy_trn
                            kwargs["bspssepy_load"] = self.bspssepy_load
                            kwargs["bspssepy_bus"] = self.bspssepy_bus
                            kwargs["bspssepy_agc"] = self.bspssepy_agc
                            kwargs["config"] = self.config

                        if (action["ActionStatus"] == 0) & (self.DashBoardStyle == 0):
                            bp(f"Executing action: ==> {ElementActionType} for {ElementType} ==> {ElementIDType} : {ElementIDValue} (t = {CurrentSimTime}s)", app=app)
                            await asyncio.sleep(app.async_print_delay if app else 0)

                        # action["ActionStartTime"] += self.TimeShift  # Adjust start times
                        if action["ActionStatus"] == 0:
                            action["StartTime"] = CurrentSimTime
                        
                        # Call the action function (pass appropriate arguments as per your function requirements)
                        action["ActionStatus"] = await ActionFunction(**kwargs)

                        if ElementType in ["BRN", "BUS", "LOAD", "TRN"]:
                            # Those functions returns ierr value from psspy functions, and if ierr == 0 --> no errors occured and actions are completed successfully.
                            if action["ActionStatus"] == 0:
                                action["ActionStatus"] = 2  # update it to state 2 --> marking that the action was completed successfully for BSPSSEPy program


                        # Update Action Status using the stored row index
                        self.config.bspssepy_sequence.at[action["BSPSSEPySequenceRowIndex"], "Action Status"] = action["ActionStatus"]

                        if self.debug_print:
                            bp(f"[DEBUG] Updated Action Status for Row {action['BSPSSEPySequenceRowIndex']}: {action['ActionStatus']}",app=app)
                            await asyncio.sleep(app.async_print_delay if app else 0)

                        if action["ActionStatus"] == -999:
                            
                            action["EndTime"] = CurrentSimTime
                            
                            # This action will be ignored as it will be embedded with a generator action. Modify the plan to avoid this error/msg.
                            if self.debug_print:
                                bp(f"[CAUTION]{action} - **** This action will be skipped as it should be embedded within GenEnable actions. To avoid this msg, remove the action from the plan! ****",app=app)
                                await asyncio.sleep(app.async_print_delay if app else 0)
                            self.Actions = [action for action in self.Actions if action["ActionStatus"] != -999]
                        
                        
                        
                        if action["ActionStatus"] in[2, -999]:
                            action["EndTime"] = CurrentSimTime

                        # Update Action Status using the stored row index
                        self.config.bspssepy_sequence.at[action["BSPSSEPySequenceRowIndex"], "Action Status"] = action["ActionStatus"]
                        self.config.bspssepy_sequence.at[action["BSPSSEPySequenceRowIndex"], "Start Time"] = action["StartTime"]
                        self.config.bspssepy_sequence.at[action["BSPSSEPySequenceRowIndex"], "End Time"] = action["EndTime"]

            
            if not (self.config.delay_agc_after_action >= CurrentSimTime - max(
                (row["End Time"] for row_index, row in self.config.bspssepy_sequence.iterrows() if row["Action Status"] == 2), default=0)
            ):
                self.bspssepy_gen, self.bspssepy_agc, FrequencyRegulated, old_freq_dev = await AGCControl(
                    bspssepy_gen=self.bspssepy_gen,
                    bspssepy_agc = self.bspssepy_agc,
                    Channels =self.config.Channels,
                    TimeStep=self.config.BSPSSEPyTimeStep,
                    AGCTimeConstant=60.0,
                    Deadband=0.001, #Hz and Hz/s for rate of dev
                    debug_print=self.debug_print,
                    UseOutFile=False, app=app,
                    BaseFrequency=self.BaseFrequency,
                    FrequencyRegulated = False,
                    old_freq_dev = old_freq_dev,  # Δf[k-1] (Hz)
                )
            
            # ==========================
            #  Update Simulation Time
            # ==========================
            # Determine the next simulation time step to run
            NextSimTime = CurrentSimTime + self.config.BSPSSEPyTimeStep
            CutPrintMessagesFlag = False
            if self.config.BSPSSEPyHardTimeLimitFlag and CurrentSimTime >= self.config.BSPSSEPyHardTimeLimit*60:
                CutPrintMessagesFlag = True
                self.EndSimulationFlag = True
            elif not self.config.BSPSSEPyHardTimeLimitFlag and FrequencyRegulated and AllActionsExecuted:
                CutPrintMessagesFlag = True
                self.EndSimulationFlag = True

            # Print message only every BSPSSEPyProgressPrintTime minutes
            if ((int(CurrentSimTime) // (self.config.BSPSSEPyProgressPrintTime*60) != int(LastPrintedTime) // (self.config.BSPSSEPyProgressPrintTime*60) and not CutPrintMessagesFlag) or CurrentSimTime == 0) & (self.DashBoardStyle == 0):
                if app == None:
                    bp(f"running simulation from {CurrentSimTime/60} to {CurrentSimTime/60 + self.config.BSPSSEPyProgressPrintTime} minutes", app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                LastPrintedTime = CurrentSimTime

            psspy.run(0,                  # Network solution convergence monitor option
                    NextSimTime,          # Time to run the simulation to (in seconds)
                    1000,                 # Number of time steps between channel value prints
                    50,                   # Number of time steps between writing output channel values
                    0)                    # Number of time steps between plotting CRT channels

            # Update the current simulation time
            CurrentSimTime = NextSimTime

            if self.DashBoardStyle == 1 & (not self.debug_print):
                from .bspssepy_live_monitoring import CreateMainDashboard
                CreateMainDashboard(5,0.5)
            from fun.bspssepy.app.app_helper_funs import update_bspssepy_app_gui
            if app:
                await update_bspssepy_app_gui(app=app)

        bp("Simulation ended.")
        await asyncio.sleep(app.async_print_delay if app else 0)


async def SetupVoltageFrequencyChannels(config, debug_print = False, app=None):
    """
    Sets up voltage and frequency monitoring channels in PSSE.

    This function configures PSSE to monitor voltage magnitudes, voltage angles,
    and bus frequency deviations for the specified buses.

    Parameters:
        config (config): The configuration object containing buses to monitor.
        debug_print (bool, optional): If True, prints debug messages for troubleshooting.

    Returns:
        config (config): Updated configuration object with added monitoring channels.

    This function performs the following steps:
        - Adds voltage magnitude and angle monitoring for specified buses.
        - Adds frequency monitoring for specified buses.
        - Updates `config.Channels` with the newly created channels.

    Notes:
        - The buses to be monitored are specified in `config.BusesToMonitor_Voltage` and `config.BusesToMonitor_Frequency`.
        - The channel index is managed through `config.CurrentChannelIndex`.
    """

    # ==========================
    #  Voltage Monitoring Setup
    # ==========================
    bp("Setting up voltage channels...",app=app)
    await asyncio.sleep(app.async_print_delay if app else 0)

    for bus in config.BusesToMonitor_Voltage:
        # Add monitoring for voltage magnitude and angle
        ierr = psspy.voltage_and_angle_channel([-1, -1, -1, bus])

        if ierr == 0:
            # Add voltage magnitude channel to config.Channels
            config.Channels.append({
                "Channel Type": "Voltage Magnitude",
                "Bus Number": bus,
                "Element Index": bus,  # Assuming bus number as the index for buses
                "Element Name": f"Bus {bus}",
                "Channel Index": config.CurrentChannelIndex,
                "Additional Info": "Voltage magnitude (pu)"
            })
            if debug_print:
                bp(f"[DEBUG] Voltage Magnitude channel setup for Bus {bus} - Channel Index {config.CurrentChannelIndex}.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            config.CurrentChannelIndex += 1  # Increment index

            # Add voltage angle channel to config.Channels
            config.Channels.append({
                "Channel Type": "Voltage Angle",
                "Bus Number": bus,
                "Element Index": bus,  # Assuming bus number as the index for buses
                "Element Name": f"Bus {bus}",
                "Channel Index": config.CurrentChannelIndex,
                "Additional Info": "Voltage angle (degrees)"
            })
            if debug_print:
                bp(f"[DEBUG] Voltage Angle channel setup for Bus {bus} - Channel Index {config.CurrentChannelIndex}.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            config.CurrentChannelIndex += 1  # Increment index

            bp(f"[SUCCESS] Voltage monitoring (Magnitude and Angle) added for Bus {bus}.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        else:
            bp(f"[ERROR] Failed to set up voltage monitoring for Bus {bus}. Error code = {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                # Fatel Error Hanlding in the GUI
                raise Exception("Error In SetupVoltageFrequencyChannels function!")
            else:
                sys.exit(1)

    if debug_print:
        bp("[DEBUG] Voltage monitoring setup completed.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)


    
    # ==========================
    #  Frequency Monitoring Setup
    # ==========================
    bp("Setting up frequency channels...",app=app)
    await asyncio.sleep(app.async_print_delay if app else 0)
    for bus in config.BusesToMonitor_Frequency:
        # Add monitoring for frequency deviation
        ierr = psspy.bus_frequency_channel([-1, bus])
        if ierr == 0:
            # Use CurrentChannelIndex from config and increment it
            config.Channels.append({
                "Channel Type": "Frequency",
                "Bus Number": bus,
                "Element Index": bus,  # Assuming bus number as the index for buses
                "Element Name": f"Bus{bus}",
                "Channel Index": config.CurrentChannelIndex,
                "Additional Info": "Frequency deviation in Hz"
            })
            if debug_print:
                bp(f"[DEBUG] Frequency channel setup completed for Bus {bus} - Channel Index {config.CurrentChannelIndex}.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            
            config.CurrentChannelIndex += 1  # Increment index

            bp(f"[SUCCESS] Frequency monitoring added for Bus {bus}.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        else:
            bp(f"[ERROR] Failed to set up frequency monitoring for Bus {bus}. Error code = {ierr}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if app:
                # Fatel Error Hanlding in the GUI
                raise Exception("Error In SetupVoltageFrequencyChannels function!")
            else:
                sys.exit(1)
            
    if debug_print:
        bp("[DEBUG] Frequency monitoring setup completed.",app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

    return config
