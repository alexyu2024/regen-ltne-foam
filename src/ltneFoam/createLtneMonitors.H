// Optional monitors (constant/ltneProperties, subdictionary "monitors"):
//   axis (0 0 1); faceZones (...); patches (...);
// One row per time step in postProcessing/ltneDiagnostics/<t0>/monitors.dat:
//   per faceZone: area-average p and T, mass flow along the axis, and the
//     total energy flow H = phi (h + K) - (eps alphaEff snGrad h
//     (h relative to 0 K for a constant Cp)
//     + kSf snGrad Ts) |Sf|, using the same discrete terms as the equations;
//   per patch: piston volume flow Up = -sum(meshPhi) and work rate
//     -sum(p meshPhi) on the gas;
//   per fixedTs zone: heat rate from the fixed solid into the gas,
//     Qgas = hA (Ts - T) V, and by solid conduction into the adjacent solid,
//     Qsolid = kSf (Ts_fixed - Ts_neighbour) deltaCoeff |Sf| (same discrete
//     term as the solid equation).
const bool monitorsActive = ltneProperties.found("monitors");
vector monitorAxis(0, 0, 1);
wordList monitorFaceZones, monitorPatches;
autoPtr<OFstream> monitorFile;
if (monitorsActive)
{
    const dictionary& md = ltneProperties.subDict("monitors");
    monitorAxis = normalised(md.get<vector>("axis"));
    monitorFaceZones = md.get<wordList>("faceZones");
    monitorPatches = md.get<wordList>("patches");

    for (const word& fz : monitorFaceZones)
    {
        if (mesh.faceZones().findZoneID(fz) < 0)
        {
            FatalErrorInFunction
                << "faceZone " << fz << " not found" << exit(FatalError);
        }
    }
    for (const word& pn : monitorPatches)
    {
        if (mesh.boundaryMesh().findPatchID(pn) < 0)
        {
            FatalErrorInFunction
                << "patch " << pn << " not found" << exit(FatalError);
        }
    }

    if (Pstream::master())
    {
        const fileName dir
        (
            runTime.globalPath()/"postProcessing"/"ltneDiagnostics"
           /runTime.timeName()
        );
        mkDir(dir);
        monitorFile.reset(new OFstream(dir/"monitors.dat"));
        monitorFile().precision(15);
        monitorFile() << "# time";
        for (const word& fz : monitorFaceZones)
        {
            monitorFile()
                << ' ' << fz << "_p " << fz << "_T " << fz << "_mdot "
                << fz << "_H";
        }
        for (const word& pn : monitorPatches)
        {
            monitorFile() << ' ' << pn << "_Up " << pn << "_Wrate";
        }
        for (const word& zn : fixedTsZones)
        {
            monitorFile() << ' ' << zn << "_Qgas " << zn << "_Qsolid";
        }
        monitorFile() << endl;
    }
}

// Cell flag: which fixedTs zone a cell belongs to (-1: none)
labelList fixedZoneOfCell(mesh.nCells(), -1);
forAll(fixedTsZoneCells, zi)
{
    for (const label celli : fixedTsZoneCells[zi])
    {
        fixedZoneOfCell[celli] = zi;
    }
}
