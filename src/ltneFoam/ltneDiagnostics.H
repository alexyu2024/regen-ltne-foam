// Global inventories for the verification scripts (one line per time step):
// gas mass, gas internal energy (sensible, relative to the thermo reference),
// solid energy (cells with solid only, relative to 0 K), total volume.
{
    const volScalarField& he = thermo.he();
    const volScalarField eGas
    (
        he.name() == "e" ? volScalarField(he) : volScalarField(he - p/rho)
    );

    Info<< "ltne: time = " << runTime.value()
        << " gasMass = " << fvc::domainIntegrate(eps*rho).value()
        << " gasInternalEnergy = "
        << fvc::domainIntegrate(eps*rho*eGas).value()
        << " solidEnergy = "
        << (solidActive ? fvc::domainIntegrate(solidMask*CS*Ts).value() : 0)
        << " volume = " << gSum(mesh.V())
        << endl;
}
