class Config:
    def __init__(self):
        self.vdd_v = 1.8
        self.nominal_input_common_mode_v = 0.9
        self.load_pf = 1
        self.compensation_pf = 0.5
        self.rise_slew_rate_v_per_us = 20
        self.fall_slew_rate_v_per_us = 20
        self.unity_gain_mhz = 20
        self.phase_margin_deg = 45
        self.stage1_gain_target_db = 40
        self.stage2_gain_target_db = 23

        self.input_pair_length_um = 1
        self.pmos_mirror_length_um = 1  # M3, M4, M13, MB15 and MB18
        self.reference_current_ua = 10
        self.mb12_width_um = 4
        self.reference_mirror_length_um = 2  # MB12, MB13 and MB14
        # In full-circuit DC, tune MB17 for M3/M4 drain headroom and MB20 for M7/M8 drain headroom.
        self.mb17_trial_width_um = 2
        self.mb20_trial_width_um = 2
        self.triode_bias_length_um = 6  # MB17 and MB20


config = Config()
