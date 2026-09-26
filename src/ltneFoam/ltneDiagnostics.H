// Global inventories for the verification scripts, one row per time step in
// postProcessing/ltneDiagnostics/<startTime>/ltne.dat:
//   gas mass, gas internal energy (sensible, relative to the thermo reference),
//   gas kinetic energy, solid energy (cells with solid, relative to 0 K),
//   gas volume, gas-volume-averaged pressure, cumulative work done on the gas
//   by moving boundaries, and min/max cell volume of every cellZone.
{
    const volScalarField& he = thermo.he();
    const volScalarField eGas
    (
        he.name() == "e" ? volScalarField(he) : volScalarField(he - p/rho)
    );

    if (mesh.moving())
    {
        forAll(mesh.boundary(), patchi)
        {
            boundaryWork -=
                runTime.deltaTValue()
               *gSum
                (
                    mesh.phi().boundaryField()[patchi]
                   *p.boundaryField()[patchi]
                );
        }
    }

    const scalar gasVolume = fvc::domainIntegrate(eps).value();

    if (Pstream::master())
    {
        diagFile()
            << runTime.value()
            << ' ' << fvc::domainIntegrate(eps*rho).value()
            << ' ' << fvc::domainIntegrate(eps*rho*eGas).value()
            << ' ' << fvc::domainIntegrate(rho*K).value()
            << ' '
            << (solidActive ? fvc::domainIntegrate(solidMask*CS*Ts).value() : 0)
            << ' ' << gasVolume
            << ' ' << fvc::domainIntegrate(eps*p).value()/gasVolume
            << ' ' << boundaryWork;
    }

    for (const cellZone& zone : mesh.cellZones())
    {
        const scalarField zoneV(mesh.V().field(), zone);
        const scalar vMin = gMin(zoneV);
        const scalar vMax = gMax(zoneV);
        if (Pstream::master())
        {
            diagFile() << ' ' << vMin << ' ' << vMax;
        }
    }

    if (Pstream::master())
    {
        diagFile() << endl;
    }
}
