# MOS operating-point sweeps

`nmos.csv` and `pmos.csv` contain Spectre DC measurements of the TSMC 180 nm `nmos2v` and `pmos2v` devices at the TT corner and 27 °C. Both files cover W/L sizes of **2/1, 4/1, 2/2 and 4/2 µm**. The PMOS file also includes **6/1 and 10/1 µm** for the shared-bias current mirror. Each device has one finger and a multiplier of one.

| Gate sweep | NMOS | PMOS |
| --- | --- | --- |
| Source and body voltage | 0 V | 1.8 V |
| Fixed VDS | +0.9 V | −0.9 V |
| Fixed VBS | 0 V | 0 V |
| Swept VGS | 0 to +1.2 V | 0 to −1.2 V |

The gate sweep has 121 points per size at 10 mV intervals. The NMOS file also contains an M11 drain sweep for each size: VDS runs from 0 to 1.8 V in 10 mV steps at VBS = 0 V. A diode-connected 4/2 µm NMOS carrying 10 µA sets VGS to approximately 0.59956 V.

| Columns | Meaning |
| --- | --- |
| `width_m`, `length_m` | Total channel width and drawn length (m) |
| `vgs_v`, `vds_v`, `vbs_v` | Signed gate, drain and body voltages relative to the source (V) |
| `id_a`, `gm_s`, `gds_s` | Drain-current magnitude (A), transconductance and output conductance (S) |
| `ro_ohm` | Small-signal output resistance, 1/gds (Ω) |
| `vth_v`, `vdsat_v` | Signed model threshold and saturation voltages (V) |
| `region` | Spectre BSIM3v3 operating-region code: 0 = off, 1 = triode, 2 = saturation, 3 = subthreshold, 4 = breakdown |
| `ref_width_um`, `ref_length_um`, `ref_current_ua` | Reference-device W, L (µm) and current (µA). Populated only for the NMOS drain sweep. |

Each region code describes the device at the voltages in that row. The calculator uses code 2 for sizing steps that require saturation.
