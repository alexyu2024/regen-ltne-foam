# L2 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L2.1 v1_final_time | == 0.05 (docs/VERIFICATION.md:118) | 0.05 | PASS | results/L2/v1.log.ltneFoam:71277 |
| L2.2 v2_final_time | == 0.05 (docs/VERIFICATION.md:119) | 0.05 | PASS | results/L2/v2.log.ltneFoam:71277 |
| L2.3 v3_final_time | == 0.05 (docs/VERIFICATION.md:120) | 0.05 | PASS | results/L2/v3.log.ltneFoam:71277 |
| L2.4 v4_final_time | == 0.05 (docs/VERIFICATION.md:121) | 0.05 | PASS | results/L2/v4.log.ltneFoam:71277 |
| L2.5 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:122) | 0 | PASS | results/L2/log.*:all lines of all logs |
| L2.6 v1_rel_err | <= 0.01 (docs/VERIFICATION.md:123) | 0.02244065202199519 | FAIL | results/L2/v1.inletP.dat:105 with v1.outletP.dat:105, v1.inletFlux.dat:105, v1.porousRho.dat:104 |
| L2.7 v2_rel_err | <= 0.01 (docs/VERIFICATION.md:124) | 0.02282258515027824 | FAIL | results/L2/v2.inletP.dat:105 with v2.outletP.dat:105, v2.inletFlux.dat:105, v2.porousRho.dat:104 |
| L2.8 v3_rel_err | <= 0.01 (docs/VERIFICATION.md:125) | 0.026903305392853905 | FAIL | results/L2/v3.inletP.dat:105 with v3.outletP.dat:105, v3.inletFlux.dat:105, v3.porousRho.dat:104 |
| L2.9 v4_rel_err | <= 0.01 (docs/VERIFICATION.md:126) | 0.036529972112332776 | FAIL | results/L2/v4.inletP.dat:105 with v4.outletP.dat:105, v4.inletFlux.dat:105, v4.porousRho.dat:104 |
| L2.10 v1_ratio | <= 0.1 (docs/VERIFICATION.md:127) | 0.008063681598723617 | PASS | results/L2/v1.porousRho.dat:104 with v1.inletFlux.dat:105 |
| L2.11 v4_ratio | >= 1 (docs/VERIFICATION.md:128) | 8.07772973645226 | PASS | results/L2/v4.porousRho.dat:104 with v4.inletFlux.dat:105 |
| L2.12 v2_ratio | report (docs/VERIFICATION.md:129) | 0.08063696962359296 | REPORT (> 0) | results/L2/v2.porousRho.dat:104 with v2.inletFlux.dat:105 |
| L2.13 v3_ratio | report (docs/VERIFICATION.md:130) | 0.8063962094585426 | REPORT (> 0) | results/L2/v3.porousRho.dat:104 with v3.inletFlux.dat:105 |
| L2.14 v1_steady | <= 1e-3 (docs/VERIFICATION.md:131) | 2.549699940002147e-06 | PASS | results/L2/v1.inletP.dat:95,105 with v1.outletP.dat:95,105 |
| L2.15 v2_steady | <= 1e-3 (docs/VERIFICATION.md:132) | 1.1896969395084235e-06 | PASS | results/L2/v2.inletP.dat:95,105 with v2.outletP.dat:95,105 |
| L2.16 v3_steady | <= 1e-3 (docs/VERIFICATION.md:133) | 1.8581553055548573e-07 | PASS | results/L2/v3.inletP.dat:95,105 with v3.outletP.dat:95,105 |
| L2.17 v4_steady | <= 1e-3 (docs/VERIFICATION.md:134) | 0.0002231023825906778 | PASS | results/L2/v4.inletP.dat:95,105 with v4.outletP.dat:95,105 |
| L2.18 v1_dp | report (docs/VERIFICATION.md:135) | 0.39220599993132055 | REPORT (> 0) | results/L2/v1.inletP.dat:105 minus v1.outletP.dat:105 |
| L2.19 v4_dp | report (docs/VERIFICATION.md:136) | 3484.6916070000734 | REPORT (> 0) | results/L2/v4.inletP.dat:105 minus v4.outletP.dat:105 |
| L2.20 allclean_leftover | == 0 (docs/VERIFICATION.md:137) | 0 | PASS | results/L2/log.allclean-check:empty file |

12/16 PASS
## Result: L2 FAILS (bars L2.6 to L2.9)

The pressure drop is 2.2 % (Darcy regime) to 3.7 % (Forchheimer regime) below the closed form on the specified mesh
(1 mm cells, 20 cells in the plug). The run itself is sound:
- all runs reach endTime with no FATAL/nan/inf (L2.1 to L2.5);
- the flow is steady (L2.14 to L2.17: at most 2.2e-4);
- the runs span both regimes (Forchheimer / Darcy ratio 0.0081 to 8.1).

## Diagnosis

Experiments separating the hypotheses, one factor at a time; all diagnostic runs are v1 or v4 run to t = 0.02 s.

1. **Mesh refinement only** (`cases/L2_porousPlug/Allrun.refine`, output `refine/log.refine`, sources
   `refine/*.dat`, last row). The error halves with each halving of dx:

   | cells in plug | v1 (Darcy) | v4 (Forchheimer) |
   |---|---|---|
   | 20 | -0.02238 | -0.03744 |
   | 40 | -0.01082 | -0.01862 |
   | 80 | -0.00493 | -0.00943 |

   - The error is first order in dx: a constant deficit of about 0.45 cells of plug length (Darcy) and 0.75 cells
     (Forchheimer).
   - First-order Richardson extrapolation of the two finest meshes gives +0.10 % (v1) and -0.02 % (v4): the solver
     converges to the closed form.
   - The coefficients (d, f), the viscosity and the ESI source (mu d + 0.5 f rho |U|, checked in
     `DarcyForchheimerTemplates.C`) are therefore right; the deficit comes from the plug edges.
2. **Location.** Cell-centred velocity in the final field of v4 at 1 mm, t = 0.02 s (diagnostic run, not stored):
   - it is 0.759 u in the first and last plug cells, while the face mass flux is uniform;
   - the open cells next to the plug show odd-even ripples of 0.57 to 1.50 u.

   The drag in the two edge cells is computed with this low cell velocity. That accounts for 2 x (1 - 0.759) = 0.48
   cells (Darcy) and 2 x (1 - 0.759^2) = 0.85 cells (Forchheimer) of missing plug length, matching item 1. This is the
   collocated (Rhie-Chow) pressure-velocity coupling at a step change of the momentum-equation diagonal.
3. **Harmonic instead of linear interpolation of rho/A at faces** (fvSchemes only): v4 moves from -3.74 % to -3.70 %.
   Not the cause.
4. **Cell velocity rebuilt from face fluxes** after the pressure correction (`U = reconstruct(phi)/rho`, a trial
   code change, reverted): the edge-cell velocity becomes u and the ripples vanish. The error drops to -0.43 % (v1)
   and -2.41 % (v4), so a face-level part of the interface error remains. This is not a one-line fix; it was not kept.

Consequence for L5: the error scales as (0.45 to 0.75) dx / L_plug per plug end pair. It shrinks with the number of
cells across the matrix, but a porous-to-open interface exists at both ends of every regenerator.
