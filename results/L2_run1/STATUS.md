# L2 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L2.1 v1_final_time | == 0.05 (docs/VERIFICATION.md:118) | 0.05 | PASS | results/L2/v1.log.ltneFoam:71277 |
| L2.2 v2_final_time | == 0.05 (docs/VERIFICATION.md:119) | 0.05 | PASS | results/L2/v2.log.ltneFoam:71277 |
| L2.3 v3_final_time | == 0.05 (docs/VERIFICATION.md:120) | 0.05 | PASS | results/L2/v3.log.ltneFoam:71277 |
| L2.4 v4_final_time | == 0.05 (docs/VERIFICATION.md:121) | 0.05 | PASS | results/L2/v4.log.ltneFoam:71277 |
| L2.5 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:122) | 0 | PASS | results/L2/log.*:all lines of all logs |
| L2.6 v1_rel_err | <= 0.01 (docs/VERIFICATION.md:123) | 0.02244065202199519 | FAIL | results/L2/v1.inletP.dat:105 with v1.outletP.dat:105, v1.inletFlux.dat:105, v1.porousRho.dat:104 |
| L2.7 v2_rel_err | <= 0.01 (docs/VERIFICATION.md:124) | 0.02282258515027824 | FAIL | results/L2/v2.inletP.dat:105 with v2.outletP.dat:105, v2.inletFlux.dat:105, v2.porousRho.dat:104 |
| L2.8 v3_rel_err | <= 0.01 (docs/VERIFICATION.md:125) | 0.026903305392853905 | FAIL | results/L2/v3.inletP.dat:105 with v3.outletP.dat:105, v3.inletFlux.dat:105, v3.porousRho.dat:104 |
| L2.9 v4_rel_err | <= 0.01 (docs/VERIFICATION.md:126) | 0.036529972112332776 | FAIL | results/L2/v4.inletP.dat:105 with v4.outletP.dat:105, v4.inletFlux.dat:105, v4.porousRho.dat:104 |
| L2.10 v1_ratio | <= 0.1 (docs/VERIFICATION.md:127) | 0.008063681598723617 | PASS | results/L2/v1.porousRho.dat:104 with v1.inletFlux.dat:105 |
| L2.11 v4_ratio | >= 1 (docs/VERIFICATION.md:128) | 8.07772973645226 | PASS | results/L2/v4.porousRho.dat:104 with v4.inletFlux.dat:105 |
| L2.12 v2_ratio | report (docs/VERIFICATION.md:129) | 0.08063696962359296 | REPORT (> 0) | results/L2/v2.porousRho.dat:104 with v2.inletFlux.dat:105 |
| L2.13 v3_ratio | report (docs/VERIFICATION.md:130) | 0.8063962094585426 | REPORT (> 0) | results/L2/v3.porousRho.dat:104 with v3.inletFlux.dat:105 |
| L2.14 v1_steady | <= 1e-3 (docs/VERIFICATION.md:131) | 2.549699940002147e-06 | PASS | results/L2/v1.inletP.dat:95,105 with v1.outletP.dat:95,105 |
| L2.15 v2_steady | <= 1e-3 (docs/VERIFICATION.md:132) | 1.1896969395084235e-06 | PASS | results/L2/v2.inletP.dat:95,105 with v2.outletP.dat:95,105 |
| L2.16 v3_steady | <= 1e-3 (docs/VERIFICATION.md:133) | 1.8581553055548573e-07 | PASS | results/L2/v3.inletP.dat:95,105 with v3.outletP.dat:95,105 |
| L2.17 v4_steady | <= 1e-3 (docs/VERIFICATION.md:134) | 0.0002231023825906778 | PASS | results/L2/v4.inletP.dat:95,105 with v4.outletP.dat:95,105 |
| L2.18 v1_dp | report (docs/VERIFICATION.md:135) | 0.39220599993132055 | REPORT (> 0) | results/L2/v1.inletP.dat:105 minus v1.outletP.dat:105 |
| L2.19 v4_dp | report (docs/VERIFICATION.md:136) | 3484.6916070000734 | REPORT (> 0) | results/L2/v4.inletP.dat:105 minus v4.outletP.dat:105 |
| L2.20 allclean_leftover | == 0 (docs/VERIFICATION.md:137) | 0 | PASS | results/L2/log.allclean-check:empty file |

12/16 PASS
