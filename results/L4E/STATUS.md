# L4E status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L4E.1 final_time | == 150 (docs/VERIFICATION.md:799) | 150.0 | PASS | results/L4E/log.ltneFoam:433577 |
| L4E.2 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:800) | 0 | PASS | results/L4E/log.ltneFoam:all lines of log.blockMesh and log.ltneFoam |
| L4E.3 gas_err | <= 0.03 (docs/VERIFICATION.md:801) | 0.0022647689188936004 | PASS | results/L4E/probe_T.dat:4-1503; max at line 818, x = 0.09975 m, t = 81.5 s |
| L4E.4 solid_err | <= 0.03 (docs/VERIFICATION.md:802) | 0.0023923357806601153 | PASS | results/L4E/probe_Ts.dat:4-1503; max at line 880, x = 0.09975 m, t = 87.7 s |
| L4E.5 dp_rel_err | <= 0.02 (docs/VERIFICATION.md:803) | 0.0025049220296875507 | PASS | results/L4E/inletP.dat:6-1505; max at line 1505, t = 150 s |
| L4E.6 dp_final_Pa | report (docs/VERIFICATION.md:804) | 769.7926819999702 | REPORT (> 0) | results/L4E/inletP.dat:line 1505 |
| L4E.7 dp_ergun_final_Pa | report (docs/VERIFICATION.md:805) | 771.7257949446051 | REPORT (> 0) | results/L4E/inletP.dat:line 1505; Ergun with bedRho.dat and inletFlux.dat |
| L4E.8 Re_p | report (docs/VERIFICATION.md:806) | 7.806564887326633 | REPORT (> 0) | results/L4E/inletFlux.dat:G d_p / mu, line 1505 |
| L4E.9 allclean_leftover | == 0 (docs/VERIFICATION.md:807) | 0 | PASS | results/L4E/log.allclean-check:empty file |

6/6 PASS
