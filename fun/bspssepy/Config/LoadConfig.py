# ===========================================================
#   BSPSSEPy Application - Load Configuration File
# ===========================================================
#   This module loads configuration values from a Python-based
#   config file and assigns them to the BSPSSEPy.Config class.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================

import os
import importlib.util
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint
import asyncio

async def LoadConfig(self, ConfigPath, DebugPrint=False,app=None):
    """
    Load configuration values from a specified Python config file and assign them to class attributes.
    
    Parameters:
        self (Config): The instance of the BSPSSEPy.Config class where values will be assigned.
        ConfigPath (str): The path to the Python configuration file.
        DebugPrint (bool): If True, prints detailed debug messages about the loading process.
    
    This function dynamically imports the given config file, retrieves its variables, and assigns
    them to the corresponding attributes in the Config class if they exist. Only defined attributes
    in the class are updated to prevent unintended modifications.
    
    Notes:
        - The configuration file must be a valid Python script.
        - Variables in the configuration file should be named using uppercase letters.
    """
    if (DebugPrint is None) and app:
        DebugPrint = app.DebugCheckBox.value
    
    # Check if the provided configuration file exists at the given path.
    if os.path.exists(ConfigPath):
        
        # If DebugPrint is enabled, print a debug message indicating the config file is found.
        if DebugPrint:
            bsprint(f"[DEBUG] Config file located at: {ConfigPath}",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        # Dynamically load the specified config file using the importlib module
        # This approach allows you to import Python files (configuration files) at runtime.
        spec = importlib.util.spec_from_file_location("ConfigModule", ConfigPath)
        
        # Create a module from the specification. This will act as the imported configuration file.
        ConfigModule = importlib.util.module_from_spec(spec)
        
        # If DebugPrint is enabled, print a debug message indicating the import process has started.
        if DebugPrint:
            bsprint("[DEBUG] Importing configuration module...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
                
        # Execute the module (import the configuration file) so that its contents become available.
        spec.loader.exec_module(ConfigModule)
        
        # If DebugPrint is enabled, print a debug message indicating the import process has finished.
        if DebugPrint:
            bsprint("[DEBUG] Configuration module imported successfully.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        # Now that the config file is imported as a module (ConfigModule),
        # loop over all items in the module's dictionary (its variables and values).
        for Key, Value in ConfigModule.__dict__.items():
            # Only assign values to the Config object's attributes if the key is uppercase 
            # and if the attribute exists in the current Config object (self).
            if hasattr(self, Key):
                # Update the attribute in the Config object with the value from the config file.
                setattr(self, Key, Value)
                
                # If DebugPrint is enabled, print which key-value pair was assigned to the attribute.
                if DebugPrint:
                    bsprint(f"[DEBUG] Assigned {Key} = {Value} to Config attribute.",app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    else:
        # If the provided config file does not exist at the specified path, print an error message.
        bsprint(f"[ERROR] Configuration file not found: {ConfigPath}",app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        # If DebugPrint is enabled, print a debug message indicating the error.
        if DebugPrint:
            bsprint("[DEBUG] Please check the file path and ensure it exists.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)