# ===========================================================
#   BSPSSEPy Application - load Configuration File
# ===========================================================
#   This module loads configuration values from a Python-based
#   config file and assigns them to the BSPSSEPy.config class.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================

import os
import asyncio
import importlib.util
from fun.bspssepy.app.app_helper_funs import bp


async def load_config(self, config_path, debug_print=False, app=None):
    """
    load configuration values from a specified Python config file and assign
    them to class attributes.

    Parameters:
        self (config): The instance of the BSPSSEPy.config class where values
        will be assigned. ConfigPath (str): The path to the Python
        configuration file. debug_print (bool): If True, prints detailed debug
        messages about the loading process.

    This function dynamically imports the given config file, retrieves its
    variables, and assigns them to the corresponding attributes in the config
    class if they exist. Only defined attributes in the class are updated to
    prevent unintended modifications.

    Notes:
        - The configuration file must be a valid Python script.
        - Variables in the configuration file should be named using uppercase
          letters.
    """
    if (debug_print is None) and app:
        debug_print = app.debug_checkbox.value

    # Check if the provided configuration file exists at the given path.
    if os.path.exists(config_path):

        # If debug_print is enabled, print a debug message indicating the
        # config file is found.
        if debug_print:
            bp(f"[DEBUG] config file located at: {config_path}", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Dynamically load the specified config file using the importlib
        # module This approach allows you to import Python files
        # (configuration files) at runtime.
        spec = importlib.util.spec_from_file_location(
            "config_module", config_path
        )

        # Create a module from the specification. This will act as the
        # imported configuration file.
        config_module = importlib.util.module_from_spec(spec)

        # If debug_print is enabled, print a debug message indicating the
        # import process has started.
        if debug_print:
            bp("[DEBUG] Importing configuration module...", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Execute the module (import the configuration file) so that its
        # contents become available.
        spec.loader.exec_module(config_module)

        # If debug_print is enabled, print a debug message indicating the
        # import process has finished.
        if debug_print:
            bp("[DEBUG] Configuration module imported successfully.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Now that the config file is imported as a module (config_module),
        # loop over all items in the module's dictionary (its variables and
        # values).
        for key, value in config_module.__dict__.items():
            # Only assign values to the config object's attributes if the key
            # is uppercase and if the attribute exists in the current config
            # object (self).
            if hasattr(self, key):
                # Update the attribute in the config object with the value
                # from the config file.
                setattr(self, key, value)

                # If debug_print is enabled, print which key-value pair was
                # assigned to the attribute.
                if debug_print:
                    bp(
                        f"[DEBUG] Assigned {key} = {value} to "
                        "config attribute.",
                        app=app,
                    )
                    await asyncio.sleep(app.async_print_delay if app else 0)

    else:
        # If the provided config file does not exist at the specified path,
        # print an error message.
        bp(f"[ERROR] Configuration file not found: {config_path}", app=app)
        await asyncio.sleep(app.async_print_delay if app else 0)

        # If debug_print is enabled, print a debug message indicating the
        # error.
        if debug_print:
            bp(
                "[DEBUG] Please check the file path and ensure it exists.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
