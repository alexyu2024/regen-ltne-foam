# Moving the periodic-state tool (L5P) to its own public repository

Decision by leader-gen58 on 2026-10-25: the periodic-steady-state work is released as a separate tool, not in the
solver's v1.1. Nothing on main is reverted here. This page lists what to take, and how to build and run it against
a released solver tag.

## Commits on main that came from PR 1 (`pss/driver-natural-ref`)

- **Range**: 70 commits, from `0314bd5` (2026-10-23) to `eab2432` (main's head on 2026-10-25). They sit on top of
  `fab56a3`, the v1.0.2 release (tag `v1.0.2`).
- **List**: `git log --reverse --oneline fab56a3..eab2432 --not 95b6665`
- **Excluded**: real-gas PR #19 (`262dc66`, `8ecb990`, merge `95b6665`). It came in through `be728cc`, the merge of
  main into PR 1, which is counted in the 70.
- **Landmarks**:

  | commit | what |
  |---|---|
  | `0314bd5` | per-cycle tables and natural reference driver |
  | `b2984ed` | L5P criteria registered before any run was read |
  | `51a573d` | map driver, methods (a)-(c), self-test; Amendment A1 |
  | `5d4b62a` | design page; python3-numpy in install.sh and Dockerfile |
  | `7672a59` | Amendment A2 |
  | `e0e2799` | A2 implemented |
  | `57fa5d1` | `pss/runall.py` |
  | `462de28` | reference accepted under A2 at cycle 4900 |
  | `be728cc` | merge of main (PR #19) |
  | `3e5d0e2` | `results.csv` and STATUS |
  | `eab2432` | results README and PR draft |

  The rest are the 49 "natural reference: tables at cycle N" commits and the acceptance checks at 2400-4000.

## Files and directories from PR 1

| path | what | moves? |
|---|---|---|
| `cases/L5P_periodicState/` (`pss/*.py`, `runNatural.sh`, `Allclean`, `README.md`) | the driver, map, methods, study scripts | yes: the core of the tool |
| `docs/L5P_PERIODIC_STATE.md` | design | yes |
| `docs/VERIFICATION.md`, section "L5P" with Amendments A1 and A2 (from line 515) | registered criteria | copy the section; the rest of the file stays with the solver |
| `docs/pr/pss-driver-natural-ref.md` | PR 1 draft | yes (history) |
| `results/L5P/` (`natural/` with 57 files, `reference*.json`, `natural_distance*.csv`, `natural_decay_c2400.csv`, `noise*.*`, `results.csv`, `STATUS.md`, `README.md`, `log.allclean-check`) | natural reference to cycle 4900 and its acceptance | yes |
| `tools/install.sh`, `docker/Dockerfile` | one change each: `python3-numpy` | no: keep in the solver (harmless); the tool's own README states the numpy dependency |
| `.gitignore` | `run_*/` and case logs under `cases/L5P_periodicState` | copy those lines |

Not on main but part of the tool: branches `pss/method-a`, `pss/methods-bc` and `pss/conclusion` (method results
under `results/L5P/methods/`, `docs/L5P_CONCLUSION.md`, the PR 2-4 drafts), and `pss/accel` (the
one-configuration-at-a-time runs after 2026-10-25, `docs/L5P_accel/`, `results/L5P/accel/`, `docs/RESUME_LOCAL.md`).
Take these from `pss/accel`, which contains all of them.

To keep the history, filter a clone of `pss/accel`:

    git clone --branch pss/accel https://github.com/alexyu2024/regen-ltne-foam pss-tool && cd pss-tool
    git filter-repo --path cases/L5P_periodicState --path results/L5P --path docs/L5P_PERIODIC_STATE.md \
        --path docs/L5P_CONCLUSION.md --path docs/L5P_accel --path docs/RESUME_LOCAL.md \
        --path docs/pr/pss-driver-natural-ref.md --path docs/pr/pss-method-a.md --path docs/pr/pss-methods-bc.md \
        --path docs/pr/pss-conclusion.md --path docs/pr/MOVE_OUT.md
    # then add the VERIFICATION.md L5P section as docs/CRITERIA.md

## What the driver depends on in the solver

- **Solver version**: `ltneFoam` of **v1.0.2** (`fab56a3`).
  - The natural reference (cycles 0-4900), the start state, the noise tests and the registration were all run
    with this source.
  - The method runs used main after PR #19 (`be728cc`). That code adds the optional real-gas library and two
    monitor lines. One cycle from cycle 40 was bit for bit identical to the v1.0.2 binary, so either works. The
    tag to build against is `v1.0.2`, or any later release whose L5 ideal-gas path is unchanged; check this with
    the cycle-40 test below.
- **OpenFOAM**: `openfoam2512-dev` 2512.0-2 (the solver's `tools/install.sh`). Results are bit-reproducible only on
  this package.
- **The L5 case** `cases/L5_regenSlice`, read unchanged:
  - `params_L5.yaml`, read by `pss/case.py` for geometry, porosity, frequency and gas;
  - `mkCase.py`, `system/{controlDict,fvSchemes,fvSolution}`, `Allrun.continue`, used by `runNatural.sh`;
  - `results.py`, which folds the face and HX monitors into per-cycle quantities (`pss/cycles.py`).
- **Solver tools**: `tools/resultslib.py` (used by `pss/final.py`) and `tools/verify.py` (reads bars from
  `docs/VERIFICATION.md`).
- **Python**: python3, numpy, PyYAML.
- **Paths to change when moving**:
  - `pss/case.py` line 16 finds the L5 case at `../../L5_regenSlice`, and `runNatural.sh` uses
    `L5=../L5_regenSlice`.
  - `pss/final.py` imports `../../../tools/resultslib.py`.
  - In the standalone repository, replace these three with one variable pointing at a solver checkout, for
    example `REGEN_LTNE_FOAM=/path/to/regen-ltne-foam`. Then `L5=$REGEN_LTNE_FOAM/cases/L5_regenSlice`, and copy
    or import `resultslib.py` and `verify.py`. No other code reads solver files.

## Build and run against the released solver

    # 1. solver at the release tag (Ubuntu 22.04/24.04)
    git clone --branch v1.0.2 https://github.com/alexyu2024/regen-ltne-foam
    cd regen-ltne-foam && sudo tools/install.sh        # openfoam2512-dev=2512.0-2, then src/Allwmake
    sudo apt-get install -y python3-numpy
    source /usr/lib/openfoam/openfoam2512/etc/bashrc  # every shell; puts ltneFoam on PATH
    export REGEN_LTNE_FOAM=$PWD

    # 2. the tool
    git clone <new tool repository> pss-tool && cd pss-tool/cases/L5P_periodicState

    # 3. build check: cycle-40 T_joint must be 27.865715 K within 1e-5 K (L5P.1)
    L5P_RUN=run_c40 ./runNatural.sh /tmp/c40 40 40
    python3 -c "import csv;r=[x for x in csv.DictReader(open('/tmp/c40/per_cycle.csv')) if int(float(x['cycle']))==40][0];print(abs(float(r['Tjoint_mean'])-27.865715))"

    # 4. a method from cycle 40, scored against the published reference
    mkdir -p out && cp ../../results/L5P/reference.json out/
    python3 -m pss.study method gm3 run_c40 work out
    python3 -m pss.study score out gm3

    # 5. natural reference (about 4900 cycles, 9-15 s each on one core); resumes from out/restart/state.tgz
    ./runNatural.sh nat 4900 100 && python3 -m pss.study reference nat out

Without a tool repository yet, run steps 3-5 directly in `cases/L5P_periodicState` of a `pss/accel` checkout after
building the solver from the same checkout (`sudo tools/install.sh`).

## Citation

Credit as in the solver's `CITATION.cff` (Qiming Yu, University of Southampton). The new repository gets its own
`CITATION.cff` with the same author, and a reference to the solver (DOI 10.5281/zenodo.23499221, v1.0.2). No DOI
is minted and nothing is tagged or released by this session.
