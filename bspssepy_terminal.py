ConfigPath = r"""Y:\Ilyas\Work\Research\Control & Power Systems\JWSP Research\HONI Project\PSSE\BSPSSEPy\case\IEEE9\IEEE9_Ver13_Config.py"""  # None
ConfigPath = r"""E:\Ilyas\Work\Research\Control & Power Systems\JWSP Research\HONI Project\PSSE\BSPSSEPy\case\IEEE9\IEEE9_Ver15_Config.py"""  # None
# ConfigPath = r"""E:\Ilyas\Work\Research\Control & Power Systems\JWSP Research\HONI Project\PSSE\BSPSSEPy\case\IEEE9\IEEE9_Ver12_Config.py"""  # None


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
            )  # Stop execution


# ==========================
#  Initialize BSPSSEPy
# ==========================

# importhing those to allow the editor to pull commands for easier coding
import os
from pathlib import Path

MainFolder = Path(os.getcwd())  # This will give the current working directory
sys.path.append(str(MainFolder / "fun"))

from fun.bspssepy.bspssepy_core import BSPSSEPy

config_file = Path(ConfigPath)
print(f"  Config File: {config_file.name}")
print(f"  Full Config File Path: {config_file}")


try:
    import asyncio

    # Call the main constructor and load the configurations for PSSE Simulation
    myBSPSSEPy = BSPSSEPy()

    asyncio.run(
        myBSPSSEPy.BSPSSEPyInit(ConfigPath=ConfigPath, debug_print=False)
    )

    DebugPrint = (
        myBSPSSEPy.config.debug_print
    )  # Set debug print based on configuration

    asyncio.run(myBSPSSEPy.sim.SetBlackStart())
    myBSPSSEPy.sim.print_all_t_flag = True
    asyncio.run(myBSPSSEPy.sim.Run())
    asyncio.run(myBSPSSEPy.Plot(debug_print=DebugPrint))

finally:
    # Ensure the license is always released
    print("Releasing the PSSE license and halting the engine...")
    psspy.pssehalt_2()
    print("PSSE license successfully released.")
