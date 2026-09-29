# L6 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L6.1 cycles_G1 | <= 300 (docs/VERIFICATION.md:413) | 70 | PASS | results/L6/per_cycle_G1.csv:66-71 (cycles 65-70) |
| L6.2 cycles_G2 | <= 300 (docs/VERIFICATION.md:414) | 40 | PASS | results/L6/per_cycle_G2.csv:36-41 (cycles 35-40) |
| L6.3 cycles_G3 | <= 300 (docs/VERIFICATION.md:415) | 40 | PASS | results/L6/per_cycle_G3.csv:36-41 (cycles 35-40) |
| L6.4 cycles_T2 | <= 300 (docs/VERIFICATION.md:416) | 40 | PASS | results/L6/per_cycle_T2.csv:36-41 (cycles 35-40) |
| L6.5 gci_H_hot | < 0.03 (docs/VERIFICATION.md:417) | 0.011697717743593744 | PASS | results/L6/gci.csv:2 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.6 gci_H_joint | < 0.03 (docs/VERIFICATION.md:418) | 6.989879028503001e-07 | PASS | results/L6/gci.csv:3 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.7 gci_H_cold | < 0.03 (docs/VERIFICATION.md:419) | 7.633103964207516e-05 | PASS | results/L6/gci.csv:4 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.8 gci_Qgs_abs | < 0.03 (docs/VERIFICATION.md:420) | 0.00895765788285963 | PASS | results/L6/gci.csv:5 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.9 gci_dp_amp | < 0.03 (docs/VERIFICATION.md:421) | 0.006550558668613017 | PASS | results/L6/gci.csv:6 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.10 p_err_H_hot | <= 0.5 (docs/VERIFICATION.md:422) | 0.2916664186891149 | PASS | results/L6/gci.csv:2 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.11 p_err_H_joint | <= 0.5 (docs/VERIFICATION.md:423) | 2.6470789136868014 | FAIL | results/L6/gci.csv:3 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.12 p_err_H_cold | <= 0.5 (docs/VERIFICATION.md:424) | 0.9384520272046459 | FAIL | results/L6/gci.csv:4 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.13 p_err_Qgs_abs | <= 0.5 (docs/VERIFICATION.md:425) | 1.7579189132426132 | FAIL | results/L6/gci.csv:5 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.14 p_err_dp_amp | <= 0.5 (docs/VERIFICATION.md:426) | 1.3833418985143875 | FAIL | results/L6/gci.csv:6 (per_cycle_G3.csv:41, per_cycle_G2.csv:41, per_cycle_G1.csv:71) |
| L6.15 dt_rel_H_hot | < 0.01 (docs/VERIFICATION.md:427) | 0.001861078930622462 | PASS | results/L6/gci.csv:2 (per_cycle_T2.csv:41 vs per_cycle_G2.csv:41) |
| L6.16 dt_rel_H_joint | < 0.01 (docs/VERIFICATION.md:428) | 0.0001099179221239665 | PASS | results/L6/gci.csv:3 (per_cycle_T2.csv:41 vs per_cycle_G2.csv:41) |
| L6.17 dt_rel_H_cold | < 0.01 (docs/VERIFICATION.md:429) | 0.0017704109893429496 | PASS | results/L6/gci.csv:4 (per_cycle_T2.csv:41 vs per_cycle_G2.csv:41) |
| L6.18 dt_rel_Qgs_abs | < 0.01 (docs/VERIFICATION.md:430) | 0.0005952349424372052 | PASS | results/L6/gci.csv:5 (per_cycle_T2.csv:41 vs per_cycle_G2.csv:41) |
| L6.19 dt_rel_dp_amp | < 0.01 (docs/VERIFICATION.md:431) | 5.1948468358761094e-05 | PASS | results/L6/gci.csv:6 (per_cycle_T2.csv:41 vs per_cycle_G2.csv:41) |
| L6.20 crash_count | == 0 (docs/VERIFICATION.md:432) | 0 | PASS | results/L6/log.*:all lines of all logs of all runs; 27 trapFpe banner lines skipped |
| L6.21 closure4_G2_W | report (docs/VERIFICATION.md:433) | -0.39653103830555936 | REPORT (<= 0) | results/L6/per_cycle_G2.csv:41 |
| L6.22 closure6_G2_W | report (docs/VERIFICATION.md:434) | 0.020348916425388656 | REPORT (> 0) | results/L6/per_cycle_G2.csv:41 |
| L6.23 closure4_G3_W | report (docs/VERIFICATION.md:435) | -0.5837685519534406 | REPORT (<= 0) | results/L6/per_cycle_G3.csv:41 |
| L6.24 closure6_G3_W | report (docs/VERIFICATION.md:436) | -0.02666457175622873 | REPORT (<= 0) | results/L6/per_cycle_G3.csv:41 |
| L6.25 allclean_leftover | == 0 (docs/VERIFICATION.md:437) | 0 | PASS | results/L6/log.allclean-check:empty file |

17/21 PASS
