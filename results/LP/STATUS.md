# LP status

| check | bar | value | status | value source |
|---|---|---|---|---|
| LP.1 rho_rel_22 | <= 0.001 (docs/VERIFICATION.md:498) | 1.778622420456344e-07 | PASS | results/LP/propsCheck.dat:3 vs nist_helium.csv:7 |
| LP.2 rho_rel_50 | <= 0.001 (docs/VERIFICATION.md:499) | 5.5572821455740495e-08 | PASS | results/LP/propsCheck.dat:4 vs nist_helium.csv:8 |
| LP.3 rho_rel_80 | <= 0.001 (docs/VERIFICATION.md:500) | 6.797573426364778e-08 | PASS | results/LP/propsCheck.dat:5 vs nist_helium.csv:9 |
| LP.4 cp_rel_22 | <= 0.001 (docs/VERIFICATION.md:501) | 8.904463832948295e-09 | PASS | results/LP/propsCheck.dat:3 vs nist_helium.csv:7 |
| LP.5 cp_rel_50 | <= 0.001 (docs/VERIFICATION.md:502) | 2.6088450066907853e-08 | PASS | results/LP/propsCheck.dat:4 vs nist_helium.csv:8 |
| LP.6 cp_rel_80 | <= 0.001 (docs/VERIFICATION.md:503) | 5.944470915508759e-09 | PASS | results/LP/propsCheck.dat:5 vs nist_helium.csv:9 |
| LP.7 rho_rel_22c | <= 0.001 (docs/VERIFICATION.md:504) | 3.5846840405806546e-05 | PASS | results/LP/propsCheck.dat:6 vs nist_helium.csv:10 |
| LP.8 rho_rel_50c | <= 0.001 (docs/VERIFICATION.md:505) | 1.7929945408390324e-06 | PASS | results/LP/propsCheck.dat:7 vs nist_helium.csv:11 |
| LP.9 rho_rel_80c | <= 0.001 (docs/VERIFICATION.md:506) | 1.043641858600175e-06 | PASS | results/LP/propsCheck.dat:8 vs nist_helium.csv:12 |
| LP.10 cp_rel_22c | <= 0.001 (docs/VERIFICATION.md:507) | 5.222590902187463e-06 | PASS | results/LP/propsCheck.dat:6 vs nist_helium.csv:10 |
| LP.11 cp_rel_50c | <= 0.001 (docs/VERIFICATION.md:508) | 1.0705469999372497e-07 | PASS | results/LP/propsCheck.dat:7 vs nist_helium.csv:11 |
| LP.12 cp_rel_80c | <= 0.001 (docs/VERIFICATION.md:509) | 6.581716338605048e-08 | PASS | results/LP/propsCheck.dat:8 vs nist_helium.csv:12 |
| LP.13 T_roundtrip_max_K | report (docs/VERIFICATION.md:510) | 7.180000238804496e-08 | REPORT (> 0) | results/LP/propsCheck.dat:3-8 (column 6 vs column 1) |
| LP.14 mu_rel_50 | report (docs/VERIFICATION.md:511) | 6.770264571187568e-08 | REPORT (> 0) | results/LP/propsCheck.dat:10 vs nist_helium.csv:8 |
| LP.15 kappa_rel_50 | report (docs/VERIFICATION.md:512) | 8.197369094631313e-08 | REPORT (> 0) | results/LP/propsCheck.dat:10 vs nist_helium.csv:8 |
| LP.16 allclean_leftover | == 0 (docs/VERIFICATION.md:513) | 0 | PASS | results/LP/log.allclean-check:empty file |
| LP.17 out_of_range_stopped | == 4 (docs/VERIFICATION.md:523) | 4 | PASS | results/LP/log.oorLowT:log.oorLowT:43, log.oorHighT:43, log.oorLowP:43, log.oorHighP:43 |
| LP.18 out_of_range_values_written | == 0 (docs/VERIFICATION.md:524) | 0 | PASS | results/LP/log.oorLowT:oor*.dat present: 0 |

15/15 PASS
