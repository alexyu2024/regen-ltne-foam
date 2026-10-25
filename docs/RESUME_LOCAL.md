# Resuming the L5P acceleration runs off-cloud

Kept current on branch `pss/accel`. Last update: 2026-10-25.

## Rules (leader-gen58, 2026-10-25)

- One configuration at a time.
- Before each run, write and push a dated registration file in `docs/L5P_accel/` with its criteria fixed. Never
  change a criterion after seeing results.
- Natural marching (4195 cycles) stays the reference.
- Nothing from `pss/*` is merged into main. No tag, release or DOI.

## Queue

| id | configuration | registration | status |
|---|---|---|---|
| X1 | Graves-Morris m = 3, total budget 1280 (`L5P_BUDGET=1240`) | `docs/L5P_accel/2026-10-25_gm3_b1280.md` | **running** (started 2026-10-25 in the cloud container) |
| X2 | Newton-Picard with a larger subspace: p = 6-10, or several subspace iterations per Newton step | to be written if X1 fails | pending |
| X3 | BRR with a trust region instead of the 2 K cap | to be written if X2 fails | pending |

The next pending configuration is the first row not marked done. Results go to `results/L5P/accel/<id>_<name>/`.

## Setup (Ubuntu 22.04/24.04, about 30 min)

    git clone --branch pss/accel https://github.com/alexyu2024/regen-ltne-foam && cd regen-ltne-foam
    sudo tools/install.sh                              # openfoam2512-dev=2512.0-2 and src/Allwmake
    sudo apt-get install -y python3-numpy python3-yaml
    source /usr/lib/openfoam/openfoam2512/etc/bashrc   # in every shell
    cd cases/L5P_periodicState
    L5P_RUN=run_c40 ./runNatural.sh /tmp/c40 40 40     # start state, 40 cycles, about 8 min

Build check: in `/tmp/c40/per_cycle.csv`, the cycle-40 `Tjoint_mean` must be within 1e-5 K of 27.865715 K. Every
number in this study was produced on 2512.0-2; another OpenFOAM version is not bit for bit comparable.

## Running a configuration (X1 as the example)

From `cases/L5P_periodicState` with OpenFOAM sourced:

    O=../../results/L5P/accel/X1_gm3_b1280
    mkdir -p $O && cp ../../results/L5P/reference.json $O/
    L5P_BUDGET=1240 L5P_WORKERS=1 python3 -m pss.study method gm3 run_c40 /tmp/accel_work/X1 $O > $O/gm3_run.log 2>&1
    python3 -m pss.study score $O gm3              # writes E, D, NR, M, passed into gm3_summary.json

Inputs:
- the cycle-40 state `run_c40/`;
- `reference.json`: accepted reference at cycle 4900, with tolerances, drift tolerances and r_A2 = 0.998813;
- the method name, which fixes the method and its parameter (`gm3`: Graves-Morris, m = 3);
- `L5P_BUDGET`: cycles allowed after cycle 40. The total is 40 + used. Stopping with status "budget" is a FAIL.
- `L5P_WORKERS`: cycles run at the same time. Graves-Morris and BRR use 1; Newton-Picard p uses p + 1.

Time: 9-15 s per cycle per core, so X1 takes about 3.5-5 h.

**Restarts**: the method runs have no restart point. The map is deterministic, so rerun the configuration from
`run_c40`; it repeats bit for bit. Count the cycles of the lost attempt in the honest total, and say so in the
results. `<O>/gm3_evals.csv` is rewritten after every evaluation, so a lost run leaves its evaluations on disk for
the count.

**Checks**:
- The first 600 cycles of X1 must equal `results/L5P/methods/gm3_evals.csv` bit for bit (same method, same start).
- Run `python3 -m pss.selftest` (seconds, no solver) after any change to `pss/methods.py`.

## Adding the next configuration

1. Copy the X1 registration to `docs/L5P_accel/<date>_<name>.md` and fix in it, before running: the method and its
   parameters, budget, stop rule, verification, reference, and pass rule. Commit and push.
2. For X2 and X3 the method code needs a new variant in `pss/methods.py`, plus its name in `study.method`'s
   dispatch table (`kind` comes from the name's letters, `par` from its digits). Examples: `npk` for p with k
   subspace iterations, or `brt` for BRR with a trust region. Commit the code together with the registration,
   before the run.
3. Run as above and score. Commit `results/L5P/accel/<id>_<name>/` and update the queue table here.

## Where things are

| what | where |
|---|---|
| registered criteria and amendments A1, A2 | `docs/VERIFICATION.md`, section L5P |
| the seven L5P runs and their conclusion | `results/L5P/methods/`, `docs/L5P_CONCLUSION.md` |
| natural reference, restart point at cycle 4900 | `results/L5P/natural/`, `results/L5P/natural/restart/state.tgz` |
| moving the tool to its own repository | `docs/pr/MOVE_OUT.md` |
