# LRG status

| check | bar | value | status | value source |
|---|---|---|---|---|
| LRG.1 restart_check_rel | <= 1e-09 (docs/VERIFICATION.md:727) | 0.0 | PASS | results/LRG_A3/restartcheck.json:cycles 4801-4900 |
| LRG.2 inventory_rel | report (docs/VERIFICATION.md:728) | -0.007214758468591098 | REPORT (<= 0) | results/LRG_A3/switch.json:inventory_rel |
| LRG.3 rg_cycles | report (docs/VERIFICATION.md:729) | 6200 | REPORT (> 0) | results/LRG_A3/real_cycles.csv:cycles 4901-11100 |
| LRG.4 rg_remaining_max_frac | <= 0.2 (docs/VERIFICATION.md:730) | 0.19288697411406341 | PASS | results/LRG_A3/real_acceptance.json:ref_remaining_max_frac |
| LRG.5 rg_mass_drift_max | <= 1e-09 (docs/VERIFICATION.md:731) | 4.923340194410067e-11 | PASS | results/LRG_A3/real_cycles.csv:gas_mass_kg, cycles 4901-11100 vs switch.json M_real0 |
| LRG.6 Q_hot_ideal_W | report (docs/VERIFICATION.md:732) | -12.189233105974894 | REPORT (<= 0) | results/LRG_A3/ideal_reference.json:ref.Q_hot (L5P reference, cycle 4900) |
| LRG.7 Q_hot_real_W | report (docs/VERIFICATION.md:733) | -12.770402713483632 | REPORT (<= 0) | results/LRG_A3/real_acceptance.json:ref.Q_hot (cycle 11100) |
| LRG.8 dQ_hot_rel | report (docs/VERIFICATION.md:734) | 0.04767893127122665 | REPORT (> 0) | results/LRG_A3/real_acceptance.json:vs ideal_reference.json; equal initial mean pressure |
| LRG.9 dQ_hot_unc | report (docs/VERIFICATION.md:735) | 0.00011365540907670587 | REPORT (> 0) | results/LRG_A3/real_acceptance.json:remaining distances 7.038e-04 W (real) + 6.816e-04 W (ideal) |
| LRG.10 Q_cold_ideal_W | report (docs/VERIFICATION.md:736) | 1.8545558018103432 | REPORT (> 0) | results/LRG_A3/ideal_reference.json:ref.Q_cold (L5P reference, cycle 4900) |
| LRG.11 Q_cold_real_W | report (docs/VERIFICATION.md:737) | 1.9751900884525109 | REPORT (> 0) | results/LRG_A3/real_acceptance.json:ref.Q_cold (cycle 11100) |
| LRG.12 dQ_cold_rel | report (docs/VERIFICATION.md:738) | 0.06504753673327561 | REPORT (> 0) | results/LRG_A3/real_acceptance.json:vs ideal_reference.json; equal initial mean pressure |
| LRG.13 dQ_cold_unc | report (docs/VERIFICATION.md:739) | 5.218906849976484e-05 | REPORT (> 0) | results/LRG_A3/real_acceptance.json:remaining distances 5.078e-05 W (real) + 4.600e-05 W (ideal) |
| LRG.14 p_mean_drift_rel | report (docs/VERIFICATION.md:740) | 0.011893001735058079 | REPORT (> 0) | results/LRG_A3/real_acceptance.json:ref.p_mean vs ideal_reference.json |
| LRG.15 crash_count | == 0 (docs/VERIFICATION.md:741) | 0 | PASS | results/LRG_A3/log.*:all lines of all logs; 63 trapFpe banner lines skipped |
| LRG.16 allclean_leftover | == 0 (docs/VERIFICATION.md:742) | 0 | PASS | results/LRG_A3/log.allclean-check:empty file |

5/5 PASS
