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

    // Solid energy: CS Ts for a constant solid, (1-eps) rhoS hS(Ts) otherwise
    scalar solidEnergyTotal = 0;
    if (variableSolid)
    {
        forAll(Ts, celli)
        {
            solidEnergyTotal +=
                solidMask[celli]*epsS[celli]*rhoS.value()*hSS(Ts[celli])
               *mesh.V()[celli];
        }
        reduce(solidEnergyTotal, sumOp<scalar>());
    }
    else if (solidActive)
    {
        solidEnergyTotal = fvc::domainIntegrate(solidMask*CS*Ts).value();
    }

    if (Pstream::master())
    {
        diagFile()
            << runTime.value()
            << ' ' << fvc::domainIntegrate(eps*rho).value()
            << ' ' << fvc::domainIntegrate(eps*rho*eGas).value()
            << ' ' << fvc::domainIntegrate(rho*K).value()
            << ' '
            << (solidActive ? solidEnergyTotal : 0)
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

// Monitors (see createLtneMonitors.H)
if (monitorsActive)
{
    const volScalarField& he = thermo.he();
    const surfaceScalarField pf(fvc::interpolate(p));
    const surfaceScalarField Tf(fvc::interpolate(thermo.T()));
    const surfaceScalarField Hf
    (
        // enthalpy relative to 0 K: he is sensible enthalpy relative to Tstd,
        // so add Cp Tstd (constant-Cp gases)
        fvc::flux(phi, he, "div(phi,h)") + fvc::flux(phi, K, "div(phi,K)")
      + phi*fvc::interpolate(thermo.Cp())*constant::standard::Tstd
      - fvc::interpolate(eps*turbulence->alphaEff())*fvc::snGrad(he)
       *mesh.magSf()
      - kSf*fvc::snGrad(Ts)*mesh.magSf()
    );

    DynamicList<scalar> row;
    for (const word& fz : monitorFaceZones)
    {
        const faceZone& zone = mesh.faceZones()[fz];
        scalar A = 0, pA = 0, TA = 0, mdot = 0, H = 0;
        for (const label facei : zone)
        {
            if (facei >= mesh.nInternalFaces()) { continue; }
            const scalar a = mesh.magSf()[facei];
            const scalar sgn = sign(mesh.Sf()[facei] & monitorAxis);
            A += a;
            pA += pf[facei]*a;
            TA += Tf[facei]*a;
            mdot += sgn*phi[facei];
            H += sgn*Hf[facei];
        }
        reduce(A, sumOp<scalar>());
        reduce(pA, sumOp<scalar>());
        reduce(TA, sumOp<scalar>());
        reduce(mdot, sumOp<scalar>());
        reduce(H, sumOp<scalar>());
        row.append(pA/max(A, VSMALL));
        row.append(TA/max(A, VSMALL));
        row.append(mdot);
        row.append(H);
    }
    for (const word& pn : monitorPatches)
    {
        const label patchi = mesh.boundaryMesh().findPatchID(pn);
        scalar Up = 0, W = 0;
        if (mesh.moving())
        {
            // mesh.phi() is the swept volume per unit time [m3/s]
            Up = -gSum(mesh.phi().boundaryField()[patchi]);
            W = -gSum
            (
                mesh.phi().boundaryField()[patchi]*p.boundaryField()[patchi]
            );
        }
        row.append(Up);
        row.append(W);
    }
    forAll(fixedTsZones, zi)
    {
        scalar Q = 0;
        for (const label celli : fixedTsZoneCells[zi])
        {
            Q += hA[celli]*(Ts[celli] - thermo.T()[celli])*mesh.V()[celli];
        }
        reduce(Q, sumOp<scalar>());
        row.append(Q);

        scalar Qs = 0;
        const labelUList& own = mesh.owner();
        const labelUList& nei = mesh.neighbour();
        forAll(nei, facei)
        {
            const label zo = fixedZoneOfCell[own[facei]];
            const label zn = fixedZoneOfCell[nei[facei]];
            const scalar G =
                kSf[facei]*mesh.deltaCoeffs()[facei]*mesh.magSf()[facei];
            if (zo == zi && zn != zi)
            {
                Qs += G*(Ts[own[facei]] - Ts[nei[facei]]);
            }
            else if (zn == zi && zo != zi)
            {
                Qs += G*(Ts[nei[facei]] - Ts[own[facei]]);
            }
        }
        reduce(Qs, sumOp<scalar>());
        row.append(Qs);
    }

    {
        scalar Qn = 0, Qa = 0;
        forAll(hA, celli)
        {
            if (fixedZoneOfCell[celli] >= 0) { continue; }
            const scalar q =
                hA[celli]*(Ts[celli] - thermo.T()[celli])*mesh.V()[celli];
            Qn += q;
            Qa += mag(q);
        }
        reduce(Qn, sumOp<scalar>());
        reduce(Qa, sumOp<scalar>());
        row.append(Qn);
        row.append(Qa);
    }

    if (Pstream::master())
    {
        monitorFile() << runTime.value();
        for (const scalar v : row) { monitorFile() << ' ' << v; }
        monitorFile() << endl;
    }
}
