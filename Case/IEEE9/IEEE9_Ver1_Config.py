# Config.py
#
#
# Use this template to set the configuration for your PSSE case. The specs below are arbitrary.
#
#    Last Update for this file was on BSPSSEPy Ver 0.2 (13 Dec. 2024)
#
#       BSPSSEPy Application
#       Copyright (c) 2024, Ilyas Farhat
#       by Ilyas Farhat
#    
#       This file is part of BSPSSEPy Application
#       Contact the developer at ilyas.farhat@outlook.com
#
#
#


#┎┈┈┈┈┈┈┈┈┈┈┈┈┈┈୨♡୧┈┈┈┈┈┈┈┈┈┈┈┈┈┈┒
#    𝑼𝒔𝒆𝒓 𝑪𝒐𝒏𝒇𝒊𝒈𝒖𝒓𝒂𝒕𝒊𝒐𝒏𝒔 𝑺𝒕𝒂𝒓𝒕
#┖┈┈┈┈┈┈┈┈┈┈┈┈┈┈୨♡୧┈┈┈┈┈┈┈┈┈┈┈┈┈┈┚

# Should match the name of the case folder exactly.
CaseName = "IEEE9"

# Version number from the .sav file name (e.g., 3Bus_Ver2.sav). Use -1 if no version is specified.
Ver = 1

# Number of buses in the system. If unsure, leave as 0, and the code will derive this automatically from the case data.
NumberOfBuses = 50

# Specify buses to monitor voltage as a list of bus numbers. 
# Use 'Range(start, end)' syntax to indicate a range of buses. 
# Flag 'VoltageFlag' may override this setting.
BusesToMonitor_Voltage = range(1,10)

# Specify buses to monitor frequency as a list of bus numbers. 
# Flag 'FrequencyFlag' may override this setting.
BusesToMonitor_Frequency = [1,2,3]

# Flag for voltage monitoring behavior: 
# 0 = use specified buses, 1 = all generator buses, 
# 2 = all transformer buses, 3 = gen+TF buses, 
# 4 = all load buses, 5 = all buses.
VoltageFlag = 0

# Flag for frequency monitoring behavior: 
# 0 = use specified buses, 1 = all generator buses, 
# 2 = all transformer buses, 3 = gen+TF buses, 
# 4 = all load buses, 5 = all buses.
FrequencyFlag = 0

# Time step for the simulation in seconds. Default is 1ms (0.001).
SimulationTimeStep = 1e-3 #seconds

# Frequency filtering threshold for simulation in seconds. Default is 4 times the SimulationTimeStep.
Simulationfreqfilter = 4 * SimulationTimeStep

# Maximum iterations allowed for PSSE Newton-Raphson solver. Default is 100.
PSSEMaxIterationNewtonRaphson = 100

# If true, forces regeneration of the CNV file regardless of its existence.
IgnoreCNVFile = True

# If true, forces regeneration of the SNP file regardless of its existence.
IgnoreSNPFile = True

# BSPSSEPy Hard Time Limit in minutes (ignored if BSPSSEPyHardTimeLimitFlag is False)
BSPSSEPyHardTimeLimit = 30 #minutes

# If true, BSPSSEPy will enforce a hard time limit on the simulation.
BSPSSEPyHardTimeLimitFlag = True

# BSPSSEPy Time Step in seconds
# This timestep controls the python functions execution rate.
# This controls AGC, control actions, and other time-dependent functions.
# Default is 1 second.
# Note: This is different from the simulation time step specified for dynamic modeling in PSSE.
BSPSSEPyTimeStep = 1 #seconds


# BSPSSEPyProgressPrintTime controls the frequency of progress print messages in minutes.
BSPSSEPyProgressPrintTime = 1 #minutes


# Table of Generators Configuration
# Each generator should have:
# - Generator Name: The unique name of the generator
# - Bus Name: Name of the associated bus
# - Status: Initial status of the generator ("OFF", "Cranking", etc.)
# - Load Name: Name of the corresponding cranking load (if any)
# - Cranking Time: Duration of the cranking phase
# - Ramp Rate: Ramp-up rate
# - Generator Type: "NBS" (Non-Black-Start) or "BS" (Black-Start)
# - Cranking Load Array: Power array [PL, QL, IP, IQ, YP, YQ, Power Factor] - Reminder: All powers are in MW, MVAR
#
# For BS generators, only Generator Name, Bus Name, Status, and Generator Type are required. The rest are ignored.
# For NBS generators, all fields are required to model all phases correctly!

