from math import atan, degrees, log10, pi

from config import config
from sources import retrieve_device_data, sizing_functions

# %% Amplifier Core Sizing

#
# SR: Tail and second-stage bias currents
#
tail_current_ua, second_stage_current_ua = sizing_functions.calculate_bias_currents_for_slew(config)

#
# Set the input, fold and M3/M4 branch currents from the design tail current
#
input_current_ua, fold_current_ua, branch_source_current_ua = sizing_functions.calculate_stage1_branch_currents(
    tail_current_ua
)

#
# First-stage effective transconductance at the target unity-gain frequency
#
stage1_effective_gm_us = sizing_functions.calculate_stage1_effective_gm(config)

#
# PM: M12 transconductance
#
m12_target_gm_us = sizing_functions.calculate_m12_gm_for_phase_margin(config)

#
# Miller nulling resistor from the M12 transconductance target
#
nulling_resistance_kohm = 1000 / m12_target_gm_us

#
# Select M12 and keep its gate voltage as the quiescent VX target (source at 0 V)
#
m12_width_um, m12_length_um, m12_point = retrieve_device_data.select_nmos_by_gm(
    second_stage_current_ua, m12_target_gm_us
)
m12_gm_us = float(m12_point["gm_s"]) * 1e6
vx_quiescent_v = float(m12_point["vgs_v"])

#
# M13 output resistance required by the second-stage gain target
#
m12_ro_kohm = float(m12_point["ro_ohm"]) / 1000
stage2_required_resistance_kohm, m13_required_ro_kohm = sizing_functions.calculate_stage2_required_resistances(
    config.stage2_gain_target_db, m12_gm_us, m12_ro_kohm
)

#
# Size M3/M4 and M13 at one gate bias for their respective branch currents
#
m3_m4_width_um, m13_width_um, m3_m4_point, m13_point = retrieve_device_data.select_pmos_mirror(
    branch_source_current_ua, second_stage_current_ua, config.pmos_mirror_length_um, m13_required_ro_kohm
)
m13_ro_kohm = float(m13_point["ro_ohm"]) / 1000
pmos_mirror_vsg_v = -float(m13_point["vgs_v"])
vbias_current_source_v = config.vdd_v - pmos_mirror_vsg_v

#
# Estimate second-stage DC gain from the selected devices
#
stage2_output_resistance_kohm = 1 / (1 / m12_ro_kohm + 1 / m13_ro_kohm)
stage2_gain_db = 20 * log10(m12_gm_us * stage2_output_resistance_kohm / 1000)

#
# Size M1 and M2 from gm/ID and require both current and gm at the selected point
#
input_pair_starting_width_um = sizing_functions.calculate_mos_width(
    "nmos", stage1_effective_gm_us, input_current_ua, config.input_pair_length_um
)
input_pair_width_um, input_pair_length_um, input_pair_point = retrieve_device_data.select_nmos_by_gm(
    input_current_ua, stage1_effective_gm_us, config.input_pair_length_um, input_pair_starting_width_um,
    current_floor=True,
)
input_vgs_at_target_v = float(input_pair_point["vgs_v"])

#
# Select the smallest saturated M11 that meets the tail-current floor at the MB12 gate bias
#
m11_available_vds_v = config.nominal_input_common_mode_v - input_vgs_at_target_v
m11_width_um, m11_length_um, m11_point = retrieve_device_data.select_m11_size(
    config, tail_current_ua, m11_available_vds_v
)
m11_current_at_design_vds_ua = float(m11_point["id_a"]) * 1e6
m11_vds_v = float(m11_point["vds_v"])
m11_saturation_margin_v = m11_vds_v - float(m11_point["vdsat_v"])

#
# Estimate input-pair performance at its selected operating point
#
input_pair_gm_us = float(input_pair_point["gm_s"]) * 1e6
input_pair_gm_over_id = input_pair_gm_us / (float(input_pair_point["id_a"]) * 1e6)
input_pair_overdrive_v = input_vgs_at_target_v - float(input_pair_point["vth_v"])
stage1_estimated_unity_gain_mhz = input_pair_gm_us / (2 * pi * config.compensation_pf)
estimated_phase_margin_deg = degrees(atan(m12_gm_us / (2 * pi * stage1_estimated_unity_gain_mhz * config.load_pf)))

#
# Size M5–M10 for first-stage gain, starting at 2/1 µm
#
(
    folded_stage_length_um, m5_m6_width_um, m9_m10_width_um,
    stage1_output_resistance_ohm, stage1_gain_db,
) = sizing_functions.size_folded_stage_pairs(
    config.stage1_gain_target_db, stage1_effective_gm_us, fold_current_ua,
    float(input_pair_point["ro_ohm"]), float(m3_m4_point["ro_ohm"]),
)
m7_m8_width_um = m9_m10_width_um

# %% Bias Network Sizing

# Use design branch currents here. M11's measured current only checks its sizing floor.

#
# Scale MB13 and MB14 from MB12 to sink the target currents through MB15 and MB16
#
mb13_target_width_um = config.mb12_width_um * branch_source_current_ua / config.reference_current_ua
mb14_target_width_um = config.mb12_width_um * fold_current_ua / config.reference_current_ua

#
# Copy M3/M4 into MB15 and M5/M6 into MB16 at equal design currents
#
mb15_width_um = m3_m4_width_um
mb16_width_um, mb16_length_um = m5_m6_width_um, folded_stage_length_um

#
# Use one reference current through MB18 and MB19. Match MB19's current per width to M9/M10.
#
mb18_target_width_um = mb15_width_um * config.reference_current_ua / branch_source_current_ua
mb19_length_um = folded_stage_length_um
mb19_target_width_um = m9_m10_width_um * config.reference_current_ua / fold_current_ua
