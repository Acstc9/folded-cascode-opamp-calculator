from math import ceil, pi, radians, tan

from .retrieve_device_data import retrieve_current_per_width


def calculate_bias_currents_for_slew(config):
    tail_current_ua = config.compensation_pf * max(
        config.rise_slew_rate_v_per_us, config.fall_slew_rate_v_per_us
    )
    second_stage_current_ua = (config.load_pf + config.compensation_pf) * config.rise_slew_rate_v_per_us
    return tail_current_ua, second_stage_current_ua


def calculate_stage1_effective_gm(config):
    return 2 * pi * config.unity_gain_mhz * config.compensation_pf


def calculate_m12_gm_for_phase_margin(config):
    return 2 * pi * config.unity_gain_mhz * config.load_pf * tan(radians(config.phase_margin_deg))


def calculate_stage1_branch_currents(tail_current_ua):
    input_current_ua = tail_current_ua / 2
    fold_current_ua = input_current_ua
    branch_source_current_ua = input_current_ua + fold_current_ua
    return input_current_ua, fold_current_ua, branch_source_current_ua


def calculate_mos_width(device_type, gm_us, drain_current_ua, length_um):
    gm_over_id = gm_us / drain_current_ua
    current_per_width = retrieve_current_per_width(device_type, gm_over_id, length_um)
    width_um = drain_current_ua / current_per_width
    return 2 * ceil(width_um / 2)


def calculate_mos_width_from_overdrive(device_type, overdrive_v, drain_current_ua, length_um):
    gm_us = 2 * drain_current_ua / overdrive_v
    return calculate_mos_width(device_type, gm_us, drain_current_ua, length_um)