GeneratorsConfig = [
    {
        "Generator Name": "GEN1",
        "Bus Name": "Bus1",
        "Status": 3,         # If the generator is BS, then this will be overwritten and set to 3 (# 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active)
        "Load Name": "CLGEN1",
        "Cranking Time": 10.0,  # minutes
        "Ramp Rate": 5.0,   # MW/min
        "Generator Type": "BS",         # BS or NBS
        "Cranking Load Array": [0, 0, 0, 0, 0, 0], # Because it is BS generator, it won't have any asscoiated cranking load
        "AGC Participation Factor": 1,#1/3,
        "Load Damping Constant": 0,  # D
        "Effective Speed Droop": 0.05,  # R
        "Bias Scaling": 1,  # Bias Scaling (Effective Bias = Bias * Bias Scaling)
        "POPF": 71.911827,  # POPF - Governer Reference (Controls P Gen) - Regular Units - MW
        "QOPF": 24.074171,  # QOPF - Voltage Reference (Controls Q Gen) - Regular Units - MVAR
        "UseGenRampRate": True,  # If True, the generator will use the ramp rate specified in the config file. If Faluse, the generator will use the ramp rate specified in the dynamic model (if any).
    },
    {
        "Generator Name": "GEN2",
        "Bus Name": "Bus2",
        "Status": 0,    # If the generator is BS, then this will be overwritten and set to 3 (# 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active)
        "Load Name": "CLGEN2",
        "Cranking Time": 2.5,   # minutes
        "Ramp Rate": 6,   # MW/min
        "Generator Type": "NBS",         # BS or NBS
        # "Cranking Load Array": [0.05, 0.02, 0, 0, 0, 0],
        "Cranking Load Array": [5, 2, 0, 0, 0, 0],
        "AGC Participation Factor": 0,#1/3,
        "Load Damping Constant": 0,  # D
        "Effective Speed Droop": 0.05,  # R
        "Bias Scaling": 1,  # Bias Scaling (Effective Bias = Bias * Bias Scaling)
        "POPF": 163.029465,  # POPF - Governer Reference (Controls P Gen) - Regular Units - MW
        "QOPF": 14.466742,  # QOPF - Voltage Reference (Controls Q Gen) - Regular Units - MVAR
        "UseGenRampRate": True,  # If True, the generator will use the ramp rate specified in the config file. If Faluse, the generator will use the ramp rate specified in the dynamic model (if any).
    },
    {
        "Generator Name": "GEN3",
        "Bus Name": "Bus3",
        "Status": 0,    # If the generator is BS, then this will be overwritten and set to 3 (# 0: OFF, 1: Cranking, 2: Ramp-up, 3: Ready/active)
        "Load Name": "CLGEN3",
        "Cranking Time": 4,   # minutes
        "Ramp Rate": 3,       # MW/min
        "Generator Type": "NBS",         # BS or NBS
        # "Cranking Load Array": [0.03, 0.05, 0, 0, 0, 0],
        "Cranking Load Array": [2, 1.5, 0, 0, 0, 0],
        "AGC Participation Factor": 0,#1/3,
        "Load Damping Constant": 0,  # D
        "Effective Speed Droop": 0.05,  # R
        "Bias Scaling": 1,  # Bias Scaling (Effective Bias = Bias * Bias Scaling)
        "POPF": 85.015396,  # POPF - Governer Reference (Controls P Gen) - Regular Units - MW
        "QOPF": -3.646511,  # QOPF - Voltage Reference (Controls Q Gen) - Regular Units - MVAR
        "UseGenRampRate": False,  # If True, the generator will use the ramp rate specified in the config file. If Faluse, the generator will use the ramp rate specified in the dynamic model (if any).
    }
    # Add more generators as needed
]


# Debug print flag. If true, prints debug messages.
DebugPrintFlag = True
# DebugPrintFlag = False


EnforceActionLock = True  # Flag to enforce checking the action lock logic. True => ensuring no concurrent actions are allowed.
# EnforceActionLock = False
                          # EnforceActionLock = False  # Flag to enforce checking the action lock logic. True => ensuring no concurrent actions are allowed.

ControlSequenceAsIs = True  # If True, the control sequence is executed as is without looking at action time.
# ControlSequenceAsIs = False
                             # To set this to True, EnforceActionLock must be True (to excute actions sequentially).
                             # If True and EnforceActionLock is False, program will throw an error and exits.
                             # If False, the program will execute the control sequence based on the action time.

EnforceFrequencySafetyMargin = True  # If True, the program will enforce a safety margin on the frequency to avoid
                                     # the frequency to go below FreqSafetyMarginMin or above FreqSafetyMarginMax. 
FreqSafetyMarginMin = 60  # Minimum frequency allowed in Hz
FreqSafetyMarginMax = 60.5  # Maximum frequency allowed in Hz

# Note: If EnforceFrequencySafetyMargin is True, the system will wait until "AGC" regulate the frequency to be within limits before executing the next action.
#       If EnforceFrequencySafetyMargin is False, the system will execute the next action regardless of the frequency.


#┎┈┈┈┈┈┈┈┈┈┈┈┈┈┈୨♡୧┈┈┈┈┈┈┈┈┈┈┈┈┈┈┒
#     𝑼𝒔𝒆𝒓 𝑪𝒐𝒏𝒇𝒊𝒈𝒖𝒓𝒂𝒕𝒊𝒐𝒏𝒔 𝑬𝒏𝒅
#┖┈┈┈┈┈┈┈┈┈┈┈┈┈┈୨♡୧┈┈┈┈┈┈┈┈┈┈┈┈┈┈┚
