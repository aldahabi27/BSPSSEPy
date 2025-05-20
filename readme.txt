===========================================================
             Welcome to the BSPSSEPy Program!
===========================================================
Version: 0.4
Last Updated: 11 Feb 2025
-----------------------------------------------------------
Developed by: Ilyas Farhat
Contact: ilyas.farhat@outlook.com
-----------------------------------------------------------
Copyright (c) 2024-2025, Ilyas Farhat
All rights reserved.
-----------------------------------------------------------

BSPSSEPy Application is a Black-Start simulation tool based on PSSE Power Simulator, that uses the Python PSSE Library to run these simulations. BSPSSEPy extends the dynamic simulation capabilities of PSSE to model:

- Dynamic Black-Start behavior (phases) of non-black-start generators. It models their cranking phase, ramp-up phase (if the generator governor model does not model ramping limits.
- Can execute a black-start plan and apply AGC control during the restoration process.
- Dynamically tracks the elements in the network and monitor voltages and frequencies.

Changes in Version 0.4:
- Added BSPSSEPy Dashboard based on 'textual' python library.
- Made many changes to how the simulation works and how hte plan is being read.
- Added new flags to have more control over how the actions are executed.
- Added a new function --> GenUpdate to control generator output power (to allow to control non-AGC generators)
- Fixed few issues with the code.

Changes in Version 0.3:
- Fixed the BSPSSEPySim class code following the issues observed with generator measurement channels.
- Fixed some documentation corresponding to BSPSSEPySim


To Be Done:
- Properly finish the documentation of all main functions/classes
- Fix any remaining unclear/trial codes.
- Fix all printing messages shown in the simulation.
- Fix any [DEBUG] messages not properly formatted.


Changes in Version 0.2.1:
- Successfully models cranking phase of generator
- Rewrote the BSPSSEPyGenFunctions and modified the BSPSSEPyGen dataframe with extra information about generator phases

Changes in Version 0.2:
- Rewrote all Classes and their functions to match the new data frame content. This includes - BSPSSEPyGen, BSPSSEPyBrn, BSPSSEPyTrn, BSPSSEPyLoad, BSPSSEPyBus and their functions.
- Updated the corresponding md files for some of these new functions. This will be revisited in Ver 0.3 following the updates to be made to BSPSSEPyGen
