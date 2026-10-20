# L5D status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L5D.1 cycles_run | report (docs/VERIFICATION.md:464) | 600 | REPORT (> 0) | results/L5D/decay.csv:2-601 |
| L5D.2 r_fit_Tjoint | report (docs/VERIFICATION.md:465) | 0.9966999800468185 | REPORT (> 0) | results/L5D/decay.csv:502-601 (cycles 501-600) |
| L5D.3 r_mean50_Tjoint | report (docs/VERIFICATION.md:466) | 0.9966817899789661 | REPORT (> 0) | results/L5D/decay.csv:552-601 |
| L5D.4 r_window_change | report (docs/VERIFICATION.md:467) | 4.421358521500274e-05 | REPORT (> 0) | results/L5D/decay.csv:502-601 |
| L5D.5 tau_cycles | report (docs/VERIFICATION.md:468) | 302.52819533693906 | REPORT (> 0) | results/L5D/decay.csv:502-601 (cycles 501-600) |
| L5D.6 tau_s | report (docs/VERIFICATION.md:469) | 13.15339979725822 | REPORT (> 0) | results/L5D/decay.csv:502-601 (cycles 501-600) |
| L5D.7 Tjoint_inf_K | report (docs/VERIFICATION.md:470) | 27.042081102899747 | REPORT (> 0) | results/L5D/decay.csv:601, r_fit |
| L5D.8 Tjoint_last_K | report (docs/VERIFICATION.md:471) | 27.212006706693085 | REPORT (> 0) | results/L5D/decay.csv:601 |
| L5D.9 r_fit_H_joint | report (docs/VERIFICATION.md:472) | 1.0338594612259537 | REPORT (> 0) | results/L5D/per_cycle.csv:502-601 (cycles 501-600) |
| L5D.10 r_fit_H_hot | report (docs/VERIFICATION.md:473) | 0.9901113847845725 | REPORT (> 0) | results/L5D/per_cycle.csv:502-601 (cycles 501-600) |
| L5D.11 crash_count | == 0 (docs/VERIFICATION.md:474) | 0 | PASS | results/L5D/log.*:all lines of all logs; 14 trapFpe banner lines skipped |
| L5D.12 allclean_leftover | == 0 (docs/VERIFICATION.md:475) | 0 | PASS | results/L5D/log.allclean-check:empty file |

2/2 PASS
