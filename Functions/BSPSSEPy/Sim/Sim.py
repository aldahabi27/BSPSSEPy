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

from .BSPSSEPyBrnFunctions import *
from .BSPSSEPyBusFunctions import *
from .BSPSSEPyDefaultVariables import *
from .BSPSSEPyGenFunctions import *
from .BSPSSEPyLoadFunctions import *
from .BSPSSEPyTrnFunctions import *
from Functions.BSPSSEPy.BSPSSEPyDictionary import *
from Functions.BSPSSEPy.BSPSSEPyFunctionsDictionary import *
from .BSPSSEPyAGC import *
from .BSPSSEPyChannels import GetAvgFrequency
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint, ProgressBarUpdate
import asyncio


class Sim:
    """
    The Sim class handles the execution of the power system simulation.
    It initializes system elements, sets up monitoring channels, 
    and runs dynamic simulation cases using PSSE.

    Attributes:
        Config (Config): The simulation configuration object.
        PSSE (PSSE): The PSSE instance used for simulation operations.
        DebugPrint (bool): Enables debug messages when True.
        EnforceActionLock (bool): Ensures sequential action execution.
        ActionInProgress (bool): Tracks if an action is currently executing.
        Action (dict): Stores details of the currently executing action.
        BSPSSEPyBrn (pd.DataFrame): DataFrame containing branch information.
        BSPSSEPyBus (pd.DataFrame): DataFrame containing bus information.
        BSPSSEPyLoad (pd.DataFrame): DataFrame containing load information.
        BSPSSEPyTrn (pd.DataFrame): DataFrame containing transformer information.
        BSPSSEPyGen (pd.DataFrame): DataFrame containing generator information.
    """

    def __init__(self):
        pass
    async def SimInit(self, Config=None, PSSE=None, DebugPrint=None, app = None):
        """
        Initializes the simulation environment by setting up system elements 
        and preparing the dynamic simulation parameters.

        Parameters:
            Config (Config, optional): The simulation configuration object.
            PSSE (PSSE, optional): The PSSE instance used for executing the simulation.
            DebugPrint (bool, optional): Enables debug messages when True.
        
        This function performs the following initialization steps:
            - Loads system elements such as buses, branches, transformers, generators, and loads.
            - Initializes the PSSE dynamic simulation environment.
            - Sets up tracking variables for control sequence execution.
        
        Notes:
            - This function must be called before running the simulation.
            - After initialization, the system can be set up for black start using `Sim.SetBlackStart()`.
            - The main simulation execution is handled via `Sim.Run()`.
        """
        if (DebugPrint is None) and app:
            DebugPrint = app.DebugCheckBox.value


        # ==========================
        #  Assign Configuration and Debug Mode
        # ==========================
        self.PSSE = PSSE
        self.Config = Config

        # If DebugPrint is not explicitly set, use the value from Config
        if DebugPrint is None:
            DebugPrint = Config.DebugPrint
        

        self.DebugPrint = DebugPrint

        if self.DebugPrint:
            bsprint("[DEBUG] Simulation initialization started.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        # ==========================
        #  Get the system Base Frequency
        # ==========================
        ierr, self.BaseFrequency = psspy.base_frequency()
        if self.DebugPrint:
            bsprint(f"[DEBUG] System Base Frequency: {self.BaseFrequency}.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Load System Elements
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
        self.EnforceActionLock = self.Config.EnforceActionLock  # Ensures sequential execution of actions.
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
            

        if self.DebugPrint:
            bsprint("[DEBUG] Simulation initialization completed.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # With this, Sim initialization is complete!
        # To setup black start, call Sim.SetBlackStart()
        # To run the simulation, call Sim.Run()



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
            - Uses `self.Config` attributes to dynamically set simulation constraints.
        """

        if self.DebugPrint:
            bsprint("[DEBUG] Setting up dynamic simulation parameters...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Retrieve Default PSSE Values
        # ==========================
        from .BSPSSEPyDefaultVariables import BSPSSEPyDefaultVariablesFun
        DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()

        # ==========================
        #  Start Output File
        # ==========================
        psspy.strt_2([0,0],str(self.Config.SimOutputFile))

        # ==========================
        #  Configure Dynamic Simulation Parameters
        # ==========================
        psspy.dynamics_solution_param_2([
            self.Config.PSSEMaxIterationNewtonRaphson,  # Max iterations for network solution
                DefaultInt,  # Number of monitored channels
                DefaultInt,  # Number of state variables used
                DefaultInt,  # Next available location in the CON array
                DefaultInt,  # Next available location in the STATE array
                DefaultInt,  # Next available location in the VAR array
                DefaultInt,  # Next available location in the ICON and CHRICN arrays
                DefaultInt,  # Next available location in the channel arrays
            ],
            [
                DefaultReal,  # Acceleration factor for network solution
                DefaultReal,  # Convergence tolerance for network solution
                self.Config.SimulationTimeStep,  # Simulation Time step (DELT)
                self.Config.Simulationfreqfilter,  # Filter time constant for bus frequency deviations
                DefaultReal,  # Intermediate simulation mode time step threshold
                DefaultReal,  # Large (island frequency) mode time step threshold
                DefaultReal,  # Large (island frequency) mode acceleration factor
                DefaultReal,  # Large (island frequency) mode convergence tolerance
            ])

        if self.DebugPrint:
            bsprint("[DEBUG] Dynamic simulation parameters set successfully.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
                
        # ==========================
        #  Disable Frequency Dependence Models
        # ==========================
        # This prevents PSSE from dynamically adjusting network parameters based on frequency variations.
        psspy.set_netfrq(0)
        if self.DebugPrint:
            bsprint("[DEBUG] Frequency dependence models disabled.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)


        # ==========================
        #  Configure Channel Output Format
        # ==========================
        # Sets the output format for monitoring data:
        #   - 0: Old OUT format (default)
        #   - 1: New OUTX format (for improved data handling in modern PSSE versions)
        psspy.set_chnfil_type(0)
        if self.DebugPrint:
            bsprint("[DEBUG] Channel file type set to old format.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Reinitialize Simulation Output File
        # ==========================
        # This is necessary to ensure the simulation starts from a clean state.
        psspy.strt_2([0, 0], str(self.Config.SimOutputFile))
        if self.DebugPrint:
            bsprint(f"[DEBUG] Dynamic simulation initialized. Output file: {self.Config.SimOutputFile}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Set Generator Power Threshold
        # ==========================
        # Enables power monitoring for generators with a minimum threshold.
        ierr = psspy.set_genpwr(0, 0.01)
        if ierr == 0:
            bsprint("[SUCCESS] set_genpwr enabled with a threshold of 0.01 MW.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        else:
            bsprint(f"[ERROR] Failed to enable set_genpwr. Error code: {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)


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
            - Uses `self.Config` attributes to dynamically define system elements.
        """

        if self.DebugPrint:
            bsprint("[DEBUG] Generating BSPSSEPy Elements DataFrames...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Retrieve and Initialize Branch Information
        # ==========================
        # Get data from PSSE for basic branch information
        BSPSSEPyBrn = await GetBrnInfo(BrnKeys=["ID", "BRANCHNAME", "FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME", "STATUS"],
            DebugPrint=self.DebugPrint,
            app=app
        )

        if self.DebugPrint:
            bsprint(f"[DEBUG] Retrieved branch info from PSSE:\n{BSPSSEPyBrn}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Add metadata columns
        BSPSSEPyBrn["BSPSSEPyStatus"] = BSPSSEPyBrn["STATUS"].apply(
            lambda x: "Closed" if x == 1 else "Tripped"
        )
        BSPSSEPyBrn["BSPSSEPyStatus_0"] = BSPSSEPyBrn["BSPSSEPyStatus"]  # Initial status when the simulation is started
        BSPSSEPyBrn["BSPSSEPyLastAction"] = "Initialized"
        BSPSSEPyBrn["BSPSSEPyLastActionTime"] = 0.0  # Default time as 0.0
        BSPSSEPyBrn["BSPSSEPySimulationNotes"] = "Initialized"
        BSPSSEPyBrn["GenControlled"] = False

        # Assign to the class attribute
        self.BSPSSEPyBrn = BSPSSEPyBrn

        if self.DebugPrint:
            bsprint("[DEBUG] BSPSSEPyBrn DataFrame initialized.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(self.BSPSSEPyBrn,app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Retrieve and Initialize Bus Information
        # ==========================
        # Retrieve necessary bus information from PSSE
        BSPSSEPyBus = await GetBusInfo(BusKeys=["NUMBER", "NAME", "TYPE"], DebugPrint=self.DebugPrint,app=app)

        if self.DebugPrint:
            bsprint(f"[DEBUG] Retrieved bus info from PSSE:\n{BSPSSEPyBus}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Add metadata columns
        BSPSSEPyBus["BSPSSEPyType_0"] = BSPSSEPyBus["TYPE"]  # Same info of TYPE
        BSPSSEPyBus["BSPSSEPyStatus"] = BSPSSEPyBus["TYPE"].apply(lambda x: "Tripped" if x == 4 else "Closed")  # Set BSPSSEPyStatus based on BSPSSEPyType
        BSPSSEPyBus["BSPSSEPyLastAction"] = "Initialized"
        BSPSSEPyBus["BSPSSEPyLastActionTime"] = 0.0  # Default initialization time
        BSPSSEPyBus["BSPSSEPySimulationNotes"] = "Initialized"

        # Assign to class attribute
        self.BSPSSEPyBus = BSPSSEPyBus

        if self.DebugPrint:
            bsprint("[DEBUG] BSPSSEPyBus DataFrame initialized.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(self.BSPSSEPyBus,app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)


        # ==========================
        #  Retrieve and Initialize Load Information
        # ==========================
        # Retrieve necessary load information from PSSE
        BSPSSEPyLoad = await GetLoadInfo(LoadKeys=["ID", "LOADNAME", "NUMBER", "NAME", "STATUS"], DebugPrint=self.DebugPrint,app=app)

        if self.DebugPrint:
            bsprint(f"[DEBUG] Retrieved load info from PSSE:\n{BSPSSEPyLoad}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Add metadata columns
        BSPSSEPyLoad["BSPSSEPyStatus"] = BSPSSEPyLoad["STATUS"].apply(lambda x: "Enabled" if x == 1 else "Disabled") # Set BSPSSEPyStatus based on STATUS
        BSPSSEPyLoad["BSPSSEPyStatus_0"] = BSPSSEPyLoad["BSPSSEPyStatus"]  # Initial status
        BSPSSEPyLoad["BSPSSEPyLastAction"] = "Initialized"
        BSPSSEPyLoad["BSPSSEPyLastActionTime"] = 0.0  # Default initialization time
        BSPSSEPyLoad["BSPSSEPySimulationNotes"] = "Initialized"
        
        # Initialize columns for tied device information - Important for "Custom loads" that are created for BSPSSEPy Simulations
        BSPSSEPyLoad["BSPSSEPyTiedDeviceName"] = None  # Placeholder for tied device name
        BSPSSEPyLoad["BSPSSEPyTiedDeviceType"] = None  # Placeholder for tied device type

        # Assign to class attribute
        self.BSPSSEPyLoad = BSPSSEPyLoad

        if self.DebugPrint:
            bsprint("[DEBUG] BSPSSEPyLoad DataFrame initialized.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(self.BSPSSEPyLoad,app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Retrieve and Initialize Transformer Information
        # ==========================
        # Get data from PSSE for basic Two-Winding Transformer Information
        BSPSSEPyTrn = await GetTrnInfo(TrnKeys=["ID", "XFRNAME", "FROMNUMBER", "FROMNAME", "TONUMBER", "TONAME", "STATUS"], DebugPrint=self.DebugPrint,app=app)
       
        if self.DebugPrint:
            bsprint(f"[DEBUG] Retrieved transformer info from PSSE:\n{BSPSSEPyTrn}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Add metadata columns
        BSPSSEPyTrn["BSPSSEPyStatus"] = BSPSSEPyTrn["STATUS"].apply(lambda x: "Closed" if x == 1 else "Tripped")  # Set BSPSSEPyStatus based on STATUS
        BSPSSEPyTrn["BSPSSEPyStatus_0"] = BSPSSEPyTrn["BSPSSEPyStatus"]  # Initial status
        BSPSSEPyTrn["BSPSSEPyLastAction"] = "Initialized"
        BSPSSEPyTrn["BSPSSEPyLastActionTime"] = 0.0
        BSPSSEPyTrn["BSPSSEPySimulationNotes"] = "Initialized"
        BSPSSEPyTrn["GenControlled"] = False

        # Assign to class attribute
        self.BSPSSEPyTrn = BSPSSEPyTrn

        if self.DebugPrint:
            bsprint("[DEBUG] BSPSSEPyTrn DataFrame initialized.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(BSPSSEPyTrn,app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Set Up Voltage and Frequency Monitoring Channels
        # ==========================
        self.Config = await SetupVoltageFrequencyChannels(self.Config, DebugPrint=self.DebugPrint, app=app)
        

        # ==========================
        #  Configure Newton-Raphson Solution Parameters
        # ==========================
        # This line sets the max number of iterations for the Newton-Raphson method (ITMXN) to PSSEMaxIterationNewtonRaphson
        bsprint(f"Setting max iterations for Newton-Raphson method to {self.Config.PSSEMaxIterationNewtonRaphson}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        DefaultInt, DefaultReal, DefaultChar = BSPSSEPyDefaultVariablesFun()
        ierr = psspy.solution_parameters_5(
            [DefaultInt if i != 1 else self.Config.PSSEMaxIterationNewtonRaphson for i in range(9)],
            [DefaultReal for _ in range(21)]
        )

        if ierr == 0:
            bsprint("Settings updated successfully!",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        else:
            bsprint(f"[ERROR] Error configuring Newton-Raphson method. Error code = {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if app:
                raise Exception("Error In GetAllElements function!")
            else:
                sys.exit(1)
        

        # ==========================
        #  Retrieve and Initialize Generator Information
        # ==========================
        BSPSSEPyGen = await GetGenInfo(
            GenKeys=["ID", "MCNAME", "NAME", "NUMBER", "STATUS", "PGEN", "QGEN"],
            DebugPrint=self.DebugPrint,app=app)
        
        # Extend generator data with additional modeling details
        self.BSPSSEPyGen, self.BSPSSEPyLoad = await ExtendBSPSSEPyGenDataFrame(
            BSPSSEPyGen=BSPSSEPyGen,
            BSPSSEPyBus=self.BSPSSEPyBus,
            ConfigTable=self.Config.GeneratorsConfig,
            SimConfig=self.Config,
            BSPSSEPyLoad=self.BSPSSEPyLoad,
            BSPSSEPyTrn=self.BSPSSEPyTrn,
            BSPSSEPyBrn=self.BSPSSEPyBrn,
            Config=self.Config,
            DebugPrint=self.DebugPrint,
            app=app
        )

        if self.DebugPrint:
            bsprint("[DEBUG] BSPSSEPyGen DataFrame initialized.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(self.BSPSSEPyGen,app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)



        bsprint("Creating BSPSSEPyAGCDF dataframe", app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Create the DataFrame
        BSPSSEPyAGCDF = pd.DataFrame({
            "Gen Name": BSPSSEPyGen["MCNAME"],      # Generator name (string)
            "Alpha": BSPSSEPyGen["AGCAlpha"],       # AGC Alpha values (float)
            "ΔPᴳ": [0] * len(BSPSSEPyGen),          # Initialize ΔPᴳ with zeros
            "Δf (Hz)": [0] * len(BSPSSEPyGen),      # Initialize Δf with zeros
            "Δf' (Hz/s)": [0] * len(BSPSSEPyGen)    # Initialize Δf' (rate of Δf)
        })

        # Explicitly set the column data types
        BSPSSEPyAGCDF = BSPSSEPyAGCDF.astype({
            "Gen Name": str,      # Ensure "Gen Name" is a string
            "Alpha": float,       # "Alpha" should be float for numerical operations
            "ΔPᴳ": float,         # Ensure ΔPᴳ is float (not int)
            "Δf (Hz)": float,     # Ensure Δf (Hz) is float (not int)
            "Δf' (Hz/s)": float,  # Ensure Δf' (Hz/s) is float (not int)
        })

        
        self.BSPSSEPyAGCDF = BSPSSEPyAGCDF
        if self.DebugPrint:
            bsprint("[DEBUG] BSPSSEPyAGCDF DataFrame initialized.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint(self.BSPSSEPyAGCDF,app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            
        bsprint("[SUCCESS] All elements retrieved successfully and the data frames are initialized.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        


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

        if self.DebugPrint:
            bsprint("[DEBUG] Configuring system for black-start scenario...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Trip All Branches
        # ==========================
        bsprint("Tripping all branches...",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        for BranchRowIndex, BranchrowDF in self.BSPSSEPyBrn.iterrows():
            BranchName = BranchrowDF['BRANCHNAME']
            if self.DebugPrint:
                bsprint(f"[DEBUG] Attempting to trip branch: {BranchName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            await BrnTrip(t = 0, BSPSSEPyBrn=self.BSPSSEPyBrn, BranchName=BranchName, DebugPrint=self.DebugPrint,app=app)
            if self.DebugPrint:
                bsprint(f"[DEBUG] Successfully tripped branch: {BranchName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Trip All Two-Winding Transformers
        # ==========================
        bsprint("Tripping all two-winding transformers...",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        for TrnRowIndex, TrnrowDF in self.BSPSSEPyTrn.iterrows():
            TrnName = TrnrowDF['XFRNAME']
            if self.DebugPrint:
                bsprint(f"[DEBUG] Attempting to trip two-winding transformer: {TrnName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            await TrnTrip(t=0, BSPSSEPyTrn=self.BSPSSEPyTrn, TrnName=TrnName, DebugPrint=self.DebugPrint, app=app)
            if self.DebugPrint:
                bsprint(f"[DEBUG] Successfully tripped two-winding transformer: {TrnName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # ==========================
        #  Disable All Loads
        # ==========================
        bsprint("Disabling all loads...",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        for LoadRowIndex, LoadrowDF in self.BSPSSEPyLoad.iterrows():
            LoadName = LoadrowDF['LOADNAME']
            if self.DebugPrint:
                bsprint(f"[DEBUG] Attempting to disable load: {LoadName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            await LoadDisable(t=0, BSPSSEPyLoad=self.BSPSSEPyLoad, LoadName=LoadName, DebugPrint=self.DebugPrint,app=app)
            if self.DebugPrint:
                bsprint(f"[DEBUG] Successfully disabled load: {LoadName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

        
        # ==========================
        #  Generator Handling
        # ==========================
        # No need to manually disable generators, as transformers/branches are already tripped.
        # These transformers/branches will be re-enabled through GenEnable function as needed.

        # ==========================
        #  Reinitialize Simulation
        # ==========================
        bsprint("Reinitializing simulation...",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        psspy.strt_2([0, 0], str(self.Config.SimOutputFile))

        
        bsprint("[SUCCESS] Black-start scenario configured successfully.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    
    
    async def Run(self,app=None):
        """
        Executes the dynamic simulation in fixed time steps until completion.

        This function runs the simulation dynamically by processing time-based actions 
        defined in `self.Config.BSPSSEPySequence`. It continuously checks if actions need 
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
            - Uses `self.Config.BSPSSEPyHardTimeLimitFlag` to enforce a maximum simulation time.
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
        old_freq_dev = [0.0] * (len(self.BSPSSEPyGen)+1)  # Initialize the rate of frequency deviation Δf' (Hz/s) (last element is for the average)
        bsprint("Starting dynamic simulation...",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

        
        # Track the time shift due to execution delays
        self.TimeShift = 0  
        
        
        # ==========================
        #  Main Simulation Loop
        # ==========================
        while not self.EndSimulationFlag:
            # Keep track if CurrentSimTime cycle is already accounted for in "self.TimeShift"
            AccountedForDelay = False
            AllActionsExecuted = True #Always assume we are done!
            
            CurrentSimTime >= self.Config.BSPSSEPyHardTimeLimit*60
            if app:
                ProgressBarUpdate(app.TopBarProgressBar, CurrentSimTime, self.Config.BSPSSEPyHardTimeLimit*60, App=app, label=app.TopBarProgressBarLabel)
                await asyncio.sleep(0)

            # await asyncio.sleep(0.1)
            # bsprint(f"t = {CurrentSimTime}")
            # bsprint(pd.DataFrame(self.Actions))
            # await asyncio.sleep(app.bsprintasynciotime if app else 0)
            
            
            if self.DebugPrint:
                bsprint(f"[DEBUG] Current Simulation Time: {CurrentSimTime}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"[DEBUG] Actions before cleanup: {self.Actions}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            # Remove completed tasks from self.Actions
            # ActionStatus: 0 -> Not Started, 1 -> In Progress, 2 -> Completed
            self.Actions = [action for action in self.Actions if action["ActionStatus"] != 2]

            if self.DebugPrint:
                bsprint(f"[DEBUG] Actions after cleanup: {self.Actions}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)


            # ==========================
            #  Check for New Actions
            # ==========================
            # Iterate over BSPSSEPySequence to check for new actions
            for RowIndex, Row in self.Config.BSPSSEPySequence.iterrows():
                ActionTime = (Row["Action Time"] * 60) + self.TimeShift  # Convert to seconds + Apply time shift

                # Check if ControlSequenceAsIs Flag is enabled --> ignore action-time 
                if self.Config.ControlSequenceAsIs:
                    # ==========================
                    #  Enforce Action Locking
                    # ==========================
                    if not self.EnforceActionLock:
                        if app:
                            # Need a code to perform this request, for now, it will simply ignore it.
                            self.EnforceActionLock = True
                            bsprint('[WARNING] "EnforceActionLock" is set to False while "ControlSequenceAsIs" is True. "EnforceActionLock" has been overridden to True.', app=app)
                            await asyncio.sleep(app.bsprintasynciotime if app else 0)
                        else:
                            if str.lower(input("EnforceActionLock is False and ControlSequenceAsIs is True. EnforceActionLock Should be True. Overridde?  [y/n]:")) in ["y", "yes", "ok", "true", "t", "1"]:
                                self.EnforceActionLock = True
                            else:
                                bsprint('[ERROR] Since ControlSequenceAsIs is enabled, EnforceActionLock must be enabled. Exiting...',app=app)
                                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                                if app:
                                    raise Exception("Error in Sim.Run function!")
                                else:
                                    sys.exit(0)

                    # Add new actions if they are not already in the queue
                    if (not any(action["ElementIDValue"] == Row["Identification Value"] for action in self.Actions)) and (Row["Action Status"] not in [2,-999]):
                        if self.DebugPrint:
                            bsprint("[DEBUG] ControlSequenceAsIs is enabled. Skipping action-time validation.",app=app)
                            await asyncio.sleep(app.bsprintasynciotime if app else 0)
                        if self.EnforceActionLock and any(action["ActionStatus"] in [0, 1] for action in self.Actions):                            
                            if self.DebugPrint:
                                bsprint("[DEBUG] EnforceActionLock active. Skipping new action due to ongoing actions.",app=app)
                                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                            continue

                        # Add action to queue
                        NewAction = {
                            "UID": Row["UID"],
                            "ElementIDValue": Row["Identification Value"],
                            "ElementIDType": Row["Identification Type"],
                            "ElementType": Row["Device Type"],
                            "Action": Row["Action Type"],
                            "StartTime": ActionTime,
                            "EndTime": -1,
                            "ActionStatus": Row["Action Status"],  # 0: Not started, 1: In progress, 2: Completed
                            "BSPSSEPySequenceRowIndex": RowIndex,  # Add the row index
                        }
                        self.Actions.append(NewAction)
                        
                        # Check if self.Config.BypassTiedActions is True → Add all tied actions linked to the current action
                        if self.Config.BypassTiedActions:
                            TiedActions = self.Config.BSPSSEPySequence[self.Config.BSPSSEPySequence["Tied Action"] == Row["UID"]]
                            for _, tied_row in TiedActions.iterrows():
                                # Ensure tied action is not already in the execution queue
                                if not any(action["UID"] == tied_row["UID"] for action in self.Actions):
                                    TiedAction = {
                                        "UID": tied_row["UID"],
                                        "ElementIDValue": tied_row["Identification Value"],
                                        "ElementIDType": tied_row["Identification Type"],
                                        "ElementType": tied_row["Device Type"],
                                        "Action": tied_row["Action Type"],
                                        "StartTime": ActionTime,  # Same start time as parent action
                                        "EndTime": -1,
                                        "ActionStatus": tied_row["Action Status"],  # 0: Not started, 1: In progress, 2: Completed
                                        "BSPSSEPySequenceRowIndex": tied_row.name,  # Row index
                                    }
                                    self.Actions.append(TiedAction)

                                    if self.DebugPrint:
                                        bsprint(f"[DEBUG] Added tied action alongside parent: {TiedAction}", app=app)
                                        await asyncio.sleep(app.bsprintasynciotime if app else 0)
                        

                        if self.DebugPrint:
                            bsprint(f"[DEBUG] Added new action: {NewAction}",app=app)
                            await asyncio.sleep(app.bsprintasynciotime if app else 0)
                
                
                
                else: # ControlSequenceAsIs Flag is disabled --> Standard time-based execution
                    # ==========================
                    #  Handle Time-Based Execution
                    # ==========================

                    # Check if the action should start and is not already added to self.Actions
                    if (CurrentSimTime >= ActionTime) and (not any(action["ElementIDValue"] == Row["Identification Value"] for action in self.Actions)) and (Row["Action Status"] not in [2,-999]):

                        # If EnforceActionLock is true and an action is already in progress, skip adding new actions
                        if self.EnforceActionLock and any(action["ActionStatus"] in [0, 1] for action in self.Actions):
                            if self.DebugPrint:
                                bsprint("[DEBUG] EnforceActionLock active. Skipping new action due to ongoing actions.",app=app)
                                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                            continue

                        # Add the new action to self.Actions
                        NewAction = {
                            "UID": Row["UID"],
                            "ElementIDValue": Row["Identification Value"],
                            "ElementIDType": Row["Identification Type"],
                            "ElementType": Row["Device Type"],
                            "Action": Row["Action Type"],
                            "StartTime": ActionTime,
                            "EndTime": -1,
                            "ActionStatus": Row["Action Status"],  # 0: Not started, 1: In progress, 2: Completed
                            "BSPSSEPySequenceRowIndex": RowIndex,  # Add the row index
                        }
                        self.Actions.append(NewAction)

                        # Check if self.Config.BypassTiedActions is True → Add all tied actions linked to the current action
                        if self.Config.BypassTiedActions:
                            TiedActions = self.Config.BSPSSEPySequence[self.Config.BSPSSEPySequence["Tied Action"] == Row["UID"]]
                            for _, tied_row in TiedActions.iterrows():
                                # Ensure tied action is not already in the execution queue
                                if not any(action["UID"] == tied_row["UID"] for action in self.Actions):
                                    TiedAction = {
                                        "UID": tied_row["UID"],
                                        "ElementIDValue": tied_row["Identification Value"],
                                        "ElementIDType": tied_row["Identification Type"],
                                        "ElementType": tied_row["Device Type"],
                                        "Action": tied_row["Action Type"],
                                        "StartTime": ActionTime,  # Same start time as parent action
                                        "EndTime": -1,
                                        "ActionStatus": tied_row["Action Status"],  # 0: Not started, 1: In progress, 2: Completed
                                        "BSPSSEPySequenceRowIndex": tied_row.name,  # Row index
                                    }
                                    self.Actions.append(TiedAction)

                                    if self.DebugPrint:
                                        bsprint(f"[DEBUG] Added tied action alongside parent: {TiedAction}", app=app)
                                        await asyncio.sleep(app.bsprintasynciotime if app else 0)

                        
                        if self.DebugPrint:
                            bsprint(f"[DEBUG] Added new action: {NewAction}",app=app)
                            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            
            # for RowIndex, Row in self.Config.BSPSSEPySequence.iterrows():
            if any(Row["Action Status"] not in [2,-999] for RowIndex, Row in self.Config.BSPSSEPySequence.iterrows()):
                # we still have some actions to do!
                AllActionsExecuted = False
                    
                    
            # ==========================
            #  Execute Actions
            # ==========================
            for action in self.Actions:
                if self.DebugPrint:
                    bsprint(f"[DEBUG] Processing action: {action}",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)

                if action["ActionStatus"] != 2:  # Action is pending or in progress
                    # Handle frequency safety margin if enabled
                    if self.Config.EnforceFrequencySafetyMargin:
                        AvgFreq = await GetAvgFrequency(self.BSPSSEPyGen, self.Config.Channels, DebugPrint=self.DebugPrint)
                        if (self.Config.FreqSafetyMarginMin - AvgFreq) > 1e-3 or (AvgFreq - self.Config.FreqSafetyMarginMax) > 1e-3:
                            if self.DebugPrint:
                                bsprint(f"[DEBUG] Frequency deviation detected. Action delayed. (f_avg = {AvgFreq} Hz)", app=app)
                                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                            
                            if self.Config.AccountForActionExecutionDelays and not AccountedForDelay:
                                self.TimeShift += self.Config.BSPSSEPyTimeStep # Increment by self.Config.BSPSSEPyTimeStep
                                AccountedForDelay = True
                            continue  # Skip this action for now


                    
                    # Determine action function          
                    ElementType = DeviceTypeMapping[action["ElementType"].lower()]
                    ElementIDType = IdentificationTypeMapping[action["ElementIDType"].lower()]
                    ElementIDValue = action["ElementIDValue"]
                    ElementActionType = ActionTypeMapping[action["Action"].lower()].lower()

                    if self.DebugPrint:
                        # bsprint(f"[DEBUG] Preparing to execute: ElementType={ElementType}, ElementIDType={ElementIDType}, ElementIDValue={ElementIDValue}, ActionType={ElementActionType}",app=app)
                        # await asyncio.sleep(app.bsprintasynciotime if app else 0)
                        bsprint(f"[DEBUG] Preparing to execute action: {ElementActionType} on {ElementType} ({ElementIDType}: {ElementIDValue})",app=app)
                        await asyncio.sleep(app.bsprintasynciotime if app else 0)


                    # Determine the function to call based on element type and action type
                    if ElementType in ElementTypeFunctionMapping and ElementActionType in ElementTypeFunctionMapping[ElementType]:
                        ActionFunction = ElementTypeFunctionMapping[ElementType][ElementActionType]

                        if self.DebugPrint:
                            bsprint(f"[DEBUG] Calling function {ActionFunction} for ElementIDValue={ElementIDValue}",app=app)
                            await asyncio.sleep(app.bsprintasynciotime if app else 0)

                        # Map the identification type to the correct argument name
                        ElementArgumentName = IDTypeMapping[ElementIDType][ElementType]

                        # Create the keyword argument dictionary
                        kwargs = {
                            ElementArgumentName                             :ElementIDValue,
                            "t"                                             :CurrentSimTime,
                            BSPSSEPyDataFrameArgumentMapping[ElementType]   :getattr(self, BSPSSEPyDataFrameArgumentMapping[ElementType]),
                            "DebugPrint"                                    :self.DebugPrint,
                            "app"                                           :app
                            }

                        # Add 'BSPSSEPyBus' to 'kwargs' if `ElementType` is "BRN" or "TRN"
                        if ElementType in ["BRN", "TRN"]:
                            kwargs["BSPSSEPyBus"] = self.BSPSSEPyBus

                        if ElementType in ["LOAD"]:
                            kwargs["BSPSSEPyGen"] = self.BSPSSEPyGen
                            kwargs["BSPSSEPyAGCDF"] = self.BSPSSEPyAGCDF
                        
                        # Add the following to 'kwargs' if 'ElementType' is "GEN"
                        if ElementType == "GEN":
                            kwargs["action"] = action
                            kwargs["BSPSSEPyBrn"] = self.BSPSSEPyBrn
                            kwargs["BSPSSEPyTrn"] = self.BSPSSEPyTrn
                            kwargs["BSPSSEPyLoad"] = self.BSPSSEPyLoad
                            kwargs["BSPSSEPyBus"] = self.BSPSSEPyBus
                            kwargs["BSPSSEPyAGCDF"] = self.BSPSSEPyAGCDF
                            kwargs["Config"] = self.Config

                        if (action["ActionStatus"] == 0) & (self.DashBoardStyle == 0):
                            bsprint(f"Executing action: ==> {ElementActionType} for {ElementType} ==> {ElementIDType} : {ElementIDValue} (t = {CurrentSimTime}s)", app=app)
                            await asyncio.sleep(app.bsprintasynciotime if app else 0)

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
                        self.Config.BSPSSEPySequence.at[action["BSPSSEPySequenceRowIndex"], "Action Status"] = action["ActionStatus"]

                        if self.DebugPrint:
                            bsprint(f"[DEBUG] Updated Action Status for Row {action['BSPSSEPySequenceRowIndex']}: {action['ActionStatus']}",app=app)
                            await asyncio.sleep(app.bsprintasynciotime if app else 0)

                        if action["ActionStatus"] == -999:
                            
                            action["EndTime"] = CurrentSimTime
                            
                            # This action will be ignored as it will be embedded with a generator action. Modify the plan to avoid this error/msg.
                            if self.DebugPrint:
                                bsprint(f"[CAUTION]{action} - **** This action will be skipped as it should be embedded within GenEnable actions. To avoid this msg, remove the action from the plan! ****",app=app)
                                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                            self.Actions = [action for action in self.Actions if action["ActionStatus"] != -999]
                        
                        
                        
                        if action["ActionStatus"] in[2, -999]:
                            action["EndTime"] = CurrentSimTime

                        # Update Action Status using the stored row index
                        self.Config.BSPSSEPySequence.at[action["BSPSSEPySequenceRowIndex"], "Action Status"] = action["ActionStatus"]
                        self.Config.BSPSSEPySequence.at[action["BSPSSEPySequenceRowIndex"], "Start Time"] = action["StartTime"]
                        self.Config.BSPSSEPySequence.at[action["BSPSSEPySequenceRowIndex"], "End Time"] = action["EndTime"]

            
            if not (self.Config.delay_agc_after_action >= CurrentSimTime - max(
                (row["End Time"] for row_index, row in self.Config.BSPSSEPySequence.iterrows() if row["Action Status"] == 2), default=0)
            ):
                self.BSPSSEPyGen, self.BSPSSEPyAGCDF, FrequencyRegulated, old_freq_dev = await AGCControl(
                    BSPSSEPyGen=self.BSPSSEPyGen,
                    BSPSSEPyAGCDF = self.BSPSSEPyAGCDF,
                    Channels =self.Config.Channels,
                    TimeStep=self.Config.BSPSSEPyTimeStep,
                    AGCTimeConstant=60.0,
                    Deadband=0.001, #Hz and Hz/s for rate of dev
                    DebugPrint=self.DebugPrint,
                    UseOutFile=False, app=app,
                    BaseFrequency=self.BaseFrequency,
                    FrequencyRegulated = False,
                    old_freq_dev = old_freq_dev,  # Δf[k-1] (Hz)
                )
            
            # ==========================
            #  Update Simulation Time
            # ==========================
            # Determine the next simulation time step to run
            NextSimTime = CurrentSimTime + self.Config.BSPSSEPyTimeStep
            CutPrintMessagesFlag = False
            if self.Config.BSPSSEPyHardTimeLimitFlag and CurrentSimTime >= self.Config.BSPSSEPyHardTimeLimit*60:
                CutPrintMessagesFlag = True
                self.EndSimulationFlag = True
            elif not self.Config.BSPSSEPyHardTimeLimitFlag and FrequencyRegulated and AllActionsExecuted:
                CutPrintMessagesFlag = True
                self.EndSimulationFlag = True

            # Print message only every BSPSSEPyProgressPrintTime minutes
            if ((int(CurrentSimTime) // (self.Config.BSPSSEPyProgressPrintTime*60) != int(LastPrintedTime) // (self.Config.BSPSSEPyProgressPrintTime*60) and not CutPrintMessagesFlag) or CurrentSimTime == 0) & (self.DashBoardStyle == 0):
                if app == None:
                    bsprint(f"running simulation from {CurrentSimTime/60} to {CurrentSimTime/60 + self.Config.BSPSSEPyProgressPrintTime} minutes", app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                LastPrintedTime = CurrentSimTime

            psspy.run(0,                  # Network solution convergence monitor option
                    NextSimTime,          # Time to run the simulation to (in seconds)
                    1000,                 # Number of time steps between channel value prints
                    50,                   # Number of time steps between writing output channel values
                    0)                    # Number of time steps between plotting CRT channels

            # Update the current simulation time
            CurrentSimTime = NextSimTime

            if self.DashBoardStyle == 1 & (not self.DebugPrint):
                from .BSPSSEPyLiveMonitor import CreateMainDashboard
                CreateMainDashboard(5,0.5)
            from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import UpdateBSPSSEPyAppGUI
            if app:
                await UpdateBSPSSEPyAppGUI(app=app)

        bsprint("Simulation ended.")
        await asyncio.sleep(app.bsprintasynciotime if app else 0)


async def SetupVoltageFrequencyChannels(Config, DebugPrint = False, app=None):
    """
    Sets up voltage and frequency monitoring channels in PSSE.

    This function configures PSSE to monitor voltage magnitudes, voltage angles,
    and bus frequency deviations for the specified buses.

    Parameters:
        Config (Config): The configuration object containing buses to monitor.
        DebugPrint (bool, optional): If True, prints debug messages for troubleshooting.

    Returns:
        Config (Config): Updated configuration object with added monitoring channels.

    This function performs the following steps:
        - Adds voltage magnitude and angle monitoring for specified buses.
        - Adds frequency monitoring for specified buses.
        - Updates `Config.Channels` with the newly created channels.

    Notes:
        - The buses to be monitored are specified in `Config.BusesToMonitor_Voltage` and `Config.BusesToMonitor_Frequency`.
        - The channel index is managed through `Config.CurrentChannelIndex`.
    """

    # ==========================
    #  Voltage Monitoring Setup
    # ==========================
    bsprint("Setting up voltage channels...",app=app)
    await asyncio.sleep(app.bsprintasynciotime if app else 0)

    for bus in Config.BusesToMonitor_Voltage:
        # Add monitoring for voltage magnitude and angle
        ierr = psspy.voltage_and_angle_channel([-1, -1, -1, bus])

        if ierr == 0:
            # Add voltage magnitude channel to Config.Channels
            Config.Channels.append({
                "Channel Type": "Voltage Magnitude",
                "Bus Number": bus,
                "Element Index": bus,  # Assuming bus number as the index for buses
                "Element Name": f"Bus {bus}",
                "Channel Index": Config.CurrentChannelIndex,
                "Additional Info": "Voltage magnitude (pu)"
            })
            if DebugPrint:
                bsprint(f"[DEBUG] Voltage Magnitude channel setup for Bus {bus} - Channel Index {Config.CurrentChannelIndex}.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            Config.CurrentChannelIndex += 1  # Increment index

            # Add voltage angle channel to Config.Channels
            Config.Channels.append({
                "Channel Type": "Voltage Angle",
                "Bus Number": bus,
                "Element Index": bus,  # Assuming bus number as the index for buses
                "Element Name": f"Bus {bus}",
                "Channel Index": Config.CurrentChannelIndex,
                "Additional Info": "Voltage angle (degrees)"
            })
            if DebugPrint:
                bsprint(f"[DEBUG] Voltage Angle channel setup for Bus {bus} - Channel Index {Config.CurrentChannelIndex}.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            Config.CurrentChannelIndex += 1  # Increment index

            bsprint(f"[SUCCESS] Voltage monitoring (Magnitude and Angle) added for Bus {bus}.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        else:
            bsprint(f"[ERROR] Failed to set up voltage monitoring for Bus {bus}. Error code = {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if app:
                # Fatel Error Hanlding in the GUI
                raise Exception("Error In SetupVoltageFrequencyChannels function!")
            else:
                sys.exit(1)

    if DebugPrint:
        bsprint("[DEBUG] Voltage monitoring setup completed.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)


    
    # ==========================
    #  Frequency Monitoring Setup
    # ==========================
    bsprint("Setting up frequency channels...",app=app)
    await asyncio.sleep(app.bsprintasynciotime if app else 0)
    for bus in Config.BusesToMonitor_Frequency:
        # Add monitoring for frequency deviation
        ierr = psspy.bus_frequency_channel([-1, bus])
        if ierr == 0:
            # Use CurrentChannelIndex from Config and increment it
            Config.Channels.append({
                "Channel Type": "Frequency",
                "Bus Number": bus,
                "Element Index": bus,  # Assuming bus number as the index for buses
                "Element Name": f"Bus{bus}",
                "Channel Index": Config.CurrentChannelIndex,
                "Additional Info": "Frequency deviation in Hz"
            })
            if DebugPrint:
                bsprint(f"[DEBUG] Frequency channel setup completed for Bus {bus} - Channel Index {Config.CurrentChannelIndex}.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            
            Config.CurrentChannelIndex += 1  # Increment index

            bsprint(f"[SUCCESS] Frequency monitoring added for Bus {bus}.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        else:
            bsprint(f"[ERROR] Failed to set up frequency monitoring for Bus {bus}. Error code = {ierr}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if app:
                # Fatel Error Hanlding in the GUI
                raise Exception("Error In SetupVoltageFrequencyChannels function!")
            else:
                sys.exit(1)
            
    if DebugPrint:
        bsprint("[DEBUG] Frequency monitoring setup completed.",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    return Config
