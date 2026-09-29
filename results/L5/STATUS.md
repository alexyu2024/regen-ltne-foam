# L5 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L5.1 cycles_run | >= 40 (docs/VERIFICATION.md:286) | 40 | PASS | results/L5/per_cycle.csv:2-41 |
| L5.2 crash_count | == 0 (docs/VERIFICATION.md:287) | 0 | PASS | results/L5/log.*:all lines of all logs (base and sens); 11 trapFpe banner lines skipped |
| L5.3 piston_hot_amp_err | <= 0.005 (docs/VERIFICATION.md:288) | 7.758558149273398e-07 | PASS | results/L5/piston_check.csv:2 |
| L5.4 piston_hot_phase_err_deg | <= 0.5 (docs/VERIFICATION.md:289) | 0.07499999986492867 | PASS | results/L5/piston_check.csv:2 |
| L5.5 piston_cold_amp_err | <= 0.005 (docs/VERIFICATION.md:290) | 1.2592335406624855e-06 | PASS | results/L5/piston_check.csv:3 |
| L5.6 piston_cold_phase_err_deg | <= 0.5 (docs/VERIFICATION.md:291) | 0.07500000013982344 | PASS | results/L5/piston_check.csv:3 |
| L5.7 B5_closure_W | < 0.15 (docs/VERIFICATION.md:292) | 0.39653103903072084 | FAIL | results/L5/per_cycle.csv:41 (cycle 40): abs(W_hot + W_cold + Qhot_gas + Qcold_gas) |
| L5.8 B6a_dTjoint_K | < 0.1 (docs/VERIFICATION.md:293) | 0.0014748476829531398 | PASS | results/L5/per_cycle.csv:36-41 |
| L5.9 B6b_dH_rel | < 0.02 (docs/VERIFICATION.md:294) | 0.00016253614883509672 | PASS | results/L5/per_cycle.csv:36-41 |
| L5.10 sens_amp_max_rel | < 0.01 (docs/VERIFICATION.md:295) | 0.003962704669913553 | PASS | results/L5/per_cycle_sensitivity.csv:6 vs per_cycle.csv:41 |
| L5.11 sens_phase_max_deg | <= 0.5 (docs/VERIFICATION.md:296) | 0.0329761079804598 | PASS | results/L5/per_cycle_sensitivity.csv:6 vs per_cycle.csv:41 |
| L5.12 hot_p_amp_Pa | report (docs/VERIFICATION.md:297) | 65475.5301437779 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.13 hot_p_ph_deg | report (docs/VERIFICATION.md:298) | 1.1541538710949113 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.14 hot_mdot_amp | report (docs/VERIFICATION.md:299) | 0.002094612997814045 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.15 hot_mdot_ph_deg | report (docs/VERIFICATION.md:300) | 25.596097316502128 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.16 cold_p_amp_Pa | report (docs/VERIFICATION.md:301) | 54199.34175338808 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.17 cold_p_ph_deg | report (docs/VERIFICATION.md:302) | 0.2710576212335728 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.18 cold_mdot_amp | report (docs/VERIFICATION.md:303) | 0.002638840675553126 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.19 cold_mdot_ph_deg | report (docs/VERIFICATION.md:304) | -28.7836108133822 | REPORT (<= 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.20 dp_amp_Pa | report (docs/VERIFICATION.md:305) | 11313.506950653024 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.21 H_hot_W | report (docs/VERIFICATION.md:306) | 1.8626998185155996 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.22 H_joint_W | report (docs/VERIFICATION.md:307) | 1.82415750768259 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.23 H_cold_W | report (docs/VERIFICATION.md:308) | 1.8545024112289 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.24 Tjoint_mean_K | report (docs/VERIFICATION.md:309) | 27.865715126216802 | REPORT (> 0) | results/L5/per_cycle.csv:41 (cycle 40) |
| L5.25 allclean_leftover | == 0 (docs/VERIFICATION.md:310) | 0 | PASS | results/L5/log.allclean-check:empty file |
| L5.7a B5_closure6_W | < 0.15 (docs/VERIFICATION.md:342) | 0.020348915695467644 | PASS | results/L5/per_cycle.csv:41 (cycle 40): abs(W_hot + W_cold + Qhot_gas + Qcold_gas + Qhot_solid + Qcold_solid); sensitivity run cycle 45: six-term -0.041609 W, four-term -0.508583 W (same definition at dt/2 and dx/2, not an independent verification) |

11/12 PASS as preregistered (L5.7 FAIL); supplementary check L5.7a PASS (Amendment A1)
