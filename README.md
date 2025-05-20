# Welcome to the BSPSSEPy Program

**Version:** 0.5-dev  
**Last Updated:** 20 May 2025  
**Developed by:** Ilyas Farhat  
**Contact:** ilyas.farhat@outlook.com  
**Copyright (c) 2024–2025**, Ilyas Farhat  
_All rights reserved._

---

## Overview

BSPSSEPy Application is a Black-Start simulation tool based on PSSE Power Simulator, that uses the Python PSSE Library to run these simulations. BSPSSEPy extends the dynamic simulation capabilities of PSSE to model:

- Dynamic Black-Start behavior (phases) of non-black-start generators. It models their cranking phase, ramp-up phase (if the generator governor model does not model ramping limits.
- Can execute a black-start plan and apply AGC control during the restoration process.
- Dynamically tracks the elements in the network and monitor voltages and frequencies.

---

## ~~Changes~~ Goals in Version 0.5

- Rewriting the whole application code following pip8 standard.
- Grouping Measurements in one main function group for all elements.
- Generating new documentation following the new structure.
- Extending the functionality to include BESS modeling and control.
- Fixing minor GUI glitches and upgrading the dependencies if needed.

---

## Changes in Version 0.4

- Added BSPSSEPy Dashboard based on the `textual` Python library.
- Made many changes to how the simulation works and how the plan is being read.
- Introduced new flags for greater control over action execution.
- Added new function `GenUpdate` to control output of non-AGC generators.
- Fixed various issues in the code.

---

## Changes in Version 0.3

- Fixed `BSPSSEPySim` class to address generator measurement channel issues.
- Updated documentation for `BSPSSEPySim`.

---

## Changes in Version 0.2.1

- Successfully modeled the cranking phase of generators.
- Refactored `BSPSSEPyGenFunctions` and extended the generator dataframe with phase info.

---

## Changes in Version 0.2

- Rewrote all classes to align with the updated dataframe structure (`BSPSSEPyGen`, `BSPSSEPyBrn`, `BSPSSEPyTrn`, `BSPSSEPyLoad`, `BSPSSEPyBus`).
- Updated some associated markdown documentation (to be revisited in v0.3).

