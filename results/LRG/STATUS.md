# LRG status

| check | bar | value | status | value source |
|---|---|---|---|---|
| LRG.1 restart_check_rel | <= 1e-09 (docs/VERIFICATION.md:727) | 0.0 | PASS | results/LRG/restartcheck.json:cycles 4801-4900 |
| LRG.2 inventory_rel | report (docs/VERIFICATION.md:728) | -0.007214758468591098 | REPORT (<= 0) | results/LRG/switch.json:inventory_rel |
| LRG.3 rg_cycles | report (docs/VERIFICATION.md:729) | 6000 | REPORT (> 0) | results/LRG/real_cycles.csv:cycles 4901-10900 |
| LRG.4 rg_remaining_max_frac | <= 0.2 (docs/VERIFICATION.md:730) | 0.2713365247729671 | FAIL | results/LRG/real_acceptance.json:ref_remaining_max_frac |
| LRG.5 rg_mass_drift_max | <= 1e-09 (docs/VERIFICATION.md:731) | 4.923340194410067e-11 | PASS | results/LRG/real_cycles.csv:gas_mass_kg, cycles 4901-10900 vs switch.json M_real0 |
| LRG.6 Q_hot_ideal_W | report (docs/VERIFICATION.md:732) | -12.189233105974894 | REPORT (<= 0) | results/LRG/ideal_reference.json:ref.Q_hot (L5P reference, cycle 4900) |
| LRG.7 Q_hot_real_W | report (docs/VERIFICATION.md:733) | -12.770286607781353 | REPORT (<= 0) | results/LRG/real_acceptance.json:ref.Q_hot (cycle 10900) |
| LRG.8 dQ_hot_rel | report (docs/VERIFICATION.md:734) | 0.04766940600402816 | REPORT (> 0) | results/LRG/real_acceptance.json:vs ideal_reference.json; equal initial mean pressure |
| LRG.9 dQ_hot_unc | report (docs/VERIFICATION.md:735) | 0.00013680727933683529 | REPORT (> 0) | results/LRG/real_acceptance.json:remaining distances 9.860e-04 W (real) + 6.816e-04 W (ideal) |
| LRG.10 Q_cold_ideal_W | report (docs/VERIFICATION.md:736) | 1.8545558018103432 | REPORT (> 0) | results/LRG/ideal_reference.json:ref.Q_cold (L5P reference, cycle 4900) |
| LRG.11 Q_cold_real_W | report (docs/VERIFICATION.md:737) | 1.9751817149708315 | REPORT (> 0) | results/LRG/real_acceptance.json:ref.Q_cold (cycle 10900) |
| LRG.12 dQ_cold_rel | report (docs/VERIFICATION.md:738) | 0.06504302164579687 | REPORT (> 0) | results/LRG/real_acceptance.json:vs ideal_reference.json; equal initial mean pressure |
| LRG.13 dQ_cold_unc | report (docs/VERIFICATION.md:739) | 6.310081393838012e-05 | REPORT (> 0) | results/LRG/real_acceptance.json:remaining distances 7.102e-05 W (real) + 4.600e-05 W (ideal) |
| LRG.14 p_mean_drift_rel | report (docs/VERIFICATION.md:740) | 0.011890024284801098 | REPORT (> 0) | results/LRG/real_acceptance.json:ref.p_mean vs ideal_reference.json |
| LRG.15 crash_count | == 0 (docs/VERIFICATION.md:741) | 0 | PASS | results/LRG/log.*:all lines of all logs; 61 trapFpe banner lines skipped |
| LRG.16 allclean_leftover | == 0 (docs/VERIFICATION.md:742) | 0 | PASS | results/LRG/log.allclean-check:empty file |

4/5 PASS
