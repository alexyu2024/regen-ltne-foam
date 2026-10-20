// Solid-matrix energy: (1-eps) rhoS d(hS)/dt
//     = div((1-eps) kS grad Ts) + hA (T - Ts)
// Constant solid: hS = CpS Ts (fvm::ddt). Temperature-dependent solid:
// energy-conservative enthalpy form, Euler in time, linearised about the
// current iterate Ts*:
//   CS (Ts - Ts*)/dt + (1-eps) rhoS (hS(Ts*) - hS(Ts_old))/dt
// Cells of zones with fixedTs keep that temperature.
if (solidActive)
{
    tmp<fvScalarMatrix> tTsEqn;

    if (variableSolid)
    {
        const scalar rDeltaT = 1.0/runTime.deltaTValue();
        volScalarField hDiff
        (
            IOobject("hDiff", runTime.timeName(), mesh),
            mesh,
            dimensionedScalar(dimPower/dimVolume, Zero)
        );
        const volScalarField& Ts0 = Ts.oldTime();
        forAll(hDiff, celli)
        {
            hDiff[celli] =
                epsS[celli]*rhoS.value()*rDeltaT
               *(hSS(Ts[celli]) - hSS(Ts0[celli]));
        }

        tTsEqn =
        (
            fvm::Sp(CS*dimensionedScalar(dimless/dimTime, rDeltaT), Ts)
          - CS*dimensionedScalar(dimless/dimTime, rDeltaT)*Ts
          + hDiff
          - fvm::laplacian(kSf, Ts)
         ==
            hA*thermo.T() - fvm::Sp(hA, Ts)
        );
    }
    else
    {
        tTsEqn =
        (
            fvm::ddt(CS, Ts)
          - fvm::laplacian(kSf, Ts)
         ==
            hA*thermo.T() - fvm::Sp(hA, Ts)
          + fvOptions(CS, Ts)
        );
    }
    fvScalarMatrix& TsEqn = tTsEqn.ref();

    if (fixedTsCells.size())
    {
        TsEqn.setValues(fixedTsCells, fixedTsValues);
    }

    TsEqn.relax();

    fvOptions.constrain(TsEqn);

    TsEqn.solve();

    fvOptions.correct(Ts);

    // Ts has no meaning in open gas cells
    Ts.primitiveFieldRef() =
        solidMask*Ts.primitiveField() + (1 - solidMask)*thermo.T().primitiveField();
    Ts.correctBoundaryConditions();
}
