# Verification bars

Rules (from `docs/TASK.md`): the bars of a level are committed before that level's case is run, and never change
afterwards. A miss is reported as FAIL with a diagnosis.

Machine-readable format. `tools/verify.py` reads every table row of the form

    | <id> | <metric> | <op> | <bar> | <description> |

where `<id>` is `L<level>.<n>`, `<metric>` is the key the level's `results.py` writes, `<op>` is one of
`==`, `<=`, `>=`, `<`, `>`, and `<bar>` is a number. `==` means `|value - bar| <= 1e-9 * max(1, |bar|)`.
A metric that `results.py` could not read is "not read" and counts as FAIL.

## L0 Build and smoke run

Committed before the L0 smoke case (`cases/L0_smoke`) was run for the first time.

The smoke case is a 1-D closed helium tube with a sinusoidal piston (mesh motion), a Darcy-Forchheimer porous plug with
LTNE (solid initially 10 K warmer than the gas), run for a short time. It checks that the code runs; it is not a
physics check.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L0.1 | solver_built | == | 1 | `ltneFoam` is on `PATH` after `src/Allwmake`, as printed by `Allrun` into `log.build` |
| L0.2 | end_line_count | == | 1 | `log.ltneFoam` contains exactly one line `End` (normal termination) |
| L0.3 | final_time | == | 0.001 | last `Time = ` in `log.ltneFoam` equals `endTime` 0.001 s |
| L0.4 | fatal_or_nan_count | == | 0 | lines matching `FOAM FATAL`, `nan` or `inf` (whole word, any case) over all `log.*` of the case |
| L0.5 | p_min | > | 0 | minimum of `min(p)` over all written `fieldMinMax` rows |
| L0.6 | T_min | > | 0 | minimum of `min(T)` over all written `fieldMinMax` rows |
| L0.7 | Ts_min | > | 0 | minimum of `min(Ts)` over all written `fieldMinMax` rows |
| L0.8 | allclean_leftover | == | 0 | files under the case directory that `git status --porcelain --ignored` lists after `Allclean` |

Clean clone: the recorded L0 result is produced from a fresh `git clone` of the branch, and CI runs from a fresh
checkout on every pull request.
