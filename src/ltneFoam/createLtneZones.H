// Optional per-zone porous-medium description (constant/ltneProperties,
// subdictionary "zones"). Without it the fields porosity/asf and the constant
// hsf are used as before. With it, each named cellZone sets:
//   porosity, asf [1/m]
//   hsfModel      none | constant | screenGedeonWood | wakao
//     constant:          hsf [W/m2/K]
//     screenGedeonWood:  Nu = (1 + 0.99 Pe^0.66) nuBetaFactor, Pe = Re Pr,
//                        Re = rho |U| d_re / mu, hsf = Nu k / d_h
//     wakao:             Nu = max(2, 2 + 1.1 Re^0.6 Pr^(1/3)), Re on d_h
//   ksFrac        solid conductivity factor (default 1)
//   kSolid        optional constant intrinsic solid conductivity [W/m/K]
//                 (overrides the solid model in this zone, e.g. copper HX)
//   fixedTs       optional fixed solid temperature [K]
// solidModel (top level): constant (rhoS, CpS, kS) or stainlessDeltaEC
// (DeltaEC Users Guide 13.5 fits for cp(T) and k(T), rhoS constant).

// Per-cell zone data (model id: -1 none, 0 constant, 1 screenGedeonWood,
// 2 wakao)
labelList hsfModelId(mesh.nCells(), -1);
scalarField hsfConst(mesh.nCells(), Zero);
scalarField dRe(mesh.nCells(), Zero);
scalarField dH(mesh.nCells(), GREAT);
scalarField nuBeta(mesh.nCells(), Zero);
scalarField ksFrac(mesh.nCells(), 1.0);
scalarField kSolidConst(mesh.nCells(), -1.0);
labelList fixedTsCells;
scalarField fixedTsValues;
wordList fixedTsZones;
List<labelList> fixedTsZoneCells;

if (zonesActive)
{
    const dictionary& zonesDict = ltneProperties.subDict("zones");

    for (const entry& e : zonesDict)
    {
        const word& zoneName = e.keyword();
        const dictionary& zd = e.dict();
        const label zonei = mesh.cellZones().findZoneID(zoneName);
        if (zonei < 0)
        {
            FatalErrorInFunction
                << "cellZone " << zoneName << " not found" << exit(FatalError);
        }
        const labelList& cells = mesh.cellZones()[zonei];

        const scalar zEps = zd.get<scalar>("porosity");
        const scalar zAsf = zd.get<scalar>("asf");
        const word model(zd.get<word>("hsfModel"));
        label id = -1;
        if (model == "constant") { id = 0; }
        else if (model == "screenGedeonWood") { id = 1; }
        else if (model == "wakao") { id = 2; }
        else if (model != "none")
        {
            FatalErrorInFunction
                << "zone " << zoneName << ": unknown hsfModel " << model
                << exit(FatalError);
        }

        for (const label celli : cells)
        {
            eps[celli] = zEps;
            asf[celli] = zAsf;
            hsfModelId[celli] = id;
            if (id == 0) { hsfConst[celli] = zd.get<scalar>("hsf"); }
            if (id == 1)
            {
                dRe[celli] = zd.get<scalar>("d_re");
                dH[celli] = zd.get<scalar>("d_h");
                nuBeta[celli] = zd.get<scalar>("nuBetaFactor");
            }
            if (id == 2) { dH[celli] = zd.get<scalar>("d_h"); }
            ksFrac[celli] = zd.getOrDefault<scalar>("ksFrac", 1.0);
            kSolidConst[celli] = zd.getOrDefault<scalar>("kSolid", -1.0);
        }

        if (zd.found("fixedTs"))
        {
            const scalar Tfix = zd.get<scalar>("fixedTs");
            fixedTsZones.append(zoneName);
            fixedTsZoneCells.append(cells);
            for (const label celli : cells)
            {
                fixedTsCells.append(celli);
                fixedTsValues.append(Tfix);
            }
        }

        Info<< "LTNE zone " << zoneName << ": porosity " << zEps
            << ", asf " << zAsf << ", hsfModel " << model
            << (zd.found("fixedTs") ? ", fixed Ts" : "") << endl;
    }
    eps.correctBoundaryConditions();
    asf.correctBoundaryConditions();
}

// Stainless-steel fits (DeltaEC Users Guide 13.5), valid 6-1300 K
auto cpSS = [](const double T) -> double
{
    return
        std::pow(1.7054e-6*std::pow(T, -0.88962) + 23324*std::pow(T, -6.0), -1.0/3.0)
      + 15/T - 35/(T*T) + 25/(T*T*T);
};
auto kSS = [](const double T) -> double
{
    return std::pow(266800*std::pow(T, -5.2) + 0.21416*std::pow(T, -1.6), -0.25);
};

// Specific solid enthalpy h(T) = int_{Tlo}^{T} cp dT, tabulated for the
// energy-conservative solid equation (variable cp only)
const scalar hTabTlo = 4.0, hTabDT = 0.005;
scalarField hTab;
if (variableSolid)
{
    const label n = label((400.0 - hTabTlo)/hTabDT) + 1;
    hTab.setSize(n, Zero);
    for (label i = 1; i < n; ++i)
    {
        const scalar Ta = hTabTlo + (i - 1)*hTabDT;
        hTab[i] = hTab[i - 1] + 0.5*hTabDT*(cpSS(Ta) + cpSS(Ta + hTabDT));
    }
}
auto hSS = [&](const double T) -> double
{
    const scalar x = (min(max(T, hTabTlo), 399.99) - hTabTlo)/hTabDT;
    const label i = label(x);
    return hTab[i] + (x - i)*(hTab[i + 1] - hTab[i]);
};
