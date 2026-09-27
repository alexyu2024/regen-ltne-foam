# L4 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L4.1 final_time | == 150 (docs/VERIFICATION.md:238) | 150.0 | PASS | results/L4/log.ltneFoam:424562 |
| L4.2 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:239) | 0 | PASS | results/L4/log.*:all lines of all logs |
| L4.3 out_err | <= 0.02 (docs/VERIFICATION.md:240) | 0.001473263962978838 | PASS | results/L4/outletT.dat:6-1505 |
| L4.4 Es_err | <= 0.01 (docs/VERIFICATION.md:241) | 0.000538644919982398 | PASS | results/L4/ltne.dat:2-30002 (every 100th row) |
| L4.5 energy_err | <= 0.01 (docs/VERIFICATION.md:242) | 0.0005161299789159485 | PASS | results/L4/ltne.dat:2,30002 with outletT.dat:6-1505 |
| L4.6 t_half | report (docs/VERIFICATION.md:243) | 70.36896041267686 | REPORT (> 0) | results/L4/outletT.dat:6-1505 |
| L4.7 t_half_exact | report (docs/VERIFICATION.md:244) | 70.4362206670653 | REPORT (> 0) | results/L4/outletT.dat:computed from the inputs |
| L4.8 allclean_leftover | == 0 (docs/VERIFICATION.md:245) | 0 | PASS | results/L4/log.allclean-check:empty file |

6/6 PASS
