class Config:
    def __init__(self):
        self.load_pf = 1
        self.compensation_pf = 0.5
        self.rise_slew_rate_v_per_us = 20
        self.fall_slew_rate_v_per_us = 20
        self.unity_gain_mhz = 20
        self.phase_margin_deg = 45

        self.m3_m4_target_overdrive_v = 0.30
        self.reference_current_ua = 10
        self.mb12_width_um = 4
        self.starting_lengths_um = {}
        for length_um, devices in (
            (1, ("M1", "M2", "M5", "M6", "M9", "M10", "M12", "MB16", "MB19")),
            (2, ("MB12", "MB13", "MB14")),
            (6, ("M3", "M4", "M7", "M8", "M11", "M13", "MB15", "MB17", "MB18", "MB20")),
        ):
            for device in devices:
                self.starting_lengths_um[device] = length_um


config = Config()
