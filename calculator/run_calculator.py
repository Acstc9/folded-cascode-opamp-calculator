from math import ceil

from config import config
from sources import sizing_functions

# %% Stage requirements

#
# SR: Tail and second-stage bias currents
#
tail_current_ua, second_stage_current_ua = sizing_functions.calculate_bias_currents_for_slew(config)

#
# GBW: First-stage effective transconductance
#
stage1_effective_gm_us = sizing_functions.calculate_stage1_effective_gm(config)

#
# PM: M12 transconductance
#
m12_gm_us = sizing_functions.calculate_m12_gm_for_phase_margin(config)

#
# Miller nulling resistor from the M12 transconductance target
#
nulling_resistance_kohm = 1000 / m12_gm_us

#
# First-stage quiescent branch currents
#
input_current_ua, fold_current_ua, branch_source_current_ua = sizing_functions.calculate_stage1_branch_currents(
    tail_current_ua
)

# %% Transistor sizing

#
# Shared width for M1 and M2
#
input_pair_width_um = sizing_functions.calculate_mos_width(
    "nmos", stage1_effective_gm_us, input_current_ua, config.starting_lengths_um["M1"]
)

#
# Second-stage NMOS width
#
m12_width_um = sizing_functions.calculate_mos_width(
    "nmos", m12_gm_us, second_stage_current_ua, config.starting_lengths_um["M12"]
)

#
# Shared width for M3 and M4
#
m3_m4_width_um = sizing_functions.calculate_mos_width_from_overdrive(
    "pmos", config.m3_m4_target_overdrive_v, branch_source_current_ua, config.starting_lengths_um["M3"]
)

#
# Second-stage PMOS load width
#
m13_width_um = m3_m4_width_um * second_stage_current_ua / branch_source_current_ua

#
# M11 tail-source width from the MB12 reference
#
m11_width_to_length = (config.mb12_width_um / config.starting_lengths_um["MB12"]) * (
    tail_current_ua / config.reference_current_ua
)
m11_width_um = 2 * ceil(m11_width_to_length * config.starting_lengths_um["M11"] / 2)

# Try W = 2 µm and L = 1 µm for M5 and M6. Check that both are saturated at the amplifier's DC operating point.
# Start M7 and M8 at W = L = 6 µm. Check saturation at the target DC current of 5 µA per device.
# Try W = 2 µm and L = 1 µm for M9 and M10. Aim for a low VDS requirement for saturation at 5 µA each.
