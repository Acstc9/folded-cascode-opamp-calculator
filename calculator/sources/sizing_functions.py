from math import ceil, log10, pi, radians, tan

from .retrieve_device_data import retrieve_current_per_width, select_fold_branch_point


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


def calculate_stage2_required_resistances(gain_db, m12_gm_us, m12_ro_kohm):
    output_kohm = 1000 * 10 ** (gain_db / 20) / m12_gm_us
    if m12_ro_kohm <= output_kohm:
        raise ValueError("M12 cannot reach the gain target with a finite M13 output resistance.")
    m13_ro_kohm = 1 / (1 / output_kohm - 1 / m12_ro_kohm)
    return output_kohm, m13_ro_kohm


def size_folded_stage_pairs(target_gain_db, effective_gm_us, fold_current_ua, m2_ro_ohm, m4_ro_ohm):
    fold_source_ohm = 1 / (1 / m2_ro_ohm + 1 / m4_ro_ohm)
    gain_db = None
    for length_um in (1, 2):
        m6 = select_fold_branch_point("pmos", length_um, fold_current_ua)
        m10 = select_fold_branch_point("nmos", length_um, fold_current_ua)
        if m6 is None or m10 is None:
            continue
        upper_ohm = float(m6["gm_s"]) * float(m6["ro_ohm"]) * fold_source_ohm
        # M8 and M10 have the same size and current in the single-device table.
        m8_ro_ohm = float(m10["ro_ohm"])
        lower_ohm = float(m10["gm_s"]) * float(m10["ro_ohm"]) * m8_ro_ohm
        output_ohm = 1 / (1 / upper_ohm + 1 / lower_ohm)
        gain_db = 20 * log10(effective_gm_us * 1e-6 * output_ohm)
        if gain_db >= target_gain_db:
            fold_width_um = float(m6["width_m"]) * 1e6
            nmos_width_um = float(m10["width_m"]) * 1e6
            return length_um, fold_width_um, nmos_width_um, output_ohm, gain_db
    if gain_db is None:
        raise ValueError("Neither length has saturated NMOS and PMOS data at the fold current.")
    raise ValueError(f"Neither length meets {target_gain_db:g} dB. Last available estimate: {gain_db:.2f} dB.")
