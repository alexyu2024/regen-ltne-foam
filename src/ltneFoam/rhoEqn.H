// Continuity with porosity-weighted storage: eps d(rho)/dt + div(phi) = 0
{
    fvScalarMatrix rhoEqn
    (
        eps()*fvm::ddt(rho)
      + fvc::div(phi)
      ==
        fvOptions(rho)
    );

    fvOptions.constrain(rhoEqn);

    rhoEqn.solve();

    fvOptions.correct(rho);
}
