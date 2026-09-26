# L4 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L4.1 final_time | == 150 (docs/VERIFICATION.md:238) | not read | FAIL | results/L4/log.ltneFoam (not found) |
| L4.2 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:239) | 0 | PASS | results/L4/log.*:all lines of all logs |
| L4.3 out_err | <= 0.02 (docs/VERIFICATION.md:240) | not read | FAIL | results/L4/outletT.dat (not found) |
| L4.4 Es_err | <= 0.01 (docs/VERIFICATION.md:241) | not read | FAIL | results/L4/ltne.dat (not found) |
| L4.5 energy_err | <= 0.01 (docs/VERIFICATION.md:242) | not read | FAIL | results/L4/ltne.dat (not found) |
| L4.6 t_half | report (docs/VERIFICATION.md:243) | not read | REPORT (not read) | results/L4/outletT.dat (not found) |
| L4.7 t_half_exact | report (docs/VERIFICATION.md:244) | not read | REPORT (not read) | results/L4/outletT.dat (not found) |
| L4.8 allclean_leftover | == 0 (docs/VERIFICATION.md:245) | 0 | PASS | results/L4/log.allclean-check:empty file |

2/6 PASS
