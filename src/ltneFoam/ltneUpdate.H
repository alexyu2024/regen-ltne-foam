// Per-iteration update of the zone-dependent LTNE coefficients (zones only):
// the live film coefficient hA = hsf(Re, Pr, k) asf and, for a
// temperature-dependent solid, its heat capacity CS and face conductivity kSf.
if (zonesActive)
{
    const tmp<volScalarField> tmu(thermo.mu());
    const tmp<volScalarField> tkappa(thermo.kappa());
    const tmp<volScalarField> tCp(thermo.Cp());
    const scalarField& muC = tmu().primitiveField();
    const scalarField& kC = tkappa().primitiveField();
    const scalarField& cpC = tCp().primitiveField();

    forAll(hA, celli)
    {
        const label id = hsfModelId[celli];
        scalar hsfCell = 0;
        if (id == 0)
        {
            hsfCell = hsfConst[celli];
        }
        else if (id > 0)
        {
            const scalar Pr = muC[celli]*cpC[celli]/kC[celli];
            const scalar rhoU = rho[celli]*mag(U[celli]);
            if (id == 1)
            {
                const scalar Pe = rhoU*dRe[celli]/muC[celli]*Pr;
                hsfCell =
                    (1 + 0.99*std::pow(Pe, 0.66))*nuBeta[celli]*kC[celli]/dH[celli];
            }
            else
            {
                const scalar Re = rhoU*dH[celli]/muC[celli];
                hsfCell =
                    max(2.0, 2.0 + 1.1*std::pow(Re, 0.6)*std::cbrt(Pr))
                   *kC[celli]/dH[celli];
            }
        }
        hA[celli] = hsfCell*asf[celli];
    }
    hA.correctBoundaryConditions();

    if (variableSolid)
    {
        volScalarField kScell("kScell", epsS*kS);
        forAll(Ts, celli)
        {
            const scalar Tc = max(Ts[celli], 6.0);
            CS[celli] = epsS[celli]*rhoS.value()*cpSS(Tc);
            kScell[celli] =
                epsS[celli]
               *(
                    kSolidConst[celli] >= 0
                  ? kSolidConst[celli]
                  : ksFrac[celli]*kSS(Tc)
                );
        }
        kScell.correctBoundaryConditions();
        kSf = harmonic(mesh).interpolate(kScell);
    }
}
