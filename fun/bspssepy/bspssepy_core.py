# # ===========================================================
# #   BSPSSEPy Application - Main Simulation Class
# # ===========================================================
# #   This class handles the BSPSSEPy simulation framework.
# #   It consists of the following core components:
# #
# #   1. BSPSSEPy.PSSE: Handles PSSE simulation link (establishes the connection with PSSE).
# #   2. BSPSSEPy.config: Stores all configuration settings and input parameters.
# #   3. BSPSSEPy.sim: Initalizes the power system, establishes black-start and runs the actual simulation logic.
# #
# #   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
# #   Copyright (c) 2024-2025, Ilyas Farhat
# #   Contact: ilyas.farhat@outlook.com
# # ===========================================================

# from .config.config import config
# from .psse.psse import PSSE
# from .sim.sim import sim
# from .plot.plot import *
# # from fun.bspssepy.app.app_helper_funs import * # Importing custom helper functions
# from fun.bspssepy.app.app_helper_funs import bp

# import asyncio

# class BSPSSEPy:
#     def __init__(self, CaseName=None, Ver=None, ConfigPath=None, debug_print=None, app=None):
#         self.ConfigPath = ConfigPath
# ===========================================================
#   BSPSSEPy Application - Main Simulation Class
# ===========================================================
#   This class handles the BSPSSEPy simulation framework.
#   It consists of the following core components:
#
#   1. BSPSSEPy.PSSE: Handles PSSE simulation link (establishes the connection with PSSE).
#   2. BSPSSEPy.config: Stores all configuration settings and input parameters.
#   3. BSPSSEPy.sim: Initalizes the power system, establishes black-start and runs the actual simulation logic.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================

from .config.config import config
from .psse.psse import PSSE
from .sim.sim import sim
from .plot.plot import *
from fun.bspssepy.app.app_helper_funs import bp

class BSPSSEPy:
    def __init__(self):
        pass

    async def BSPSSEPyInit(self, CaseName=None, Ver=None, ConfigPath=None, debug_print=None, app=None):   
        self.InitializationCompleted = False
         
        if app:
            debug_print = app.debug_checkbox.value
        
        if debug_print:
            bp("[DEBUG] Entered BSPSSEPy Constructor",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp("[DEBUG] Initializing configuration settings...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        # await asyncio.sleep(app.async_print_delay if app else 0)
        # Initialize configuration settings
        self.config = config()
        await self.config.ConfigInit(CaseName=CaseName, Ver=Ver, ConfigPath=ConfigPath, debug_print=debug_print, app=app)

        if debug_print:
            bp("[DEBUG] Configuration settings initialized successfully.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp("[DEBUG] Initializing PSSE simulation module...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        
        # Initialize PSSE module
        self.PSSE = PSSE()
        await self.PSSE.PSSEInit(config=self.config, app = app)
        
        if debug_print:
            bp("[DEBUG] PSSE simulation module initialized successfully.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp("[DEBUG] Initializing Simulation logic...",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)

        # Initialize simulation logic
        self.sim = sim()
        await self.sim.SimInit(config=self.config, PSSE=self.PSSE, debug_print=debug_print,app=app)
        
        if debug_print:
            bp("[DEBUG] Simulation logic initialized successfully.", app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
            bp("[DEBUG] BSPSSEPy Constructor completed.",app=app)
            await asyncio.sleep(app.async_print_delay if app else 0)
        
        self.InitializationCompleted = True
    
    def Plot(self, debug_print=False,app=None):
        if app:
            debug_print = app.debug_checkbox.value

        if debug_print:
            bp("[DEBUG] Entering Plot function...",app)
            bp("[DEBUG] Calling BSPSSEPyPlotFreq...",app)
        
        if app:
            BaseFrequency = app.bspssepy.sim.BaseFrequency
        else:
            BaseFrequency = self.sim.BaseFrequency

        # Generate plots
        BSPSSEPyPlotGen(config=self.config, PSSE=self.PSSE, debug_print=debug_print, BaseFrequency = BaseFrequency)
        BSPSSEPyPlotFreq(config=self.config, PSSE=self.PSSE, debug_print=debug_print, BaseFrequency = BaseFrequency)

        if debug_print:
            bp("[DEBUG] Plot function completed.",app)




    # def BSPSSEPyInit(self, app = None):
    #         bp("[DEBUG] Entered BSPSSEPy Constructor", app)
    #         bp("[DEBUG] Initializing configuration settings...", app)



    #     await asyncio.sleep(0.0001)
        
        # Initialize configuration settings
    #     self.config = config(CaseName=CaseName, Ver=Ver, ConfigPath=ConfigPath, debug_print=debug_print, app=None)

    #     if debug_print:
    #         print("[DEBUG] Configuration settings initialized successfully.")
    #         print("[DEBUG] Initializing PSSE simulation module...")
        
    #     # Initialize PSSE module
    #     self.PSSE = PSSE(config=self.config, app=None)
        
    #     if debug_print:
    #         print("[DEBUG] PSSE simulation module initialized successfully.")
    #         print("[DEBUG] Initializing Simulation logic...")

    #     # Initialize simulation logic
    #     self.sim = sim(config=self.config, PSSE=self.PSSE, debug_print=debug_print, app=None)


    #     if debug_print:
    #         print("[DEBUG] Simulation logic initialized successfully.")
    #         print("[DEBUG] BSPSSEPy Constructor completed.")

    
    # def Plot(self, debug_print=False):
    #     if debug_print:
    #         print("[DEBUG] Entering Plot function...")
    #         print("[DEBUG] Calling BSPSSEPyPlotFreq...")
        
        
    #     # Generate plots
    #     BSPSSEPyPlotGen(config=self.config, PSSE=self.PSSE, debug_print=debug_print, app=None)
    #     BSPSSEPyPlotFreq(config=self.config, PSSE=self.PSSE, debug_print=debug_print, app=None)

    #     if debug_print:
    #         print("[DEBUG] Plot function completed.")


