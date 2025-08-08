# Welcome to the BSPSSEPy Program

> **Version:** 0.6  
**Last Updated:** 10 Aug 2025  
**Developed by:** Ilyas Farhat  
**Contact:** [ilyas.farhat@outlook.com](mailto:ilyas.farhat@outlook.com)  
**Copyright (c) 2024–2025**, Ilyas Farhat  
_All rights reserved._

---

## Overview

BSPSSEPy is a Black-Start simulation tool built on the PSSE Power Simulator, using the Python PSSE API to execute restoration studies. It extends PSSE’s dynamic simulation capabilities to:

* Model dynamic Black-Start phases of non-black-start generators, including cranking and ramp-up (if not already modeled in the governor).
* Execute black-start restoration plans and apply AGC during the process.
* Continuously track network elements and monitor voltage and frequency stability.

---

## First-Time Setup & Download

1. **Download BSPSSEPy** from the official GitHub page: [BSPSSEPy GitHub
   Page](https://github.com/aldahabi27/BSPSSEPy)  
    
  <p align="center">
  <a href="doc/images/setup_download_github.png">
    <img src="doc/images/setup_download_github.png" alt="GitHub BSPSSEPy Release Page" width="600">
  </a>
  </p>


2. **Extract the ZIP package** to your preferred folder. (here we renamed the
   folder to ___BSPSSEPy___)
  <p align="center">
  <a href="doc/images/setup_extract_files.png">
    <img src="doc/images/setup_extract_files.png" alt="Extracting BSPSSEPy Files" width="600">
  </a>
  </p>

3. **Open the terminal** in the BSPSSEPy main folder. This guide uses *Microsoft Windows Terminal*.

  <p align="center">
  <a href="doc/images/setup_open_terminal.png">
    <img src="doc/images/setup_open_terminal.png" alt="Opening Windows Terminal in BSPSSEPy Folder" width="600">
  </a>
  </p>  

> [Microsoft Store Link – Windows Terminal](https://apps.microsoft.com/detail/9n0dx20hk701)
   
---

## Prerequisites

Before running BSPSSEPy for the first time, ensure you have:

1. **PSSE Version 36.1**
2. **Python 3.11.9** (installed via PSSE installer)
3. **Required Python Libraries**

BSPSSEPy will automatically check for missing libraries and attempt to install
them. However, ensure you have these core Python modules preinstalled
(_usually are installed by default with Python_):

* `subprocess`
* `sys`

**Additional required libraries (_will be auto-installed_):**

1. `psse3601`
2. `psspy`
3. `dyntools`
4. `os`
5. `sys`
6. `pathlib`
7. `datetime`
8. `csv`
9. `matplotlib`
10. `pandas`
11. `plotext`
12. `importlib`
13. `json`
14. `numbers`
15. `numpy`
16. `textual`

---

## First Run – Installing Libraries

1. **Navigate to BSPSSEPy folder in Terminal**
```bash
cd "D:\Tutorial\BSPSSEPy"
```
___note: Replace the directory with your BSPSSEPy directory___

  <p align="center">
  <a href="doc/images/run_navigate_terminal.png">
    <img src="doc/images/run_navigate_terminal.png" alt="Navigating to BSPSSEPy in Terminal" width="600">
  </a>
  </p> 

2. **Run the program**

```bash
python .\__main__.py
```

  <p align="center">
  <a href="doc/images/run_first_launch.png">
    <img src="doc/images/run_first_launch.png" alt="Running BSPSSEPy First Time" width="600">
  </a>
  </p> 

3. **Library check and installation process**
  <p align="center">
  <a href="doc/images/run_checking_libraries.png">
    <img src="doc/images/run_checking_libraries.png" alt="Running BSPSSEPy First Time - Checking Python Libraries - detected missing libraries and attempted to install them" width="600">
  </a>
  </p> 

  <p align="center">
  <a href="doc/images/run_installing_libraries.png">
    <img src="doc/images/run_installing_libraries.png" alt="Running BSPSSEPy First Time - successfully installed missing libraries" width="600">
  </a>
  </p> 

  <p align="center">
  <a href="doc/images/run_bug_warning.png">
    <img src="doc/images/run_bug_warning.png" alt="Running BSPSSEPy First Time - Installation Completed with Minor Bug Warning" width="600">
  </a>
  </p> 

4. **Restart after installation (_if error shows up_)**

```bash
python .\__main__.py
```
  <p align="center">
  <a href="doc/images/run_all_loaded.png">
    <img src="doc/images/run_all_loaded.png" alt="Running BSPSSEPy Post Installation -All Libraries Loaded Successfully" width="600">
  </a>
  </p> 

  <p align="center">
  <a href="doc/images/run_gui_loaded.png">
    <img src="doc/images/run_gui_loaded.png" alt="Running BSPSSEPy Post Installation -BSPSSEPy GUI Loaded Successfully" width="600">
  </a>
  </p> 

---

## Running a Simulation

---

### Case Folder Layout

Each study case lives in its own subfolder under `case/`, with files sharing the same base name:

```
case/IEEE9/
  IEEE9_Ver1.sav
  IEEE9_Ver1.dyr
  IEEE9_Ver1_Config.py
  IEEE9_Ver1_Conv.py
  IEEE9_Ver1.csv
```

---

### Step 1: Prepare Power System Case Files

Prepare a `.sav` power system case file and a `.dyr` dynamic data file in PSSE. Ensure:

* **All device names** in the case match the names in your BSPSSEPy control plan CSV (more on that later).
* Follow the recommended naming convention:

| Element Type                             | Naming Pattern | Description & Rules                                                                                                                                                                          |
| ---------------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Generator**                            | `GEN#@`        | `#` = bus number. `@` = device order at that bus (`A`, `B`, `C`, ...). Example: `GEN55A`, `GEN55B`.                                                                                          |
| **Branch (Transmission Line)**           | `BRN#_#@`      | `#_#` = `from_bus` **underscore** `to_bus`. **Always** write the smaller bus number first (`min_bus_max_bus`). Example: line between 4 and 15 is `BRN4_15A` (even if power flows from 15→4). |
| **Two‑Winding Transformer (2W TF)**      | `TWTF#_#@`     | Same ordering rule as branches: `TWTFmin_bus_max_bus@`. Example: `TWTF7_13A`.                                                                                                                |
| **Load**                                 | `LOAD#@`       | `#` = bus number; `@` = device order. Example: `LOAD15A`, `LOAD15B`.                                                                                                                         |
| **Battery Energy Storage System (BESS)** | `BESS#@`       | `#` = bus number; `@` = device order. Example: `BESS5A`.                                                                                                                                     |

  
> **Device order (`@`) guidance:** Use `A, B, C, ...` for parallel units at the same bus. If you exceed 26, continue with `AA, AB, ...`.
>
> * Currently, only **two-winding transformers** are supported. For other transformer types, use a clear naming scheme and update BSPSSEPy accordingly.
> * BESS can be generalized to other IBRs with code adjustments.
> * If only one element is present at a bus __DON'T PUT A LETTER SUFFIX__

Optional but recommended: prepare an **SLD file** in PSSE for better visualization during analysis.

---


### Step 2: BSPSSEPy Config File (drop‑in template)

Name this file to match your case, e.g. `IEEE9_Ver1_Config.py` (or `IEEE9_Config.py` if you only have one variant). Adjust the values to your study.

```python
"""
BSPSSEPy case configuration file.

Edit values to match your PSSE case and study needs. This file is imported by
BSPSSEPy at runtime; keep variable names in snake_case.
"""

# -------------------------
# Core case identification
# -------------------------
case_name = "IEEE9"  # Should match the name of the case folder exactly.

# Version number from the .sav file name (e.g., 3Bus_Ver2.sav). Use -1 if no version is specified.
ver = 1

# Number of buses in the system. If unsure, leave as 0, and the code will derive this automatically from the case data.
num_of_buses = 50

# -------------------------
# Channel / monitoring setup
# -------------------------
# Specify buses to monitor voltage as a list of bus numbers.
# Use 'Range(start, end)' syntax to indicate a range of buses.
# Flag 'v_flag' may override this setting when non-zero.
v_buses_to_monitor = range(1, 10)

# Specify buses to monitor frequency as a list of bus numbers.
# Flag 'freq_flag' may override this setting when non-zero.
freq_buses_to_monitor = [1, 2, 3, 5]

# Flag for voltage monitoring behavior (not active yet):
# 0 = use specified buses, 1 = all generator buses,
# 2 = all transformer buses, 3 = gen+TF buses,
# 4 = all load buses, 5 = all buses.
v_flag = 0

# Flag for frequency monitoring behavior (not active yet):
# 0 = use specified buses, 1 = all generator buses,
# 2 = all transformer buses, 3 = gen+TF buses,
# 4 = all load buses, 5 = all buses.
freq_flag = 0

# -------------------------
# Simulation timing
# -------------------------
# Time step for the simulation in seconds. Default is 1ms (0.001).
sim_time_step = 1e-3  # seconds

# Frequency filtering threshold for simulation in seconds. Default is 4 × sim_time_step.
sim_freq_filter = 4 * sim_time_step

# Maximum iterations allowed for PSSE Newton-Raphson solver. Default is 100.
psse_max_iter_newton_raphson = 100

# File regeneration (CNV/SNP)
# If True, forces regeneration regardless of file existence; if False, reuses existing when present.
ignore_cnv_file = True
ignore_snp_file = True

# -------------------------
# BSPSSEPy supervisor timing
# -------------------------
# BSPSSEPy Hard Time Limit in minutes (ignored if bspssepy_hard_time_limit_flag is False)
bspssepy_hard_time_limit = 10  # minutes

# If True, enforce a hard wall-clock limit on the simulation; if False, no hard limit.
bspssepy_hard_time_limit_flag = True

# BSPSSEPy Time Step in seconds
# This timestep controls the Python supervisor execution rate (AGC, actions, etc.).
# Note: This is different from the PSSE dynamic time step (sim_time_step).
bspssepy_time_step = 1  # seconds

# Controls the frequency of progress print messages (minutes).
bspssepy_progress_print_time = 1  # minutes

# -------------------------
# Generator configuration table
# -------------------------
# Each generator dictionary in `gen_config` must define:
#
# - Generator Name (str): Unique generator ID in PSSE & BSPSSEPy. Must match .sav/.dyr exactly.
# - Bus Name (str): PSSE bus name where generator is connected.
# - Status (int): Initial state: 0 OFF, 1 Cranking, 2 Ramp-up, 3 Ready/Active.
#   * For BS units, this is auto-forced to 3 at runtime.
# - load Name (str): Name of the corresponding cranking load, if any.
# - Cranking Time (float): Time for cranking phase, in minutes.
# - Ramp Rate (float): Ramp-up rate in MW/min; ignored if UseGenRampRate=False.
# - Generator Type (str): "BS" for black-start, "NBS" for non-black-start.
# - Cranking load Array (list[float]): [PL, QL, IP, IQ, YP, YQ, PF]
#     PL (MW)  – Constant power P
#     QL (MVAr) – Constant power Q
#     IP – Constant current P
#     IQ – Constant current Q
#     YP – Constant admittance P
#     YQ – Constant admittance Q
#     PF – Power factor (optional)
#     * For BS units, set all to zero.
# - AGC Participation Factor (float): Share of AGC regulation (sum over gens ≈ 1.0).
# - load Damping Constant (float): Damping constant D for frequency response.
# - Effective Speed Droop (float): Droop R in p.u. (e.g., 0.05 for 5%).
# - Bias Scaling (float): Multiplier on AGC bias term.
# - POPF (float): Governor power reference (MW).
# - QOPF (float): Voltage/reactive reference (MVAr).
# - UseGenRampRate (bool): True ⇒ use config Ramp Rate; False ⇒ use model's internal ramp rate.
# - Load Enabled Response (bool): True ⇒ output adjusts for anticipated load connection, using LERPF.
# - LERPF (float): Load Enabled Response Participation Factor. -1 ⇒ use AGC PF; 0–1 ⇒ explicit share.
# - Inertia Constant (float): H in seconds, representing kinetic energy in rotor mass.

gen_config = [
    {
        "Generator Name": "GEN1",
        "Bus Name": "Bus1",
        "Status": 3,  # BS unit ⇒ status forced to 3 internally (Ready/Active)
        "load Name": "CLGEN1",
        "Cranking Time": 4.0,       # minutes
        "Ramp Rate": 0.2 * 247.5,   # MW/min
        "Generator Type": "BS",    # BS or NBS
        "Cranking load Array": [0, 0, 0, 0, 0, 0],  # BS ⇒ no cranking load used
        "AGC Participation Factor": 1,   # share for AGC distribution (e.g., 1/3)
        "load Damping Constant": 0,      # D
        "Effective Speed Droop": 0.05,   # R
        "Bias Scaling": 1,               # Effective Bias = Bias * Bias Scaling
        "POPF": 45.8217,  # Governor reference (MW)
        "QOPF": -42.6377, # Voltage/reactive reference (MVAr)
        "UseGenRampRate": False,  # True ⇒ use config Ramp Rate; False ⇒ use model limits
        "Load Enabled Response": False,  # True ⇒ supply based on anticipated load-enabled using LERPF
        "LERPF": -1,  # -1 ⇒ use AGC PF; else 0≤LERPF≤1 and sum over gens = 1
        "Inertia Constant": 13.7363,  # H (s)
    },
    {
        "Generator Name": "GEN2",
        "Bus Name": "Bus2",
        "Status": 0,  # NBS initially OFF
        "load Name": "CLGEN2",
        "Cranking Time": 60,        # minutes
        "Ramp Rate": 0.2 * 192,     # MW/min
        "Generator Type": "NBS",
        # "Cranking load Array": [0.05, 0.02, 0, 0, 0, 0],
        "Cranking load Array": [9.6, 0, 0, 0, 0, 0],
        "AGC Participation Factor": 0,
        "load Damping Constant": 0,
        "Effective Speed Droop": 0.05,
        "Bias Scaling": 1,
        "POPF": 0,       # MW governor reference (set if pre-scheduling P)
        "QOPF": -39.7548,
        "UseGenRampRate": False,  # True ⇒ use config Ramp Rate; False ⇒ use model limits
        "Load Enabled Response": False,
        "LERPF": -1,
        "Inertia Constant": 8.3136,
    },
    {
        "Generator Name": "GEN3",
        "Bus Name": "Bus3",
        "Status": 0,  # NBS initially OFF
        "load Name": "CLGEN3",
        "Cranking Time": 40,        # minutes
        "Ramp Rate": 0.1 * 128,     # MW/min
        "Generator Type": "NBS",
        # "Cranking load Array": [0.03, 0.05, 0, 0, 0, 0],
        "Cranking load Array": [3.84, 0, 0, 0, 0, 0],
        "AGC Participation Factor": 0,
        "load Damping Constant": 0,
        "Effective Speed Droop": 0.05,
        "Bias Scaling": 1,
        "POPF": 0,       # MW governor reference (set if pre-scheduling P)
        "QOPF": -45.8050,
        "UseGenRampRate": False,
        "Load Enabled Response": False,
        "LERPF": -1,
        "Inertia Constant": 4.2880,
    },
    # Add more generators as needed
]

# -------------------------
# IBRs Configuration
# -------------------------
ibr_config = [
    {
        "IBR Name": "BESS5",
        "Bus Name": "Bus5",
        "Status": 0,  # 0: OFF, 1: Online
        "IBR Type": "BESS",  # e.g., BESS, Wind, Solar (extend if needed)
        "Ramp Rate": 0,  # Placeholder; currently rely on dynamic model
        "GFM Flag": True,  # True ⇒ operate in GFM mode (handled in .dyr)
        "Initial Capacity": 0.2,  # p.u. of MBASE
    }
]

# -------------------------
# Supervisor and safety logic
# -------------------------
# Debug print flag. True ⇒ emit [DEBUG] messages; False ⇒ quiet.
debug_print = True
# DebugPrintFlag = False  # (legacy name kept for reference)

# Flag to enforce action lock logic.
# True ⇒ no concurrent actions (sequential execution guaranteed).
# False ⇒ actions may overlap when time-aligned.
enforce_action_lock = False

# Execute tied actions with their parent action regardless of lock status.
# True ⇒ "tied" actions execute with the parent even if enforce_action_lock is True.
# False ⇒ tied actions follow normal scheduling/locking.
bypass_tied_actions = False

# Execute the control sequence exactly as listed (ignore action times).
# True ⇒ ignore timestamps; requires enforce_action_lock = True.
# False ⇒ schedule by action time (default behavior).
control_sequence_as_is = False

# Adjust action timings to compensate for execution delays (AGC settling,
# generator startup, etc.) while preserving intended gaps.
account_for_action_exec_delays = True

# Enforce frequency safety margins.
# True ⇒ hold next action until frequency is within [min, max].
# False ⇒ proceed regardless of frequency.
enforce_freq_safety_margin = True
# Bounds (Hz) if enforce_freq_safety_margin is True:
freq_safety_margin_min = 59.5
freq_safety_margin_max = 60.5

# If enforce_freq_safety_margin is True, BSPSSEPy waits for AGC to restore
# frequency to within limits before executing the next action. If False,
# scheduling ignores frequency bounds.

# Tie actions by their execution time. If actions are also tied by value fields,
# they will be grouped under the parent.
tie_actions_by_exec_time = True

# Delay after each action before AGC re-engages (seconds).
delay_agc_after_action = 30
```

---

### Step 3: PSSE Dynamic Conversion File Example

Save as `IEEE9_Ver1_Conv.py` (or without version number if only one case).

```python
# This file contains the PSSE conversion commands for the case.
# Conversion is required to prepare dynamic simulation models after solving power flow.

# Apply fixed-slope decoupled Newton-Raphson power flow calculation.
psspy.fdns([1, 0, 1, 1, 1, 0, 99, 0])

# Convert all generators for dynamic simulation.
psspy.cong(0)

# Initialize for load conversion, then convert loads to dynamic models.
# Mode 1: convert constant power loads.
psspy.conl(0, 1, 1, [0, 0], [0, 0, 0, 0])
# Mode 2: convert constant current loads.
psspy.conl(0, 1, 2, [0, 0], [0, 0, 0, 0])
# Mode 3: convert constant impedance loads.
psspy.conl(0, 1, 3, [0, 0], [0, 0, 0, 0])

# Postprocessing: order network elements for simulation.
psspy.ordr(0)  # Orders buses, branches, and components for numerical stability.
psspy.fact()   # Factorizes the admittance matrix for use in dynamic simulation.
psspy.tysl(0)  # Builds and stores the system solution matrix for time simulation.
psspy.tysl(0)  # Repeats to ensure full update after conversion.
```

---

### Step 4: BSPSSEPy CSV Plan

The CSV plan defines the chronological sequence of actions during the simulation.

**File name format:**

```
<case_name>_Ver<version>.csv
```

If only one version exists, omit `_Ver<version>`.

**Example:**

```
IEEE9_Ver1.csv
```

---

**Sample Content:**

| Device Type | Identification Type | Identification Value | Action Type | Action Time | Action Status | Values         |
| ----------- | ------------------- | -------------------- | ----------- | ----------- | ------------- | -------------- |
| TRN         | NAME                | TWTF1\_4             | ON          | 2           | 0             | {}             |
| LOAD        | NAME                | LOAD4B               | ON          | 2.016666667 | 0             | {}             |
| GEN         | NAME                | GEN1                 | UPDATE      | 2.033333333 | 0             | {'P': 8}       |
| LOAD        | NAME                | LOAD4A               | ON          | 4           | 0             | {}             |
| GEN         | NAME                | GEN1                 | UPDATE      | 4.016666667 | 0             | {'P': 13}      |
| BRN         | NAME                | BRN4\_5              | ON          | 6           | 0             | {}             |
| LOAD        | NAME                | LOAD5D               | ON          | 6.016666667 | 0             | {}             |
| BESS        | NAME                | BESS5                | ON          | 6.033333333 | 0             | {}             |
| GEN         | NAME                | GEN1                 | UPDATE      | 6.05        | 0             | {'P': 20.9372} |
| BESS        | NAME                | BESS5                | UPDATE      | 6.066666667 | 0             | {'P': 5.0628}  |
| GEN         | NAME                | GEN1                 | UPDATE      | 8           | 0             | {'P': 30.2399} |
| BESS        | NAME                | BESS5                | UPDATE      | 8.05        | 0             | {'P': -4.2399} |

---

**Column Descriptions:**

* **Device Type:** TRN (Transformer), LOAD, GEN, BRN (Branch), BESS.
* **Identification Type:** Typically `NAME`, but can be other identifier types
  supported by BSPSSEPy (Refer to Code Help documentation).
* **Identification Value:** Exact device name following the naming scheme.
* **Action Type:** Operation to perform (ON, OFF, UPDATE, etc.).
* **Action Time:** Time in minutes from simulation start to perform the action.
* **Action Status:** Reserved for runtime flags or internal state tracking
  (keep it 0 for Black-Start Simulations).
* **Values:** Dictionary of parameters to change (e.g., `{'P': 8}` to set generator active power to 8 MW).
