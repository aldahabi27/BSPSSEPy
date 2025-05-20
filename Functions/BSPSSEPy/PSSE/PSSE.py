# ===========================================================
#   BSPSSEPy Application - PSSE Initialization Class
# ===========================================================
#   This module handles the initialization and configuration
#   of PSSE for dynamic power system simulations.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================
 
import psse3601
import psspy
import sys
import os
from Functions.BSPSSEPy.Sim.BSPSSEPyDefaultVariables import BSPSSEPyDefaultVariablesFun
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint
import asyncio
import io
from contextlib import redirect_stdout


class PSSE:
    """
    The PSSE class initializes the PSSE environment and loads system files required for simulation.

    Attributes:
        Config (Config): An instance of the BSPSSEPy.Config class containing simulation settings.
        DebugPrint (bool): Enables debug messages when True.
        CaseInitializationFlag (int): Status flag for PSSE case initialization.
        DefaultInt, DefaultReal, DefaultChar: Default PSSE values for missing parameters.
    """

    def __init__(self):

        pass

    async def PSSEInit(self, Config, DebugPrint = None, app = None):
        """
        Initializes the PSSE simulation environment and loads necessary files.

        Parameters:
            Config (Config): The configuration object containing simulation settings.
            DebugPrint (bool, optional): Enables debug messages if set to True. Defaults to Config.DebugPrint.

        This function initializes PSSE, sets up logging, loads the case files,
        runs power flow solutions, and prepares snapshot and converted files.
        """

        if DebugPrint is None:
            if app:
                DebugPrint = app.DebugCheckBox.value
            else:
                DebugPrint = Config.DebugPrint
        

        if DebugPrint:
            bsprint("[DEBUG] Entering PSSE Constructor...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        
        try:
            # ==========================
            #  Initialize PSSE
            # ==========================

            # Create a StringIO object to capture the output
            output_capture = io.StringIO()

            # Use the context manager to capture the stdout
            with redirect_stdout(output_capture):
                self.CaseInitializationFlag = psspy.psseinit(Config.NumberOfBuses)
            # Get the captured output
            captured_output = output_capture.getvalue()
            
            bsprint(captured_output, app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            
            if self.CaseInitializationFlag != 0:
                # if app:
                #     raise Exception(f"PSSE initialization failed with error code {self.CaseInitializationFlag}.")
                # else:
# 
                    raise RuntimeError(f"PSSE initialization failed with error code {self.CaseInitializationFlag}.")
            else:
                bsprint("PSSE initialized successfully.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            if DebugPrint:
                bsprint(f"[DEBUG] Case Initialization Flag: {self.CaseInitializationFlag} (0 indicates no errors)",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)


            # Retrieve default PSSE values for inputs
            # Those values can be used when we want to modify certain parameters in the models, without changing the other parameters values. So we simply say "default" for the other values.
            self.DefaultInt, self.DefaultReal, self.DefaultChar = BSPSSEPyDefaultVariablesFun()
            if DebugPrint:
                bsprint("[DEBUG] Default PSSE values retrieved.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            # Redirect PSSE progress output to log file
            psspy.progress_output(2,str(Config.LogFile),[0,0])
            bsprint(f"Log file will be saved to: {Config.LogFile}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            # ==========================
            #  Load SAV File
            # ==========================
            bsprint("Loading SAV File",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            ierr = psspy.case(str(Config.SAVFile))
            if ierr == 0:
                bsprint(f"[SUCCESS] SAV file '{Config.SAVFile.name}' loaded successfully.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            else:
                # if app:
                #     raise Exception(f"[ERROR] Failed to load SAV file '{Config.SAVFile.name}'. Error code: {ierr}")
                # else:
                    raise RuntimeError(f"[ERROR] Failed to load SAV file '{Config.SAVFile.name}'. Error code: {ierr}")

            # ==========================
            #  Load DYR File
            # ==========================
            bsprint("Loading DYR File",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            # Starting indices (use defaults unless you know what you're doing)
            startindx = [1, 1, 1, 1]
            ierr = psspy.dyre_new_2(startindx, str(Config.DYRFile))  # Use CaseDYRFile directly

            # Check for errors
            if ierr == 0:
                bsprint(f"[SUCCESS] DYR file '{Config.DYRFile.name}' loaded successfully.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            else:
                # if app:
                #     raise Exception (f"[ERROR] Failed to load DYR file '{Config.DYRFile.name}'. Error code: {ierr}")
                # else:
                    raise RuntimeError(f"[ERROR] Failed to load DYR file '{Config.DYRFile.name}'. Error code: {ierr}")
            
            # ==========================
            #  Power Flow Solution
            # ==========================
            bsprint("Running Power Flow Solution...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            for _ in range(6):
                psspy.fdns([0, 0, 0, 1, 1, 0, 99, 0])
            psspy.fnsl()
            bsprint("[SUCCESS] Power flow solved successfully.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            
            
            # Voltage and frequency channels code is moved to Sim.GetAllElements() due to an error in psspy that results in wrong channel measurement being recorded!
            # This error cost me a lot of time to figure out!
            
            
            


            # The following code will convert loads and generators, as well as the case file to prepare it for dynamic simulation.
            # It will generate two files, SNP and CNV. The code will check to see, if those files are available, it will read them.
            # If you encounter error, update the flags "IgnoreCNVFile" & "IgnoreSNPFile" to force generate new files (warning, this overwrites the files)


            # ==========================
            #  CNV File Handling
            # ==========================
            bsprint("Checking and Loading CNV File...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if os.path.exists(Config.CNVFile) and not Config.IgnoreCNVFile:
                bsprint(f"CNV file '{Config.CNVFile.name}' found. Loading...",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                ierr = psspy.case(str(Config.CNVFile))  # Load the CNV File 
                if ierr == 0:
                    bsprint(f"[SUCCESS] CNV file '{Config.CNVFile.name}' loaded successfully.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to load CNV file '{Config.CNVFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to load CNV file '{Config.CNVFile.name}'. Error code: {ierr}")
            else:
                bsprint(f"File '{Config.CNVFile.name}' not found or ignored. Converting case '{Config.SAVFile.name}'",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"Importing conversion script in {Config.ConvCodeFile.name}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                
                # We read the file content in ConvCodeFile
                with open(Config.ConvCodeFile,"r") as file:
                    exec(file.read())
                
                bsprint(f"Saving the CNV File '{Config.CNVFile.name}'",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                ierr = psspy.save(str(Config.CNVFile))
                if ierr == 0:
                    bsprint(f"[SUCCESS] Converted case saved to '{Config.CNVFile.name}'.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to save CNV file '{Config.CNVFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to save CNV file '{Config.CNVFile.name}'. Error code: {ierr}")






            # ==========================
            #  SNP File Handling
            # ==========================
            bsprint("Checking and Loading SNP File...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if os.path.exists(Config.SNPFile) and not Config.IgnoreSNPFile:
                bsprint(f"SNP file '{Config.SNPFile.name}' found. Loading...",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                ierr = psspy.rstr(str(Config.SNPFile))  # Load the SNP File 
                if ierr == 0:
                    bsprint(f"[SUCCESS] Snapshot file '{Config.SNPFile.name}' loaded successfully.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to load SNP file '{Config.SNPFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to load SNP file '{Config.SNPFile.name}'. Error code: {ierr}")
            else:
                bsprint(f"File '{Config.SNPFile.name}' not found or ignored. Creating new SNP file...",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"Loading DYRE file '{Config.DYRFile}'",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                ierr = psspy.dyre_new_2([1, 1, 1, 1], str(Config.DYRFile))
                if ierr == 0:
                    bsprint(f"[SUCCESS] Dynamics data from file '{Config.DYRFile.name}' loaded successfully.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to load DYRE file '{Config.DYRFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to load DYRE file '{Config.DYRFile.name}'. Error code: {ierr}")
                
                bsprint (f" Saving snapshot to '{Config.SNPFile}'",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                ierr = psspy.snap([-1, -1, -1, -1, -1], str(Config.SNPFile))
                if ierr == 0:
                    bsprint(f"[SUCCESS] Snapshot saved to '{Config.SNPFile.name}'.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to save SNP file '{Config.SNPFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to save SNP file '{Config.SNPFile.name}'. Error code: {ierr}")


            bsprint("[SUCCESS] PSSE Initialization Completed Successfully.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            #█ █▄ █ █ ▀█▀ █ ▄▀█ █   █ ▀█ ▄▀█ ▀█▀ █ █▀█ █▄ █   █▀▀ █▀█ █▀▄▀█ █▀█ █   █▀▀ ▀█▀ █▀▀ █▀▄
            #█ █ ▀█ █  █  █ █▀█ █▄▄ █ █▄ █▀█  █  █ █▄█ █ ▀█   █▄▄ █▄█ █ ▀ █ █▀▀ █▄▄ ██▄  █  ██▄ █▄▀ ▄


        except Exception as e:
            bsprint(f"[ERROR] An unexpected error occurred: {e}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            if DebugPrint:
                bsprint("[DEBUG] Exception details:", app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(str(e),app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
            
            if app:
                raise
            else:
                sys.exit(1)

