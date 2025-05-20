# ===========================================================
#   BSPSSEPy Application - Main Simulation Class
# ===========================================================
#   This class handles the BSPSSEPy simulation framework.
#   It consists of the following core components:
#
#   1. BSPSSEPy.PSSE: Handles PSSE simulation link (establishes the connection with PSSE).
#   2. BSPSSEPy.Config: Stores all configuration settings and input parameters.
#   3. BSPSSEPy.Sim: Initalizes the power system, establishes black-start and runs the actual simulation logic.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================

from .Config.Config import Config
from .PSSE.PSSE import PSSE
from .Sim.Sim import Sim
from .Plot.Plot import *
# from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import * # Importing custom helper functions
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint

import asyncio

class BSPSSEPy:
    def __init__(self, CaseName=None, Ver=None, ConfigPath=None, DebugPrint=None, app=None):
        self.ConfigPath = ConfigPath


# ===========================================================
#   BSPSSEPy Application - Main Simulation Class
# ===========================================================
#   This class handles the BSPSSEPy simulation framework.
#   It consists of the following core components:
#
#   1. BSPSSEPy.PSSE: Handles PSSE simulation link (establishes the connection with PSSE).
#   2. BSPSSEPy.Config: Stores all configuration settings and input parameters.
#   3. BSPSSEPy.Sim: Initalizes the power system, establishes black-start and runs the actual simulation logic.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================

from .Config.Config import Config
from .PSSE.PSSE import PSSE
from .Sim.Sim import Sim
from .Plot.Plot import *
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint

class BSPSSEPy:
    def __init__(self):
        pass

    async def BSPSSEPyInit(self, CaseName=None, Ver=None, ConfigPath=None, DebugPrint=None, app=None):   
        self.InitializationCompleted = False
         
        if app:
            DebugPrint = app.DebugCheckBox.value
        
        if DebugPrint:
            bsprint("[DEBUG] Entered BSPSSEPy Constructor",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint("[DEBUG] Initializing configuration settings...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        # await asyncio.sleep(app.bsprintasynciotime if app else 0)
        # Initialize configuration settings
        self.Config = Config()
        await self.Config.ConfigInit(CaseName=CaseName, Ver=Ver, ConfigPath=ConfigPath, DebugPrint=DebugPrint, app=app)

        if DebugPrint:
            bsprint("[DEBUG] Configuration settings initialized successfully.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint("[DEBUG] Initializing PSSE simulation module...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        # Initialize PSSE module
        self.PSSE = PSSE()
        await self.PSSE.PSSEInit(Config=self.Config, app = app)
        
        if DebugPrint:
            bsprint("[DEBUG] PSSE simulation module initialized successfully.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint("[DEBUG] Initializing Simulation logic...",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Initialize simulation logic
        self.Sim = Sim()
        await self.Sim.SimInit(Config=self.Config, PSSE=self.PSSE, DebugPrint=DebugPrint,app=app)
        
        if DebugPrint:
            bsprint("[DEBUG] Simulation logic initialized successfully.", app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
            bsprint("[DEBUG] BSPSSEPy Constructor completed.",app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        
        self.InitializationCompleted = True
    
    def Plot(self, DebugPrint=False,app=None):
        if app:
            DebugPrint = app.DebugCheckBox.value

        if DebugPrint:
            bsprint("[DEBUG] Entering Plot function...",app)
            bsprint("[DEBUG] Calling BSPSSEPyPlotFreq...",app)
        
        if app:
            BaseFrequency = app.myBSPSSEPy.Sim.BaseFrequency
        else:
            BaseFrequency = self.Sim.BaseFrequency

        # Generate plots
        BSPSSEPyPlotGen(Config=self.Config, PSSE=self.PSSE, DebugPrint=DebugPrint, BaseFrequency = BaseFrequency)
        BSPSSEPyPlotFreq(Config=self.Config, PSSE=self.PSSE, DebugPrint=DebugPrint, BaseFrequency = BaseFrequency)

        if DebugPrint:
            bsprint("[DEBUG] Plot function completed.",app)




    # def BSPSSEPyInit(self, app = None):
    #         bsprint("[DEBUG] Entered BSPSSEPy Constructor", app)
    #         bsprint("[DEBUG] Initializing configuration settings...", app)



    #     await asyncio.sleep(0.0001)
        
        # Initialize configuration settings
    #     self.Config = Config(CaseName=CaseName, Ver=Ver, ConfigPath=ConfigPath, DebugPrint=DebugPrint, app=None)

    #     if DebugPrint:
    #         print("[DEBUG] Configuration settings initialized successfully.")
    #         print("[DEBUG] Initializing PSSE simulation module...")
        
    #     # Initialize PSSE module
    #     self.PSSE = PSSE(Config=self.Config, app=None)
        
    #     if DebugPrint:
    #         print("[DEBUG] PSSE simulation module initialized successfully.")
    #         print("[DEBUG] Initializing Simulation logic...")

    #     # Initialize simulation logic
    #     self.Sim = Sim(Config=self.Config, PSSE=self.PSSE, DebugPrint=DebugPrint, app=None)


    #     if DebugPrint:
    #         print("[DEBUG] Simulation logic initialized successfully.")
    #         print("[DEBUG] BSPSSEPy Constructor completed.")

    
    # def Plot(self, DebugPrint=False):
    #     if DebugPrint:
    #         print("[DEBUG] Entering Plot function...")
    #         print("[DEBUG] Calling BSPSSEPyPlotFreq...")
        
        
    #     # Generate plots
    #     BSPSSEPyPlotGen(Config=self.Config, PSSE=self.PSSE, DebugPrint=DebugPrint, app=None)
    #     BSPSSEPyPlotFreq(Config=self.Config, PSSE=self.PSSE, DebugPrint=DebugPrint, app=None)

    #     if DebugPrint:
    #         print("[DEBUG] Plot function completed.")


