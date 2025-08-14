## app folder
Contains GUI related functions that help updates the tables, and assign
`worker` to run BSPSSEPy Engine.

## config folder
Contains the code responsible for reading BSPSSEPy configuration python files
and plan csv data. The code will parse the information and prepare all
variables for BSPSSEPy simulation following the configuration parameters.

## plot folder
Contains the code for plotting the results at the end of the simulation. These
functions are projected to be refined and made more rich for better data
visualization from within BSPSSEPy, but for now, a two simple plots are
presented whenever the simulation `finishes successfully`. If data are to be
plotted with incomplete simulation, use `MATLAB Code` to plot it (or view
within PSSE -- check the manual)

## psse folder
Contains the code for setting up the link between BSPSSEPy and PSSE to run the
simulation. It configure PSSE for dynamic simulation following the settings in
the Config file.

## sim folder
Contains the BSPSSEPy simulation engine. The actual code that run the
dynamic simulation. This code is setup to be called by the GUI (for realtime
monitoring) or through the terminal using `bspssepy_terminal.py`.

## bspssepy main folder python code

* `bspssepy_core.py`: main python class that will run the simulation and save
  data. It can be called by other python codes to setup the GUI or without
  GUI.
  
* `bspssepy_dict.py`: python code that contains dictionaries for various
  entries such as:
  * device type mapping (various entries that map to device types - i.e. `1`,
    `g`, `gen`, `generator` all maps to `GEN` type element)
  * action types (ON, OFF...etc.)
  * various variable names mapping to element actions
  * PSSE list of `callable` entries for each type of devices (used to check if
    the entry is available in PSSE and used as a quick reference for BSPSSEPy
    development).
    
* `bspssepy_funs_dict.py`: an element vs function mapping dictionary

* `meta.py`: Contains general meta data (date, version number...etc.) for
  BSPSSEPy GUI information.