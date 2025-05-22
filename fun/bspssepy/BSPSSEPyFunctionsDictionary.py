from .Sim.BSPSSEPyGenFunctions import GenEnable, GenDisable, GenUpdate
from .Sim.BSPSSEPyBrnFunctions import BrnClose, BrnTrip
from .Sim.BSPSSEPyLoadFunctions import LoadEnable, LoadDisable
from .Sim.BSPSSEPyTrnFunctions import TrnClose, TrnTrip
from .Sim.BSPSSEPyBusFunctions import BusClose, BusTrip

# This maps the actions on elements to their corresponding functions
ElementTypeFunctionMapping = {
    "GEN":        {"on":GenEnable,    "off":GenDisable,    "update": GenUpdate},
    "TRN":        {"on":TrnClose,     "off":TrnTrip},
    "BRN":        {"on":BrnClose,     "off":BrnTrip},
    "LOAD":       {"on":LoadEnable,   "off":LoadDisable},
    "BUS":        {"on":BusClose,     "off":BusTrip}
}


