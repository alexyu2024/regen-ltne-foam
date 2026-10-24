# Helium real-gas table

`genHeliumTable.py` writes `src/ltneRealGas/tables/helium_CoolProp.dat`, the T-p property table read at run time
by the optional real-gas model (library `ltneRealGas`). Running a case needs only the committed table, not CoolProp.

    python3 -m venv venv && venv/bin/pip install -r tools/heliumRealGas/requirements.txt
    venv/bin/python tools/heliumRealGas/genHeliumTable.py src/ltneRealGas/tables/helium_CoolProp.dat

- **Source**: CoolProp 8.0.0 (MIT licence). Helium EOS: Ortiz-Vega et al., J. Phys. Chem. Ref. Data (2019);
  viscosity: Arp (NIST 1998); conductivity: Hands (Cryogenics 1981), as CoolProp selects them. At the six points of
  `cases/LP_heliumRealGas/nist_helium.csv`, CoolProp reproduces the NIST WebBook to every printed digit.
- **Grid**: T 15-95 K in 0.25 K steps; p 0.5-1.0 MPa in 0.025 MPa steps. CoolProp's helium viscosity has a jump
  near 100 K, so the table stops at 95 K.
- **Fields**: rho, hDep, cp, cv, sDep, mu and kappa. Departures are measured from the ideal gas at 1 Pa.
- **Interpolation error**: the largest bilinear error at the cell centres, against CoolProp, is written into the
  file header. It is 1.2e-4 for rho and 2.9e-5 for cp, both at the 15 K corner.
- **Ideal-gas part**: molWeight 4.002602 and cp0 = 2.5 R = 5193.15922 J/kg/K. A case must use exactly these in
  `thermophysicalProperties`; the model checks this and stops otherwise.
