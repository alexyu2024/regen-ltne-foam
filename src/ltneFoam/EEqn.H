// Gas energy with porosity-weighted storage and gas-matrix exchange
// hA (Ts - T), linearised in he about the current iterate:
//   hA (Ts - T) ~ hA (Ts - T) + hA/Cpv he* - hA/Cpv he
{
    volScalarField& he = thermo.he();
    const volScalarField& T = thermo.T();

    const volScalarField hAbyCpv("hAbyCpv", hA/thermo.Cpv());

    fvScalarMatrix EEqn
    (
        eps()*(fvm::ddt(rho, he) + fvc::ddt(rho, K))
      + fvm::div(phi, he) + fvc::div(phi, K)
      + (
            he.name() == "e"
          ? fvc::div
            (
                fvc::absolute(phi/fvc::interpolate(rho), U),
                p,
                "div(phiv,p)"
            )
          : -eps*dpdt
        )
      - fvm::laplacian(eps*turbulence->alphaEff(), he)
     ==
        hA*(Ts - T) + hAbyCpv*he - fvm::Sp(hAbyCpv, he)
      + fvOptions(rho, he)
    );

    EEqn.relax();

    fvOptions.constrain(EEqn);

    EEqn.solve();

    fvOptions.correct(he);

    thermo.correct();
}
