"""_summary_"""

from .sim.bspssepy_gen_funs import gen_enable, gen_disable, gen_update
from .sim.bspssepy_brn_funs import brn_close, brn_trip
from .sim.bspssepy_load_funs import load_enable, load_disable
from .sim.bspssepy_trn_funs import trn_close, trn_trip
from .sim.bspssepy_bus_funs import bus_close, bus_trip
from .sim.bspssepy_ibr_funs import ibr_disable, ibr_enable, ibr_update

# This maps the actions on elements to their corresponding functions
element_type_fun_map = {
    "GEN": {"on": gen_enable, "off": gen_disable, "update": gen_update},
    "TRN": {"on": trn_close, "off": trn_trip},
    "BRN": {"on": brn_close, "off": brn_trip},
    "LOAD": {"on": load_enable, "off": load_disable},
    "BUS": {"on": bus_close, "off": bus_trip},
    "IBR": {"on": ibr_enable, "off": ibr_disable, "update": ibr_update},
}
