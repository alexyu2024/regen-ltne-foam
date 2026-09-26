# Design note: face-consistent Darcy-Forchheimer drag (fix for the L2 FAIL, PR #4)

Committed before any code for the fix was written.

## Problem (measured in PR #4, `results/L2_run1/README.md`)

The drag comes from `explicitPorositySource`. It adds mu d + 0.5 f rho |U| to the cell diagonal of the momentum
matrix, so the Rhie-Chow face flux interpolates 1/A and H/A across the porous/open step. The resulting pressure
field puts almost no drop across the interface faces, and the edge cells see a cell velocity of 0.76 u. The drop
through a 20-cell plug is 0.45 (Darcy) to 0.75 (Forchheimer) cells short, which is O(dx).

## Change (buoyantPimpleFoam pattern: the force is balanced on faces, then reconstructed to cells)

Let `UEqn0` be the momentum matrix without the drag, with rAU0 = 1/A0 and HbyA0 = H0/A0. The drag coefficient is

    cells: Dc = mu D + 0.5 F rho |U|
    faces: Df = interpolate(mu D) + 0.5 interpolate(F) |phi| / |Sf|

where rho |u| on a face is the face mass flux, so no cell velocity enters the face drag. The face momentum balance
A0 (u_f - HbyA0_f) = -grad_f p - Df u_f gives u_f = kf (HbyA0_f - rAU0_f grad_f p), with kf = 1 / (1 + rAU0_f Df).
Hence:

    phiHbyA = kf (interpolate(rho) flux(HbyA0) + interpolate(rho rAU0) ddtCorr)
    rhorAUf = kf interpolate(rho rAU0)
    U       = kc (HbyA0 - rAU0 grad p),   kc = 1 / (1 + rAU0 Dc)      (cell reconstruction)
    predictor: solve(UEqn0 + fvm::Sp(Dc, U) == -grad p)

Terms that move to faces: the Darcy and Forchheimer resistances in the flux (phiHbyA, rhorAUf). The cell drag
remains only in the momentum predictor and in the cell velocity reconstruction.

On a uniform mesh, linear interpolation gives Df = D/2 on the two interface faces and D on the 19 interior faces.
The summed face drop is therefore 20 cells x dx = L exactly, for both terms.

Inputs: unchanged. ltneFoam reads the `explicitPorositySource` / `DarcyForchheimer` entries of `constant/fvOptions`
(cellZone, d, f) into cell fields D and F and no longer passes `fvOptions(rho, U)` to the momentum equation. Other
momentum fvOptions stop with a fatal error instead of being silently dropped. Only isotropic d and f are accepted
(fatal error otherwise); anisotropy is left for L5 if it needs it. The transonic pressure branch is removed (fatal
error if requested). No case uses it.

Without porous zones, D = F = 0, so kf = kc = 1 exactly and the algorithm is the previous one. L0 and L1 must be
unchanged; CI re-runs both.

## Expected effect on the L2 rows (unchanged case, unchanged bars)

| rows | before (PR #4) | expected after |
|---|---|---|
| L2.1-L2.5 runs complete, no nan | PASS | PASS |
| L2.6-L2.9 rel_err | 0.022-0.037 (FAIL) | below 1e-3 each (PASS). Remaining terms: the density variation along the plug (dp/p <= 1.8e-3, entering at second order), the open-region momentum-flux and viscous terms (< 1e-5) and solver tolerance |
| L2.10, L2.11 regime ratios | 0.0081, 8.08 | unchanged to 3 digits (G and rho_p unchanged) |
| L2.14-L2.17 steady | <= 2.2e-4 | still <= 1e-3 |
| L2.20 allclean | PASS | PASS |

If the 1 mm case still misses 1 %, it is reported as FAIL again, with the error split between the edge faces and the
interior faces. The bars do not move.

## Revision 2 (after the first implementation missed; committed before the recorded run)

First implementation, exactly as above. L2 re-run unchanged; diagnostic copy in scratch, not stored:
- rel_err 0.026 to 0.039, **worse** than before (0.022 to 0.037);
- L0 and L1 unchanged: 8/8 and 15/15.

Cause, from the steady discrete equations:
- With the cell velocity U = kc (HbyA0 - rAU0 grad p), the steady Rhie-Chow flux is
  u_f = kf [avg(U_L, U_R) - rAU0_f (grad_f p + Df u_f)] + (ddtCorr).
- rho/dt is 16 times mu d here, so the face flux follows the average of the two cell velocities.
- In open cells the steady cell equation only forces the central gradient to zero, so their velocities are free to
  ripple (measured: 0.40 u and 1.69 u next to the plug). Through avg(U) that ripple enters the face flux and the
  interface pressure drop.
- Setting `ddtPhiCoeff 1` in a diagnostic copy of fvSchemes changed nothing (identical results).

Change: after the pressure correction, the cell velocity is reconstructed from the absolute face fluxes,

    U = reconstruct(absolute(phi) / interpolate(rho))

replacing kc (HbyA0 - rAU0 grad p). Then avg(U) = u_f in 1-D, and the steady face balance is
grad_f p = -Df u_f exactly. The face drag of the first part stays.

Diagnostic result at 1 mm, t = 0.02 s (scratch copy of v1 and v4, not stored):
- rel_err -1e-6 (Darcy) and -1.3e-3 (Forchheimer);
- edge-cell U/u between 0.998 and 1.000.

This changes the cell velocity in every cell, not only in porous ones. L0 and L1 are re-run against their unchanged
bars in the same PR, and CI re-checks both.

Expected L2 rows: rel_err below 2e-3 for all four runs. The other rows are as in the table above.
