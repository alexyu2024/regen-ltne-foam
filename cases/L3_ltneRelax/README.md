# L3 LTNE relaxation, no flow

Closed 1-D block (10 cells, all porous, eps = 0.7). Gas starts at 300 K, solid at 320 K, no flow. The two
temperatures relax to T_eq through hA (T_s - T_g). The result is compared with the exact two-temperature ODE solution.
Run r uses stainless steel (c_s = 500 J/kg/K); run b uses an artificial c_s = 5 J/kg/K so that both temperatures move.
Bars and formulas: `docs/VERIFICATION.md`, L3.

## Characteristic numbers (from the inputs, before the first run)

| quantity | r | b |
|---|---|---|
| C_g = eps rho c_v, J/m3/K (rho = 3.209 kg/m3, c_v = 3115.7 J/kg/K) | 6999.6 | 6999.6 |
| C_s = (1 - eps) rho_s c_s, J/m3/K | 1.185e6 | 11850 |
| tau = 1 / (hA (1/C_g + 1/C_s)), s | 2.899e-4 | 1.833e-4 |
| dt / tau | 0.0100 | 0.0098 |
| T_eq, K | 319.883 | 312.573 |
| solid conduction time over the block, (1 - eps) rho_s c_s L^2 / ((1 - eps) k_s), s (L = 10 mm) | 26 | 0.26 |

The fields stay uniform: all cells are identical and the walls are adiabatic, so conduction plays no role. The
acoustic CFL is 1019 x 2.9e-6 / 1e-3 = 3. There is no flow, so the Reynolds and Womersley numbers do not apply.
