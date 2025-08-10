config_path = r"""I:\Work\Research\Control & Power Systems\JWSP Research\HONI Project\PSSE\BSPSSEPy\case\IEEE9\IEEE9_Ver19_Config.py"""
config_path = r"""I:\Work\Research\Control & Power Systems\JWSP Research\HONI
               Project\PSSE\BSPSSEPy\case\IEEE9\IEEE9_Ver20_Config.py"""

config_path = r"""I:\Work\Research\Control & Power Systems\JWSP Research\HONI Project\PSSE\BSPSSEPy\case\3BUS\3BUS_Ver3_Config.py"""

config_path = r"""I:\Work\Research\Control & Power Systems\JWSP Research\HONI Project\PSSE\BSPSSEPy\case\IEEE9\IEEE9_Ver1_Config.py"""


# Essential Imports to install missing libraries
import subprocess
import sys

# List of required libraries - to install any missing libraries for all methods and all submethods
RequiredLibraries = [
    "psse3601",
    "psspy",
    "dyntools",
    "os",
    "sys",
    "pathlib",
    "datetime",
    "csv",
    "matplotlib",
    "pandas",
    "plotext",
    "importlib",
    "json",
    "numbers",
    "numpy",
    "textual",
    # "BSPSSEPyApp",
]


print("Verifying that needed libraries are installed.")

# Attempt to import each library and install if missing
for lib in RequiredLibraries:
    try:
        if "." in lib:  # For local modules
            globals()[lib.split(".")[-1]] = __import__(lib, fromlist=["*"])
        else:
            globals()[lib] = __import__(lib)  # Try to import the library
        print(f"{lib} ✔")
    except ImportError:
        print(f"{lib} is missing. Installing it...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", lib]
            )  # Install the missing library
            globals()[lib] = __import__(
                lib
            )  # Try importing again after installation
            print(f"{lib} installed successfully ✔")
        except Exception as e:
            print(f"Failed to install {lib}. Error: {e}")
            print("Don't run Cell 1. Missing library cannot be installed.")
            raise SystemExit(
                f"Aborting execution due to missing library: {lib}"
            ) from e  # Stop execution


# ==========================
#  Initialize BSPSSEPy
# ==========================

# importhing those to allow the editor to pull commands for easier coding
import os
from pathlib import Path

MainFolder = Path(os.getcwd())  # This will give the current working directory
sys.path.append(str(MainFolder / "fun"))

from fun.bspssepy.bspssepy_core import BSPSSEPy

config_file = Path(config_path)
print(f"  Config File: {config_file.name}")
print(f"  Full Config File Path: {config_file}")


try:
    import asyncio

    # Call the main constructor and load the configurations for PSSE Simulation
    myBSPSSEPy = BSPSSEPy()

    asyncio.run(
        myBSPSSEPy.bspssepy_init(config_path=config_path, debug_print=False)
    )

    DebugPrint = (
        myBSPSSEPy.config.debug_print
    )  # Set debug print based on configuration

    asyncio.run(myBSPSSEPy.sim.set_black_start())
    myBSPSSEPy.sim.print_all_t_flag = True
    asyncio.run(myBSPSSEPy.sim.Run())
    myBSPSSEPy.plot(debug_print=DebugPrint)
finally:
    # Ensure the license is always released
    print("Releasing the PSSE license and halting the engine...")
    psspy.pssehalt_2()
    print("PSSE license successfully released.")
