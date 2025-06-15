"""
Entry point for BSPSSEPy Application
Run this with: python -m bspssepy


"""

from __future__ import annotations

import subprocess
import sys
import pkg_resources


REQUIRED_LIBRARIES = [
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
    # "textual==2.1.1",
    "textual",
    # "textual-dev",
    "asyncio",
    "time",
    "functools",
    "random",
    "io",
    "contextlib",
    # "BSPSSEPyApp",
]


def ensure_dependencies():
    """ Check if required libraries are installed, and install them if not. """
    for lib in REQUIRED_LIBRARIES:
        lib_name, _, lib_version = lib.partition("==")
        try:
            # Try to import the library
            globals()[lib_name] = __import__(lib_name)
            if lib_version:
                installed_version = (
                    pkg_resources.get_distribution(lib_name).version
                )
                if installed_version != lib_version:
                    raise ImportError(
                        f"{lib_name} version {lib_version} is required, "
                        f"but version {installed_version} is installed."
                    ) from None  # or from e if catching an error

            print(
                f"{lib_name}"
                f"{f' {installed_version}' if lib_version else ''} ✔"
            )
        except ImportError as ie:
            print(
                f"{lib} is missing or has the wrong version. Installing it..."
            )
            try:
                # Install the missing or correct version of the library
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", lib]
                    )
                # Try importing again after installation
                globals()[lib_name] = __import__(lib_name)
                installed_version = (
                    pkg_resources.get_distribution(lib_name).version
                )
                if lib_version and installed_version != lib_version:
                    raise ImportError(
                        f"{lib_name} version {lib_version} is required, "
                        f"but version {installed_version} is installed."
                    ) from ie
                print(f"{lib} installed successfully ✔")
            except Exception as e:
                print(f"Failed to install {lib}. Error: {e}")
                print("Don't run Cell 1. Missing library cannot be installed.")
                # Stop execution
                raise SystemExit(
                    f"Aborting execution due to missing library: {lib}"
                ) from e


def display_banner():
    """ Display the welcome banner for the application. """
    # pylint: disable=import-outside-toplevel
    from fun.bspssepy.meta import VER_NUM, current_timestamp
    current_date = current_timestamp()
    print("===========================================================")
    print("              Welcome to BSPSSEPy Application              ")
    print("===========================================================")
    print(f"Version: {VER_NUM}")
    print("Last Updated: 20 May 2025")
    print(f"Current Date and Time: {current_date}")
    print("-----------------------------------------------------------")
    print("Developed by: Ilyas Farhat")
    print("Contact: ilyas.farhat@outlook.com")
    print("Copyright (c) 2024-2025, Ilyas Farhat")
    print("All rights reserved.")
    print("-----------------------------------------------------------")


def main():
    """ Main function to run the BSPSSEPy application. """
    display_banner()
    print("Verifying that needed libraries are installed.")
    ensure_dependencies()
    print("Loading BSPSSEPyApp GUI. Please wait...")

    # pylint: disable=import-outside-toplevel
    from fun.bspssepy.app.app import launch_app
    launch_app()


if __name__ == "__main__":
    main()
