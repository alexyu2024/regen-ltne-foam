## How this was produced

- **Run**: GitHub Actions `run-case`, input `level = L6`, one job:
  [36565303378](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/36565303378) at 6c4115f, 2026-09-29,
  31 min wall time. It ran G1, G2, G3 and T2 in parallel.
- **Bars**: committed in b7062cc, before any L6 run. The local debugging runs (G1 10 cycles, G3 and T2 2 cycles
  each) came after that commit and are not part of these results.
- **Job conclusion**: "failure" only because `verify.py` exits non-zero on the four FAIL rows below. The runs, the
  post-processing and the Allclean check all completed.
- **Paths**: the `value source` paths were rewritten from `out/L6/` to `results/L6/`, and `STATUS.md` was
  regenerated with `tools/verify.py L6 results/L6`. The values are unchanged.
- **Logs**: each `*.trimmed` log keeps the first 200 and last 100 lines, prefixed with their original line numbers.
  `<run>_log.*` files are the per-run solver and meshing logs; `log.<run>` is the driver output.
- **Check that G2 is the L5 run**: G2 reproduces the L5 base run. On cycle 40, H_hot is 1.862699819 W against
  1.862699819 W in `results/L5`, and the closures agree to 1e-9 W.

## Result: 17/21 PASS as preregistered

| check | G1 (coarse) | G2 (medium) | G3 (fine) | T2 (G2, dt/2) |
|---|---|---|---|---|
| cycles to the periodic criterion | 70 | 40 | 40 | 40 |
| H_hot, W | 1.98920 | 1.86270 | 1.82399 | 1.85924 |
| H_joint, W | 1.82477 | 1.82416 | 1.82418 | 1.82436 |
| H_cold, W | 1.84872 | 1.85450 | 1.85375 | 1.85779 |
| Qgs_abs, W | 373.555 | 373.969 | 374.460 | 374.192 |
| dp_amp, Pa | 11264.9 | 11313.5 | 11345.2 | 11314.1 |

| QoI | e32/e21 | apparent order p | GCI_fine | order check \|p - 2\| <= 0.5 | dt/2 change |
|---|---|---|---|---|---|
| H_hot | 3.27 | 1.71 | 1.17 % | PASS | 0.19 % |
| H_joint | -25.1 (oscillatory) | 4.65 | 0.00007 % | **FAIL** | 0.011 % |
| H_cold | -7.67 (oscillatory) | 2.94 | 0.0076 % | **FAIL** | 0.18 % |
| Qgs_abs | 0.85 | 0.24 | 0.90 % | **FAIL** | 0.060 % |
| dp_amp | 1.53 | 0.62 | 0.66 % | **FAIL** | 0.0052 % |

**What passes**:
- periodicity on all four runs;
- GCI_fine below 3 % for all five QoIs (the largest is H_hot, 1.2 %);
- the time step: every QoI moves by less than 0.2 % at dt/2;
- no crashes, and Allclean leaves nothing behind.

**What fails**: the apparent order is outside 2 ± 0.5 for four of the five QoIs. By QoI:
- **H_joint and H_cold**: convergence is oscillatory (e32/e21 < 0), and the grid differences are at the level of
  the periodic residual.
  - H_joint: the relative G3-G2 difference is 1.3e-5.
  - H_cold: it is 4.1e-4.
  - The largest cycle-to-cycle change over the last 5 cycles was 1.6e-4 (H_joint) and 3.1e-4 (H_cold) on G2, and
    4.5e-5 and 1.2e-4 on G3.
  - With differences this small, the apparent order measures the residual drift, not the discretisation error, so it
    has no meaning here. The GCI itself is tiny.
- **dp_amp and Qgs_abs**: convergence is monotone, and the differences (0.1-0.4 %) are well above the drift
  (3e-5).
  - dp_amp converges at about first order (p = 0.62). Qgs_abs barely converges (p = 0.24): its G1-G2 and G2-G3
    differences are almost equal (0.41 and 0.49 W).
  - This was not isolated by a separate test. Two likely causes:
    - porosity, drag and area-to-volume ratio change by a step at the three zone interfaces (hot HX/500#, 500#/635#,
      635#/cold HX), where the face interpolation is locally first order, and the `limitedLinear` limiter drops to
      first order at extrema;
    - for Qgs_abs, the unresolved solid layer at the HX/matrix interfaces (next section), which adds a contribution
      that changes with the first cell's size.
  - The formal order 2 is therefore not reached for these two QoIs on these grids, although their GCI_fine is below
    1 %.

## Energy ledger (four-term and six-term closure)

Last cycle of each run, W. Per-cycle values are in `per_cycle_<run>.csv`, columns `closure4` and `closure`
(six-term).

| run | four-term (registered L5.7 form) | six-term (L5.7a form) | HX solid -> matrix solid, hot | HX solid -> matrix solid, cold | net matrix gas-solid exchange Qgs_net |
|---|---|---|---|---|---|
| G1 | -0.110 | 0.175 | 0.319 | -0.034 | 0.145 |
| G2 | -0.397 | 0.020 | 0.476 | -0.059 | 0.404 |
| G3 | -0.584 | -0.027 | 0.662 | -0.105 | 0.583 |
| T2 | -0.407 | 0.008 | 0.474 | -0.059 | 0.400 |

**What the four-term form omits, physically.** Each HX solid is held at a fixed temperature, so it is the model's
heat source or sink, and heat leaves it by two paths:
1. **Convection to the gas inside the HX**, hA (Ts - T). Both forms count this.
2. **Axial conduction from the HX solid into the adjacent matrix solid** across the HX/matrix interface, with
   k_eff = ksFrac (1 - eps) k_ss on the matrix side. Only the six-term form counts this.

That conducted heat does not stay in the matrix solid: in a periodic state the matrix solid stores nothing over a
cycle, so the matrix passes it on to the gas. Qgs_net is almost exactly the sum of the two interface terms (0.404 W
against 0.476 - 0.059 = 0.417 W on G2). It therefore reaches the gas, and the pistons' and HXs' balance, inside the
matrix instead of inside the HX. The four-term closure leaves out a real heat input and misses by about that
amount.

**New finding: the omitted term is not grid-converged.**
- The HX-solid to matrix-solid conduction grows with refinement: 0.319, 0.476 and 0.662 W (hot end) on G1, G2 and
  G3.
- The solid-side thermal layer where the matrix solid adjusts from the fixed HX temperature has a thickness of about
  delta = sqrt(k_eff / hA): 3.0e-5 m at the hot face (k_eff 0.30 W/m/K, hA 3.3e8 W/m3/K) and 1.6e-5 m at the cold
  face.
- The matrix cells are 217-867 um, so no grid resolves the layer, and the interface conduction, discretised as kSf
  deltaCoeff (Ts,HX - Ts,cell), keeps rising as the first cell shrinks.
- Consequences:
  - the four-term closure drifts with refinement (-0.11, -0.40, -0.58 W);
  - H_hot, whose face at z = 0 is the hot HX/matrix interface and includes this conduction, carries the largest GCI
    (1.2 %);
  - the six-term closure stays near zero on G2 and G3 (0.020 and -0.027 W) because it books the term consistently.
    On G1 it is 0.175 W.
- This is a property of the model as specified: a fixed-temperature HX solid in direct conductive contact with the
  matrix solid. It is not a solver defect, but the interface conduction should not be read as a converged physical
  quantity. The L5.7 bar is unchanged.
