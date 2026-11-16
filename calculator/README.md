# How the first pass is sized

## Amplifier core

**1. Turn the specifications into currents and transconductances.** The [default configuration](config.py) uses $`C_c=0.5`$ pF, $`C_L=1`$ pF, a 20 MHz unity-gain design target, 45° phase margin and 20 V/µs on each edge. During a slew, assume $`V_X`$ moves slowly compared with the output. The tail must steer enough current to charge or discharge $`C_c`$. On a rising edge M13 must also charge $`C_L`$.

```math
I_{11}^{\ast}=C_c\max(S_\uparrow,S_\downarrow)=10\,\mu\mathrm{A},
\qquad I_{13}^{\ast}=(C_L+C_c)S_\uparrow=30\,\mu\mathrm{A}.
```

At balanced inputs, each input device gets half the design tail current (5 µA). Allowing one fold branch to reach zero at full steering gives a quiescent fold current of 5 µA per side. M3 and M4 must each supply the sum, 10 µA. The bandwidth sets the first-stage transconductance target. The two-pole phase approximation sets the target for M12.

```math
G_{m1}^{\ast}=2\pi f_u C_c=62.83\,\mu\mathrm{S},
\qquad g_{m12}^{\ast}=2\pi f_u C_L\tan(\mathrm{PM})=125.66\,\mu\mathrm{S}.
```

The star marks a design target. $`G_{m1}`$ is the effective transconductance of the whole first stage. $`g_{m12}`$ belongs to one transistor. The initial Miller nulling resistor is $`1/g_{m12}^{\ast}=7.96`$ kΩ.

**2. Select M12, then use its operating point to size the PMOS load.** M12 carries the second-stage DC current. Look near 30 µA in each saturated NMOS sweep, trying the shortest length first and then the smallest width. **M12 = 2/1** ($`W/L`$ in µm throughout) meets the transconductance target. Its row gives $`g_m=188.45`$ µS, $`r_o=1.047`$ MΩ and $`V_X=V_{GS12}=0.75`$ V.

For 23 dB of second-stage gain, $`g_{m12}(r_{o12}\parallel r_{o13})`$ must reach $`10^{23/20}`$. With M12 chosen, M13 needs at least 80.74 kΩ. M13 shares its gate and source with M3/M4, so select the three at **one** $`V_{SG}`$. At 0.88 V, **M3/M4 = 2/1 each** supply 10.31 µA each, and **M13 = 6/1** supplies 32.13 µA with 921 kΩ. The 3:1 width ratio follows from this example's branch currents. Changing the load changes the required output current.

**3. Select M1/M2 before M11.** At a design current of 5 µA, each input needs approximately 62.83 µS with the 1:1 signal mirror. The measured $`g_m/I_D`$ curve gives a current per unit width. Divide 5 µA by that density, round up to an even width, then check both current and $`g_m`$ in saturation. **M1/M2 = 2/1 each** qualify at the configured 1 µm length. The selected sample gives $`V_{GS1}=0.57`$ V.

At 0.90 V input common mode, this leaves $`0.90-0.57=0.33`$ V across M11. Its gate voltage is already set by the 10 µA reference through MB12. Use the **drain sweep at that gate bias** to select M11. At 0.33 V, 4/2 gives 9.88 µA, below the 10 µA floor. **M11 = 4/1** gives 16.49 µA in saturation. Subsequent mirror calculations keep the original branch targets. The complete circuit establishes the actual current split.

**4. Choose the lengths of M5–M10 from the gain at $`V_X`$.** M5/M6 carry the fold currents and serve as PMOS cascodes. M7/M8 mirror the current. M9/M10 are the NMOS cascodes. Both cascode pairs must stay saturated while leaving room for $`V_X`$ to swing. Looking into $`V_X`$, the upper and lower branches appear in parallel.

```math
R_\mathrm{up}\approx g_{m6}r_{o6}(r_{o2}\parallel r_{o4}),\qquad
R_\mathrm{down}\approx g_{m10}r_{o10}r_{o8},\qquad
|A_1|\approx G_{m1}(R_\mathrm{up}\parallel R_\mathrm{down}).
```

Start all three pairs at **2/1 each**. The lookup estimate is 223 MΩ and 82.94 dB, already above the 40 dB first-stage target. Only if that first size cannot meet the current or gain requirement does the calculator try the three pairs at 2 µm length. MB16 and MB19 then follow their corresponding core devices.

## Bias network

| Branch | What sets its dimensions in this example |
| --- | --- |
| **MB12** | The given **4/2** NMOS carries the external 10 µA and sets the gate bias used by M11, MB13 and MB14. |
| **MB13 → MB15** | MB13 must sink the M3 branch target of 10 µA. It copies MB12 at **4/2**. The diode-connected MB15 copies M3 at **2/1** to generate the shared PMOS current-source bias. |
| **MB14 → MB16, MB17** | MB14 sinks the 5 µA fold target, so it takes half of MB12's width at the same length, **2/2**. MB16 copies M5 at **2/1**. MB17 starts at **2/6**. Its voltage drop sets the replica source voltage used to bias M5/M6. Check M3/M4 headroom in DC. |
| **MB18 → MB19, MB20** | MB18 sources 10 µA, the same target as MB15, so both use **2/1**. MB19 carries twice M9's design current and uses twice its width, **4/1**, to match current density. MB20 starts at **2/6**. Its voltage drop sets the replica source voltage used to bias M9/M10. Check M7/M8 headroom in DC. |

MB17 and MB20 are trial dimensions for triode operation. The other selections use measured saturation samples where indicated. The gate sweeps use fixed drain and body biases. Folded and cascode devices see different voltages once connected. The sweep conditions are in the [device data README](sources/data/README.md).

The implementation follows this sequence in [run_calculator.py](run_calculator.py). The first-pass gain and pole approximations follow J. R. Hellums, *Amplifier Sizing Analysis*, pp. 2–3 and 15–20.
