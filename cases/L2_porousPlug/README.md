# L2 Darcy-Forchheimer plug, steady flow

1-D helium channel, 0.1 m, porous plug in [0.04, 0.06] m (alpha = 1e-9 m2, C2 = 1e5 1/m), inlet velocity 0.001,
0.01, 0.1 and 1 m/s (runs v1 to v4), outlet at 2 MPa. The pressure drop is compared with
dp = L (mu/alpha u + C2 rho u^2 / 2). Bars and definitions: `docs/VERIFICATION.md`, L2.

## Characteristic numbers (from the inputs, before the first run; rho = 3.21 kg/m3 at 2 MPa, 300 K)

| quantity | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| u, m/s | 0.001 | 0.01 | 0.1 | 1 |
| Forchheimer / Darcy = C2 rho u alpha / (2 mu) | 0.0081 | 0.081 | 0.81 | 8.1 |
| expected dp = L (mu/alpha u + C2 rho u^2/2), Pa | 0.40 | 4.1 | 72 | 3608 |
| dp / p | 2e-7 | 2e-6 | 4e-5 | 1.8e-3 |
| Re_K = rho u sqrt(alpha) / mu | 5.1e-3 | 0.051 | 0.51 | 5.1 |
| Mach u / c | 1e-6 | 1e-5 | 1e-4 | 1e-3 |
| plug residence time L eps / u, s | 14 | 1.4 | 0.14 | 0.014 |

Acoustic CFL c dt / dx = 1019 * 1e-5 / 1e-3 = 10. Pressure relaxation of the upstream volume through the plug has a
time scale R C = (L mu / (alpha rho)) (0.04 / c^2) = 5e-6 s, so the pressure drop settles within the 0.05 s run even
where the gas has not been flushed through (v1 to v3); temperature changes from drag heating stay below
dp / (rho Cp) = 0.2 K (v4).
