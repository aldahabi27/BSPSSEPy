"""
============================================
BSPSSEPy Application - Main Simulation Class
============================================
This class handles the BSPSSEPy simulation framework. It consists of the
following core components:

1. BSPSSEPy.PSSE: Handles PSSE simulation link (establishes the connection
   with PSSE).
2. BSPSSEPy.config: Stores all configuration settings and input parameters.
3. BSPSSEPy.sim: Initalizes the power system, establishes black-start and runs
   the actual simulation logic.

Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025) Copyright (c) 2024-2025, Ilyas
Farhat Contact: ilyas.farhat@outlook.com
============================================
"""

import asyncio

from .config.config import config
from .psse.psse import psse
from .sim.sim import sim
from .plot.plot import bspssepy_plot_freq, bspssepy_plot_gen
from .app.app_helper_funs import bp


class BSPSSEPy:
    def __init__(self):
        self.init_completed: bool = False
        self.config: config = None
        self.psse: psse = None
        self.sim: sim = None

    async def bspssepy_init(
        self,
        CaseName=None,
        Ver=None,
        ConfigPath=None,
        debug_print=None,
        app=None,
    ):
        self.init_completed = False

        if app:
            debug_print = app.debug_checkbox.value

        if debug_print:
            bp("[DEBUG] Entered BSPSSEPy Constructor", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp("[DEBUG] Initializing configuration settings...", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Initialize configuration settings
        self.config = config()
        await self.config.config_init(
            case_name=CaseName,
            ver=Ver,
            config_path=ConfigPath,
            debug_print=debug_print,
            app=app,
        )

        if debug_print:
            bp(
                "[DEBUG] Configuration settings initialized successfully.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp("[DEBUG] Initializing PSSE simulation module...", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Initialize PSSE module
        self.psse = psse()
        await self.psse.PSSEInit(config=self.config, app=app)

        if debug_print:
            bp(
                "[DEBUG] PSSE simulation module initialized successfully.",
                app=app,
            )
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp("[DEBUG] Initializing Simulation logic...", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Initialize simulation logic
        self.sim = sim()
        await self.sim.sim_init(
            config=self.config,
            PSSE=self.psse,
            debug_print=debug_print,
            app=app,
        )

        if debug_print:
            bp("[DEBUG] Simulation logic initialized successfully.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp("[DEBUG] BSPSSEPy Constructor completed.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        self.init_completed = True

    def plot(self, debug_print=False, app=None):
        if app:
            debug_print = app.debug_checkbox.value

        if debug_print:
            bp("[DEBUG] Entering Plot function...", app)
            bp("[DEBUG] Calling BSPSSEPyPlotFreq...", app)

        if app:
            base_freq = app.bspssepy.sim.base_freq
        else:
            base_freq = self.sim.base_freq

        # Generate plots
        bspssepy_plot_gen(
            config=self.config,
            psse=self.psse,
            debug_print=debug_print,
            base_freq=base_freq,
        )
        bspssepy_plot_freq(
            config=self.config,
            psse=self.psse,
            debug_print=debug_print,
            base_freq=base_freq,
        )

        if debug_print:
            bp("[DEBUG] Plot function completed.", app)
