## How this was produced

The GitHub Actions `run-case` workflow ran the case with input `level = L5`, as three jobs chained by the restart
state (`restart_run_id`):

| run | commit | what it did | outcome |
|---|---|---|---|
| [36304925703](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/36304925703) | 7521e0d | base run, 40 cycles (B6 held at cycle 40) | the sensitivity set-up stopped: `moveDynamicMesh` wrote the moved mesh as `1.7391304347797` (timePrecision 14), and the script looked for the base run's name `1.7391304347797016` |
| [36307305040](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/36307305040) | fc2b899 | sensitivity run (5 cycles), final post-processing | the run finished. The workflow failed because `runLong.sh` resolved the relative output directory after `cd`, so the CSVs landed in the case directory, not in `out/L5`, and verify read nothing. The Allclean check also flagged `system/controlDict` (endTime left changed) |
| [36308186478](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/36308186478) | 927881e | final post-processing only (the base and sensitivity runs came from the state), Allclean, verify | 12/12 PASS; these files |

- **Unchanged inputs**: the solver, the case and the base-run numerics are identical in all three commits. The
  later commits change only `runLong.sh`, `results.py` (the crash scan, see below), `Allclean` and the workflow.
- **Bars**: committed in 1c92912, before any L5 run.
- **Paths**: the `value source` paths in `results.csv` and `STATUS.md` were rewritten from `out/L5/` (the job's
  output directory) to `results/L5/`. `STATUS.md` was then regenerated with `tools/verify.py L5 results/L5`; the
  values are unchanged.
- **Logs**: each `log.*.trimmed` keeps the first 200 and last 100 lines, prefixed with their original line numbers.
  The sensitivity run's logs are in the state artifact (retained 14 days), not here. They were scanned by the crash
  check (L5.2).
- **Crash scan (L5.2)**: it skips OpenFOAM's start-up banner `trapFpe: Floating point exception trapping enabled`,
  which is printed at the top of every log and reports a setting, not a crash. Without the skip, those 11 banner
  lines would count as crashes. Any other `Floating point exception` line still counts.

## Files

| file | content |
|---|---|
| `per_cycle.csv` | base run, cycles 1-40: T_joint mean, <H> at the three stations, dp and face phasors, piston work, HX heat terms, B5 closure, piston phasors |
| `per_cycle_sensitivity.csv` | sensitivity run (dt/2, matrix dx/2), cycles 41-45, same columns |
| `final_cycle_faces.csv` | cycle 40, every step: t, p, u_superficial, mdot, Tg at both matrix faces |
| `profiles.csv` | cycle 40: cycle-mean Tg(z) and Ts(z) at the 121 nodes |
| `piston_check.csv` | realised piston volume-flow phasors against the parameter file |
| `results.csv`, `STATUS.md` | metrics and the verify table |

## Notes on the values

- **Periodic state**: B6 was checked every 10 cycles, and 40 cycles was the first check at which it held. It in fact
  held from cycle 20, but the parameter file requires at least 40 cycles. Over cycles 35-40:
  - joint T drift: at most 0.0015 K per cycle;
  - matrix <H> drift: at most 0.016 % per cycle.
- **Energy closure (B5)**: 0.020 W, against a bar of 0.15 W. In the last cycle:
  - piston work: 14.256 W (hot), -3.726 W (cold);
  - heat into the gas from the HX: -12.856 W (hot; heat rejected), +1.929 W (cold; heat lifted);
  - HX solid to the matrix solid: +0.476 W (hot), -0.059 W (cold).
- **Pistons**: both realise the specified volume flow within 1.3e-6 in amplitude. Both lag the spec by 0.075 deg,
  which is half a time step (360/2400/2): the phase error of the backward-Euler mesh flux.
- **Sensitivity** (dt/2 and matrix dx/2, cycle 45 against cycle 40):
  - amplitudes: |p| +0.050 % (hot) and -0.020 % (cold); |mdot| -0.011 % and -0.001 %; dp +0.40 %;
  - phases: at most 0.033 deg.
  - Not a bar quantity but worth stating: the hot-face <H> moves from 1.863 to 1.797 W (-3.5 %). Part of that is
    the 5-cycle run still drifting (it falls by 0.011 and then 0.003 W per cycle over cycles 43-45), so B3 comparisons should allow
    for a resolution effect of this size.
- **Context against DeltaEC** (not a bar; a different model class):
  - face |p|: -3.0 % (hot), +2.7 % (cold);
  - face |mdot|: -2.2 % and +1.2 %;
  - mdot phases: 25.60 against 25.54 deg (hot), -28.78 against -28.61 deg (cold);
  - <H>: 1.82-1.86 against 1.8275 W;
  - T_joint: 27.87 against 28.04 K.
  - The dp amplitude is 23 % below DeltaEC (11.3 against 14.7 kPa). This was not investigated. The model here takes
    the file's drag verbatim: Darcy plus C2 fixed at Re_ref. DeltaEC uses the Gedeon-Wood friction factor at the
    local instantaneous Re, so a difference of this kind is expected. The code-to-code bar B2 is against the Fluent
    twin, which uses the same drag.
