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
from fun.bspssepy.sim.bspssepy_default_vars import bspssepy_default_vars_fun
from fun.bspssepy.app.app_helper_funs import bp
import asyncio
import io
from contextlib import redirect_stdout


class PSSE:
    """
    The PSSE class initializes the PSSE environment and loads system files required for simulation.

    Attributes:
        config (config): An instance of the BSPSSEPy.config class containing simulation settings.
        debug_print (bool): Enables debug messages when True.
        CaseInitializationFlag (int): Status flag for PSSE case initialization.
        default_int, default_real, default_char: Default PSSE values for missing parameters.
    """

    def __init__(self):

        pass

    async def PSSEInit(self, config, debug_print = None, app = None):
        """
        Initializes the PSSE simulation environment and loads necessary files.

        Parameters:
            config (config): The configuration object containing simulation settings.
            debug_print (bool, optional): Enables debug messages if set to True. Defaults to config.debug_print.

        This function initializes PSSE, sets up logging, loads the case files,
        runs power flow solutions, and prepares snapshot and converted files.
        """

        if debug_print is None:
            if app:
                debug_print = app.debug_checkbox.value
            else:
                debug_print = config.debug_print
        

        if debug_print:
            bp("[DEBUG] Entering PSSE Constructor...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        
        try:
            # ==========================
            #  Initialize PSSE
            # ==========================

            # Create a StringIO object to capture the output
            output_capture = io.StringIO()

            # Use the context manager to capture the stdout
            with redirect_stdout(output_capture):
                self.CaseInitializationFlag = psspy.psseinit(config.NumberOfBuses)
            # Get the captured output
            captured_output = output_capture.getvalue()
            
            bp(captured_output, app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            
            if self.CaseInitializationFlag != 0:
                # if app:
                #     raise Exception(f"PSSE initialization failed with error code {self.CaseInitializationFlag}.")
                # else:
# 
                    raise RuntimeError(f"PSSE initialization failed with error code {self.CaseInitializationFlag}.")
            else:
                bp("PSSE initialized successfully.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            if debug_print:
                bp(f"[DEBUG] Case Initialization Flag: {self.CaseInitializationFlag} (0 indicates no errors)",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)


            # Retrieve default PSSE values for inputs
            # Those values can be used when we want to modify certain parameters in the models, without changing the other parameters values. So we simply say "default" for the other values.
            self.default_int, self.default_real, self.default_char = bspssepy_default_vars_fun()
            if debug_print:
                bp("[DEBUG] Default PSSE values retrieved.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            # Redirect PSSE progress output to log file
            psspy.progress_output(2,str(config.LogFile),[0,0])
            bp(f"Log file will be saved to: {config.LogFile}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

            # ==========================
            #  load SAV File
            # ==========================
            bp("Loading SAV File",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            ierr = psspy.case(str(config.sav_file))
            if ierr == 0:
                bp(f"[SUCCESS] SAV file '{config.sav_file.name}' loaded successfully.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            else:
                # if app:
                #     raise Exception(f"[ERROR] Failed to load SAV file '{config.sav_file.name}'. Error code: {ierr}")
                # else:
                    raise RuntimeError(f"[ERROR] Failed to load SAV file '{config.sav_file.name}'. Error code: {ierr}")

            # ==========================
            #  load DYR File
            # ==========================
            bp("Loading DYR File",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            # Starting indices (use defaults unless you know what you're doing)
            startindx = [1, 1, 1, 1]
            ierr = psspy.dyre_new_2(startindx, str(config.DYRFile))  # Use CaseDYRFile directly

            # Check for errors
            if ierr == 0:
                bp(f"[SUCCESS] DYR file '{config.DYRFile.name}' loaded successfully.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            else:
                # if app:
                #     raise Exception (f"[ERROR] Failed to load DYR file '{config.DYRFile.name}'. Error code: {ierr}")
                # else:
                    raise RuntimeError(f"[ERROR] Failed to load DYR file '{config.DYRFile.name}'. Error code: {ierr}")
            
            # ==========================
            #  Power Flow Solution
            # ==========================
            bp("Running Power Flow Solution...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            for _ in range(6):
                psspy.fdns([0, 0, 0, 1, 1, 0, 99, 0])
            psspy.fnsl()
            bp("[SUCCESS] Power flow solved successfully.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

            
            
            # Voltage and frequency channels code is moved to sim.GetAllElements() due to an error in psspy that results in wrong channel measurement being recorded!
            # This error cost me a lot of time to figure out!
            
            
            


            # The following code will convert loads and generators, as well as the case file to prepare it for dynamic simulation.
            # It will generate two files, SNP and CNV. The code will check to see, if those files are available, it will read them.
            # If you encounter error, update the flags "IgnoreCNVFile" & "IgnoreSNPFile" to force generate new files (warning, this overwrites the files)


            # ==========================
            #  CNV File Handling
            # ==========================
            bp("Checking and Loading CNV File...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if os.path.exists(config.CNVFile) and not config.IgnoreCNVFile:
                bp(f"CNV file '{config.CNVFile.name}' found. Loading...",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = psspy.case(str(config.CNVFile))  # load the CNV File 
                if ierr == 0:
                    bp(f"[SUCCESS] CNV file '{config.CNVFile.name}' loaded successfully.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to load CNV file '{config.CNVFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to load CNV file '{config.CNVFile.name}'. Error code: {ierr}")
            else:
                bp(f"File '{config.CNVFile.name}' not found or ignored. Converting case '{config.sav_file.name}'",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"Importing conversion script in {config.ConvCodeFile.name}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                
                # We read the file content in ConvCodeFile
                with open(config.ConvCodeFile,"r") as file:
                    exec(file.read())
                
                bp(f"Saving the CNV File '{config.CNVFile.name}'",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = psspy.save(str(config.CNVFile))
                if ierr == 0:
                    bp(f"[SUCCESS] Converted case saved to '{config.CNVFile.name}'.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to save CNV file '{config.CNVFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to save CNV file '{config.CNVFile.name}'. Error code: {ierr}")






            # ==========================
            #  SNP File Handling
            # ==========================
            bp("Checking and Loading SNP File...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if os.path.exists(config.SNPFile) and not config.IgnoreSNPFile:
                bp(f"SNP file '{config.SNPFile.name}' found. Loading...",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = psspy.rstr(str(config.SNPFile))  # load the SNP File 
                if ierr == 0:
                    bp(f"[SUCCESS] Snapshot file '{config.SNPFile.name}' loaded successfully.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to load SNP file '{config.SNPFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to load SNP file '{config.SNPFile.name}'. Error code: {ierr}")
            else:
                bp(f"File '{config.SNPFile.name}' not found or ignored. Creating new SNP file...",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"Loading DYRE file '{config.DYRFile}'",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = psspy.dyre_new_2([1, 1, 1, 1], str(config.DYRFile))
                if ierr == 0:
                    bp(f"[SUCCESS] Dynamics data from file '{config.DYRFile.name}' loaded successfully.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to load DYRE file '{config.DYRFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to load DYRE file '{config.DYRFile.name}'. Error code: {ierr}")
                
                bp (f" Saving snapshot to '{config.SNPFile}'",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                ierr = psspy.snap([-1, -1, -1, -1, -1], str(config.SNPFile))
                if ierr == 0:
                    bp(f"[SUCCESS] Snapshot saved to '{config.SNPFile.name}'.",app=app)
                    await asyncio.sleep(app.async_print_delay if app else 0)
                else:
                    # if app:
                    #     raise Exception(f"[ERROR] Failed to save SNP file '{config.SNPFile.name}'. Error code: {ierr}")
                    # else:
                        raise RuntimeError(f"[ERROR] Failed to save SNP file '{config.SNPFile.name}'. Error code: {ierr}")


            bp("[SUCCESS] PSSE Initialization Completed Successfully.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

            #█ █▄ █ █ ▀█▀ █ ▄▀█ █   █ ▀█ ▄▀█ ▀█▀ █ █▀█ █▄ █   █▀▀ █▀█ █▀▄▀█ █▀█ █   █▀▀ ▀█▀ █▀▀ █▀▄
            #█ █ ▀█ █  █  █ █▀█ █▄▄ █ █▄ █▀█  █  █ █▄█ █ ▀█   █▄▄ █▄█ █ ▀ █ █▀▀ █▄▄ ██▄  █  ██▄ █▄▀ ▄


        except Exception as e:
            bp(f"[ERROR] An unexpected error occurred: {e}",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            if debug_print:
                bp("[DEBUG] Exception details:", app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(str(e),app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
            
            if app:
                raise
            else:
                sys.exit(1)

