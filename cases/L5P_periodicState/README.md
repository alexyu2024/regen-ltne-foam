# L5P periodic steady state of the L5 slice by cycle-map acceleration

The L5 case (`cases/L5_regenSlice`, unchanged), driven one cycle at a time: x_(k+1) = Phi(x_k). Three black-box
methods use the map to reach the periodic state in fewer cycles than natural marching. They are compared with a long
natural reference run, with every cycle counted.
- Criteria, committed before any run was read: `docs/VERIFICATION.md`, L5P (and its Amendment A1).
- Design: `docs/L5P_PERIODIC_STATE.md`.

| command | what it does |
|---|---|
| `./runNatural.sh <outdir> <cycles> [chunk]` | natural run from t = 0 (or from `<outdir>/restart/state.tgz`); per-cycle tables after every chunk, restart point every 200 cycles |
| `L5P_RUN=run_c40 ./runNatural.sh <dir> 40 40` | the common start state of the methods (cycle 40) in `run_c40/` |
| `python3 -m pss.study noise run_c40 work <out>` | noise tests N1-N4 of the map |
| `python3 -m pss.study method <np1\|np2\|np3\|brr3\|brr6\|gm0\|gm3> run_c40 work <out>` | one method from cycle 40, with its verification cycles |
| `python3 -m pss.study reference <out>/natural <out>` | reference acceptance (L5P.3) and the natural count |
| `python3 -m pss.study score <out> <methods...>` | scores finished methods against the reference |
| `python3 -m pss.final <out>` | `results.csv` for `tools/verify.py L5P <out>` |
| `python3 -m pss.selftest` | the methods on a synthetic map (no solver, seconds) |
| `./Allclean` | removes run directories, work and logs |

Run the Python commands from this directory with OpenFOAM sourced (`L5P_WORKERS`, default 3, is the number of
cycles run at the same time). `pss/` holds the field I/O (`foamio.py`), the state vector and the registered
quantities (`case.py`, `cycles.py`), the map (`cyclemap.py`) and the methods (`methods.py`).
