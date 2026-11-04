# L5P status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L5P.1 c40_Tjoint_diff_K | <= 1e-05 (docs/VERIFICATION.md:588) | 1.1389829523977824e-07 | PASS | results/L5P/natural/per_cycle.csv:41 (cycle 40) |
| L5P.2 ref_cycles | report (docs/VERIFICATION.md:589) | 4900 | REPORT (> 0) | results/L5P/reference.json:ref_cycles |
| L5P.3 ref_remaining_max_frac | <= 0.2 (docs/VERIFICATION.md:590) | 0.19272167822681113 | PASS | results/L5P/reference.json:ref_remaining_max_frac |
| L5P.4 nat_k | report (docs/VERIFICATION.md:591) | 4145 | REPORT (> 0) | results/L5P/reference.json:nat_k |
| L5P.5 nat_total | report (docs/VERIFICATION.md:592) | 4195 | REPORT (> 0) | results/L5P/reference.json:nat_total |
| L5P.6 nat_within_from | report (docs/VERIFICATION.md:593) | 4156 | REPORT (> 0) | results/L5P/reference.json:nat_within_from |
| L5P.7 nat_mass_drift_max | <= 1e-09 (docs/VERIFICATION.md:594) | 3.538434927430517e-11 | PASS | results/L5P/reference.json:nat_mass_drift_max |
| L5P.8 noise_N1_K | report (docs/VERIFICATION.md:595) | 0.0 | REPORT (<= 0) | results/L5P/noise.csv:2 |
| L5P.9 noise_N2_K | report (docs/VERIFICATION.md:596) | 1.7356400405788008e-07 | REPORT (> 0) | results/L5P/noise.csv:3 |
| L5P.10 noise_N3_K | report (docs/VERIFICATION.md:597) | 1.122003823184059e-09 | REPORT (> 0) | results/L5P/noise.csv:4 |
| L5P.11 noise_N4_floor | report (docs/VERIFICATION.md:598) | 6.879137421659911e-05 | REPORT (> 0) | results/L5P/noise_summary.json:N4_floor |
| L5P.12 crash_count | == 0 (docs/VERIFICATION.md:599) | 0 | PASS | results/L5P/natural/log.*:all lines of 53 natural logs (51 trapFpe banner lines skipped) and of every map evaluation of 8 study runs (scanned when they ran) |
| L5P.13 allclean_leftover | == 0 (docs/VERIFICATION.md:600) | 0 | PASS | results/L5P/log.allclean-check:empty file |
| L5P.14 np1_total | report (docs/VERIFICATION.md:601) | 639 | REPORT (> 0) | results/L5P/methods/np1_summary.json:total |
| L5P.15 np1_pass | report (docs/VERIFICATION.md:602) | 0 | REPORT (<= 0) | results/L5P/methods/np1_summary.json:passed |
| L5P.16 np2_total | report (docs/VERIFICATION.md:603) | 639 | REPORT (> 0) | results/L5P/methods/np2_summary.json:total |
| L5P.17 np2_pass | report (docs/VERIFICATION.md:604) | 0 | REPORT (<= 0) | results/L5P/methods/np2_summary.json:passed |
| L5P.18 np3_total | report (docs/VERIFICATION.md:605) | 639 | REPORT (> 0) | results/L5P/methods/np3_summary.json:total |
| L5P.19 np3_pass | report (docs/VERIFICATION.md:606) | 0 | REPORT (<= 0) | results/L5P/methods/np3_summary.json:passed |
| L5P.20 brr3_total | report (docs/VERIFICATION.md:607) | 640 | REPORT (> 0) | results/L5P/methods/brr3_summary.json:total |
| L5P.21 brr3_pass | report (docs/VERIFICATION.md:608) | 0 | REPORT (<= 0) | results/L5P/methods/brr3_summary.json:passed |
| L5P.22 brr6_total | report (docs/VERIFICATION.md:609) | 640 | REPORT (> 0) | results/L5P/methods/brr6_summary.json:total |
| L5P.23 brr6_pass | report (docs/VERIFICATION.md:610) | 0 | REPORT (<= 0) | results/L5P/methods/brr6_summary.json:passed |
| L5P.24 gm0_total | report (docs/VERIFICATION.md:611) | 640 | REPORT (> 0) | results/L5P/methods/gm0_summary.json:total |
| L5P.25 gm0_pass | report (docs/VERIFICATION.md:612) | 0 | REPORT (<= 0) | results/L5P/methods/gm0_summary.json:passed |
| L5P.26 gm3_total | report (docs/VERIFICATION.md:613) | 640 | REPORT (> 0) | results/L5P/methods/gm3_summary.json:total |
| L5P.27 gm3_pass | report (docs/VERIFICATION.md:614) | 0 | REPORT (<= 0) | results/L5P/methods/gm3_summary.json:passed |

5/5 PASS
