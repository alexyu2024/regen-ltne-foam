# L0 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L0.1 solver_built | == 1 (docs/VERIFICATION.md:24) | 1 | PASS | results/L0/log.build:13 |
| L0.2 end_line_count | == 1 (docs/VERIFICATION.md:25) | 1 | PASS | results/L0/log.ltneFoam:45085 |
| L0.3 final_time | == 0.001 (docs/VERIFICATION.md:26) | 0.001 | PASS | results/L0/log.ltneFoam:45041 |
| L0.4 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:27) | 0 | PASS | results/L0/log.*:all lines |
| L0.5 p_min | > 0 (docs/VERIFICATION.md:28) | 2000000.0 | PASS | results/L0/fieldMinMax.dat:5-3002 (rows with field p) |
| L0.6 T_min | > 0 (docs/VERIFICATION.md:29) | 300.0 | PASS | results/L0/fieldMinMax.dat:3-3000 (rows with field T) |
| L0.7 Ts_min | > 0 (docs/VERIFICATION.md:30) | 300.0 | PASS | results/L0/fieldMinMax.dat:4-3001 (rows with field Ts) |
| L0.8 allclean_leftover | == 0 (docs/VERIFICATION.md:31) | 0 | PASS | results/L0/log.allclean-check:empty file |

8/8 PASS
Storage note (added in the L1 PR, at the author's request): `log.ltneFoam` is stored gzipped as `log.ltneFoam.gz`;
the line numbers cited here refer to the uncompressed text (`zcat log.ltneFoam.gz | sed -n 45085p`).

## How this was produced

`tools/run_level.sh L0 results/L0` in a fresh `git clone` of branch `claude/sharp-carson-dz42ib` at commit 35601b5,
2026-09-26. The user binaries (`ltneFoam`, `libltnePistonMotion.so`) were deleted first, so `Allrun` compiled both
from source (`log.build`). Machine: Ubuntu 24.04 container, 4 cores, OpenFOAM v2512 package 2512.0-2. Every file
cited above is in this directory; `results.csv` is the machine-readable form.

## Informal consistency check (not an L0 bar)

The smoke case is closed, so the gas energy gain should equal the solid energy loss plus the piston work.

| quantity | value | source |
|---|---|---|
| gas internal energy, t = 0 | -18.5101760558 J | `log.ltneFoam:84` |
| gas internal energy, t = 1 ms | -18.2686564105 J | `log.ltneFoam:45074` |
| solid energy, t = 0 | 734.7 J | `log.ltneFoam:84` |
| solid energy, t = 1 ms | 734.520722583 J | `log.ltneFoam:45074` |
| gas mass, t = 0 and t = 1 ms | 3.01678396811e-05 kg (identical to 12 digits) | `log.ltneFoam:84`, `:45074` |
| volume swept by the piston | 1e-05 - 9.96909830056e-06 = 3.0902e-08 m3 | `log.ltneFoam:84`, `:45074` |
| gas gain + solid change = piston work | 0.24152 - 0.17928 = 0.06224 J | from the rows above |
| bounds on piston work, min(p) dV .. max(p) dV | 0.06180 .. 0.06255 J | min(p) 2.0e6 Pa `fieldMinMax.dat:5`, max(p) 2.024119866e6 Pa `fieldMinMax.dat:3002` |

The implied piston work is inside the bounds. The piston work itself was not computed ("not read").
