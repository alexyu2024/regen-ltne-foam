# L0 smoke case

1-D closed helium tube, x in [0, 0.1] m, 40 cells. Piston at x = 0 (1 mm amplitude, 50 Hz; `pistonLinear` mesh motion
stretches the cells in x in [0, 0.04] m, the rest of the mesh does not move). Porous plug x in [0.04, 0.06] m: porosity 0.7, a_sf = 24000 1/m, Darcy d = 1e10 1/m2,
Forchheimer f = 1e5 1/m, h_sf = 1000 W/m2/K, solid initially at 310 K, gas at 300 K and 2 MPa. Run for 1 ms
(1000 steps, 5 % of a period). A test that the code runs, not a physics check. Bars: `docs/VERIFICATION.md`, L0.

## Characteristic numbers (computed from the inputs above before the first run)

| quantity | formula | value |
|---|---|---|
| gas constant | R = 8314.46 / 4.0026 | 2077.2 J/kg/K |
| gamma | Cp / (Cp - R) = 5193 / 3115.8 | 1.667 |
| sound speed | c = sqrt(gamma R T) | 1019 m/s |
| density | rho = p / (R T) | 3.21 kg/m3 |
| acoustic CFL | c dt / dx = 1019 * 1e-6 / 2.5e-3 | 0.41 |
| wavelength / tube length | (c / f) / L = 20.4 / 0.1 | 204 (tube length << wavelength) |
| piston velocity amplitude, Mach | U = 1e-3 * 314.16; U / c | 0.314 m/s; 3.1e-4 |
| hydraulic diameter | d_h = eps d_w / (1 - eps) | 117 um |
| pore Reynolds number (plug centre) | rho (U/2/eps) d_h / mu | 4.2 |
| pore Womersley number | (d_h / 2) sqrt(omega rho / mu) | 0.41 |
| thermal penetration depth | sqrt(2 alpha / omega), alpha = k / (rho Cp) = 9.3e-6 m2/s | 243 um (about 2 d_h) |
| gas LTNE time scale | eps rho Cp / (h_sf a_sf) | 4.9e-4 s (dt / tau = 0.002) |
| solid LTNE time scale | (1 - eps) rho_s c_s / (h_sf a_sf) | 4.9e-2 s |
