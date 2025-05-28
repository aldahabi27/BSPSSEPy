from .sim.bspssepy_gen_funs import GenEnable, GenDisable, GenUpdate
from .sim.bspssepy_brn_funs import BrnClose, BrnTrip
from .sim.bspssepy_load_funs import LoadEnable, LoadDisable
from .sim.bspssepy_trn_funs import TrnClose, TrnTrip
from .sim.bspssepy_bus_funs import BusClose, BusTrip

# This maps the actions on elements to their corresponding functions
ElementTypeFunctionMapping = {
    "GEN":        {"on":GenEnable,    "off":GenDisable,    "update": GenUpdate},
    "TRN":        {"on":TrnClose,     "off":TrnTrip},
    "BRN":        {"on":BrnClose,     "off":BrnTrip},
    "LOAD":       {"on":LoadEnable,   "off":LoadDisable},
    "BUS":        {"on":BusClose,     "off":BusTrip}
}


