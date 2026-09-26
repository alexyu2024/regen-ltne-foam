// Solid-matrix energy: (1-eps) rhoS CpS dTs/dt
//     = div((1-eps) kS grad Ts) + hA (T - Ts)
if (solidActive)
{
    fvScalarMatrix TsEqn
    (
        fvm::ddt(CS, Ts)
      - fvm::laplacian(kSf, Ts)
     ==
        hA*thermo.T() - fvm::Sp(hA, Ts)
      + fvOptions(CS, Ts)
    );

    TsEqn.relax();

    fvOptions.constrain(TsEqn);

    TsEqn.solve();

    fvOptions.correct(Ts);

    // Ts has no meaning in open gas cells
    Ts.primitiveFieldRef() =
        solidMask*Ts.primitiveField() + (1 - solidMask)*thermo.T().primitiveField();
    Ts.correctBoundaryConditions();
}
