# L3 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L3.1 r_final_time | == 0.00145 (docs/VERIFICATION.md:172) | 0.00145 | PASS | results/L3/r.log.ltneFoam:7058 |
| L3.2 b_final_time | == 0.0009 (docs/VERIFICATION.md:173) | 0.0009 | PASS | results/L3/b.log.ltneFoam:7058 |
| L3.3 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:174) | 0 | PASS | results/L3/log.*:all lines of all logs |
| L3.4 r_err_g | <= 0.01 (docs/VERIFICATION.md:175) | 0.0018524230590713842 | PASS | results/L3/r.ltne.dat:2-502 |
| L3.5 r_err_s | <= 0.01 (docs/VERIFICATION.md:176) | 9.320147273683688e-06 | PASS | results/L3/r.ltne.dat:2-502 |
| L3.6 r_energy | <= 1e-3 (docs/VERIFICATION.md:177) | 0.0006624253040098374 | PASS | results/L3/r.ltne.dat:2-502 |
| L3.7 b_err_g | <= 0.01 (docs/VERIFICATION.md:178) | 0.0011082747087158395 | PASS | results/L3/b.ltne.dat:2-502 |
| L3.8 b_err_s | <= 0.01 (docs/VERIFICATION.md:179) | 0.0006346681022932898 | PASS | results/L3/b.ltne.dat:2-502 |
| L3.9 b_energy | <= 1e-3 (docs/VERIFICATION.md:180) | 0.0006456878334820943 | PASS | results/L3/b.ltne.dat:2-502 |
| L3.10 r_Teq | report (docs/VERIFICATION.md:181) | 319.7455433893626 | REPORT (> 0) | results/L3/r.ltne.dat:502 |
| L3.11 b_Teq | report (docs/VERIFICATION.md:182) | 312.4799024281084 | REPORT (> 0) | results/L3/b.ltne.dat:502 |
| L3.12 allclean_leftover | == 0 (docs/VERIFICATION.md:183) | 0 | PASS | results/L3/log.allclean-check:empty file |

10/10 PASS
