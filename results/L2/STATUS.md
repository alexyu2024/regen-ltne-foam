# L2 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L2.1 v1_final_time | == 0.05 (docs/VERIFICATION.md:118) | 0.05 | PASS | results/L2/v1.log.ltneFoam:71279 |
| L2.2 v2_final_time | == 0.05 (docs/VERIFICATION.md:119) | 0.05 | PASS | results/L2/v2.log.ltneFoam:71279 |
| L2.3 v3_final_time | == 0.05 (docs/VERIFICATION.md:120) | 0.05 | PASS | results/L2/v3.log.ltneFoam:71279 |
| L2.4 v4_final_time | == 0.05 (docs/VERIFICATION.md:121) | 0.05 | PASS | results/L2/v4.log.ltneFoam:71279 |
| L2.5 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:122) | 0 | PASS | results/L2/log.*:all lines of all logs |
| L2.6 v1_rel_err | <= 0.01 (docs/VERIFICATION.md:123) | 1.0012468423248322e-06 | PASS | results/L2/v1.inletP.dat:105 with v1.outletP.dat:105, v1.inletFlux.dat:105, v1.porousRho.dat:104 |
| L2.7 v2_rel_err | <= 0.01 (docs/VERIFICATION.md:124) | 1.106048323595843e-06 | PASS | results/L2/v2.inletP.dat:105 with v2.outletP.dat:105, v2.inletFlux.dat:105, v2.porousRho.dat:104 |
| L2.8 v3_rel_err | <= 0.01 (docs/VERIFICATION.md:125) | 1.6494313372028557e-05 | PASS | results/L2/v3.inletP.dat:105 with v3.outletP.dat:105, v3.inletFlux.dat:105, v3.porousRho.dat:104 |
| L2.9 v4_rel_err | <= 0.01 (docs/VERIFICATION.md:126) | 0.0003833087411541092 | PASS | results/L2/v4.inletP.dat:105 with v4.outletP.dat:105, v4.inletFlux.dat:105, v4.porousRho.dat:104 |
| L2.10 v1_ratio | <= 0.1 (docs/VERIFICATION.md:127) | 0.008063681635022614 | PASS | results/L2/v1.porousRho.dat:104 with v1.inletFlux.dat:105 |
| L2.11 v4_ratio | >= 1 (docs/VERIFICATION.md:128) | 8.078258201515075 | PASS | results/L2/v4.porousRho.dat:104 with v4.inletFlux.dat:105 |
| L2.12 v2_ratio | report (docs/VERIFICATION.md:129) | 0.08063697358103013 | REPORT (> 0) | results/L2/v2.porousRho.dat:104 with v2.inletFlux.dat:105 |
| L2.13 v3_ratio | report (docs/VERIFICATION.md:130) | 0.8063969888660804 | REPORT (> 0) | results/L2/v3.porousRho.dat:104 with v3.inletFlux.dat:105 |
| L2.14 v1_steady | <= 1e-3 (docs/VERIFICATION.md:131) | 0.0 | PASS | results/L2/v1.inletP.dat:95,105 with v1.outletP.dat:95,105 |
| L2.15 v2_steady | <= 1e-3 (docs/VERIFICATION.md:132) | 0.0 | PASS | results/L2/v2.inletP.dat:95,105 with v2.outletP.dat:95,105 |
| L2.16 v3_steady | <= 1e-3 (docs/VERIFICATION.md:133) | 1.5299771127306808e-07 | PASS | results/L2/v3.inletP.dat:95,105 with v3.outletP.dat:95,105 |
| L2.17 v4_steady | <= 1e-3 (docs/VERIFICATION.md:134) | 0.000223507817210639 | PASS | results/L2/v4.inletP.dat:95,105 with v4.outletP.dat:95,105 |
| L2.18 v1_dp | report (docs/VERIFICATION.md:135) | 0.4012090000323951 | REPORT (> 0) | results/L2/v1.inletP.dat:105 minus v1.outletP.dat:105 |
| L2.19 v4_dp | report (docs/VERIFICATION.md:136) | 3615.766151000047 | REPORT (> 0) | results/L2/v4.inletP.dat:105 minus v4.outletP.dat:105 |
| L2.20 allclean_leftover | == 0 (docs/VERIFICATION.md:137) | 0 | PASS | results/L2/log.allclean-check:empty file |

16/16 PASS
