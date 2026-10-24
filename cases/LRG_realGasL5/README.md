# LRG: real- against ideal-gas helium on the L5 slice

The definition, charge basis and bars are in `docs/VERIFICATION.md`, LRG, committed before any LRG run.

- **Ideal-gas side**: the accepted L5P natural reference; no new ideal-gas run.
- **Real-gas side**: the same L5 case continued from the reference with only the gas model switched
  (`mkCase.py --gas real` files, `src/ltneRealGas`).
- **Charge basis**: equal initial mean pressure. p and T at the switch are the reference's, so the inventory
  differs; the difference is reported.

| command | what it does |
|---|---|
| `./runLong.sh <outdir> [minutes]` | the whole LRG run, resumable across jobs (exit code 3 = time budget used) |
| `./Allclean` | removes the fetched tools, the run directories and logs |

On GitHub: `.github/workflows/run-case.yml` with `level = LRG`.

## What `runLong.sh` does

1. **Fetch the L5P inputs.** At the commits pinned in `source.env`, from the L5P branch, it fetches:
   - the L5P tools (`cases/L5P_periodicState/pss`, placed in `pss/` here, not tracked);
   - the reference tables and json;
   - the restart point N_R, the latest L5P restart point before N_REF.
2. **Ideal gas from N_R to N_REF.** It checks every L5P quantity against the reference tables (LRG.1).
3. **Switch.** It copies the N_REF state and replaces the gas files with those `mkCase.py --gas real` writes:
   `thermophysicalProperties`, the table, `enthalpyReferenceCp` in `ltneProperties`, and `libs (ltneRealGas)`.
   Any other difference in `ltneProperties` stops the run. It removes `rho` and records the inventory difference
   (`switch.json`).
4. **Real gas.** It runs in 100-cycle chunks. From N_REF + 400 it applies the L5P Amendment A2 test after every
   chunk (`lrg.py accept`, the L5P `study.reference` on this run's own tables), up to the cap N_REF + 6000.
5. **Deliverables.** `lrg.py final` writes them.

`lrg.py` uses the L5P tools unchanged except for the gas mass of a real-gas run: sum eps rho V with the solver's
`rho`, which it writes at every cycle boundary.

## Dry run of the pipeline (2026-10-24; not an LRG result)

The dry run used the L5P restart point at cycle 3800 (commit 5190caf), N_REF = 3802, 2 ideal cycles and 4 real-gas
cycles. The `LRG_SOURCE_ENV` and `LRG_ALLOW_UNACCEPTED` overrides exist for such dry runs only.
- **Restart check**: the ideal-gas continuation reproduced the L5P reference tables to 5.3e-15 (relative, over all
  quantities and both cycles).
- **Switch**: at cycle 3802 the state was 22.0-84.4 K and 0.797-0.808 MPa, inside the table.
  - The reference's mean pressure there is 0.8026 MPa, not the nominal 0.75 MPa; the sealed column settled there.
  - The inventory difference real/ideal - 1 at equal pressure was -0.72 %.
- **Real-gas run**: mass conserved to 1.4e-11 over 4 cycles.
