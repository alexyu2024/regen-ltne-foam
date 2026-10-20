#!/usr/bin/env python3
"""Write the L5 case dictionaries and initial fields from params_L5.yaml (values used verbatim).

Usage: mkCase.py <case dir> [--matrix-refine N]
The matrix cells are refined N times (sensitivity check); everything else is unchanged.
"""
import math, os, sys
import yaml

here = os.path.dirname(os.path.abspath(__file__))
P = yaml.safe_load(open(os.path.join(here, 'params_L5.yaml')))
case = sys.argv[1]
refine = int(sys.argv[sys.argv.index('--matrix-refine') + 1]) if '--matrix-refine' in sys.argv else 1

HDR = """/*--------------------------------*- C++ -*----------------------------------*\\
  regen-ltne-foam, OpenFOAM v2512 - written by cases/L5_regenSlice/mkCase.py
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    object      {obj};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""


def write(rel, cls, text):
    path = os.path.join(case, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(HDR.format(cls=cls, obj=os.path.basename(rel)) + text)


f = P['operating_point']['frequency_Hz']
pm = P['operating_point']['mean_pressure_Pa']
gas = P['gas']
Z = P['layout']['zones']
area = P['layout']['area_m2']
side = math.sqrt(area)
Thot = Z['hot_hx']['solid_T_fixed_K']
Tcold = Z['cold_hx']['solid_T_fixed_K']

# ---- mesh: blocks along z (axis), 1-D -------------------------------------
order = ['hot_chamber', 'hot_hx', 'matrix_500', 'matrix_635', 'cold_hx', 'cold_chamber']
ncells = {'hot_chamber': 24, 'hot_hx': 10, 'matrix_500': 60 * refine, 'matrix_635': 60 * refine,
          'cold_hx': 10, 'cold_chamber': 8}
zlev = [Z[order[0]]['z'][0]] + [Z[n]['z'][1] for n in order]
verts = []
for z in zlev:
    verts += [(0, 0, z), (side, 0, z), (side, side, z), (0, side, z)]
blocks, sides = [], []
for k, n in enumerate(order):
    a, b = 4 * k, 4 * (k + 1)
    blocks.append(f'    hex ({a} {a+1} {a+2} {a+3} {b} {b+1} {b+2} {b+3}) {n} (1 1 {ncells[n]}) simpleGrading (1 1 1)')
    sides += [f'({a} {a+1} {b+1} {b})', f'({a+1} {a+2} {b+2} {b+1})',
              f'({a+2} {a+3} {b+3} {b+2})', f'({a} {b} {b+3} {a+3})']
last = 4 * len(order)
write('system/blockMeshDict', 'dictionary', f"""// 1-D column along z, square cross-section of area {area} m2; z = 0 at the matrix hot face
scale   1;

vertices
(
{chr(10).join(f'    ({x:.10g} {y:.10g} {z:.10g})' for x, y, z in verts)}
);

blocks
(
{chr(10).join(blocks)}
);

boundary
(
    hotPiston
    {{
        type wall;
        faces ((0 3 2 1));
    }}
    coldPiston
    {{
        type wall;
        faces (({last} {last+1} {last+2} {last+3}));
    }}
    sides
    {{
        type empty;
        faces
        (
{chr(10).join('            ' + s for s in sides)}
        );
    }}
);
""")

# face zones at the matrix hot face, the joint and the matrix cold face
planes = {'hotFace': Z['matrix_500']['z'][0], 'joint': Z['matrix_635']['z'][0], 'coldFace': Z['matrix_635']['z'][1]}
actions = []
for name, z in planes.items():
    actions.append(f"""    {{
        name    {name}Set;
        type    faceSet;
        action  new;
        source  boxToFace;
        box     (-1 -1 {z - 1e-7:.9g}) (1 1 {z + 1e-7:.9g});
    }}
    {{
        name    {name};
        type    faceZoneSet;
        action  new;
        source  setToFaceZone;
        faceSet {name}Set;
    }}""")
write('system/topoSetDict', 'dictionary', 'actions\n(\n' + '\n'.join(actions) + '\n);\n')

# ---- thermophysical properties (verbatim tables) --------------------------
RR = 8314.462618  # OpenFOAM's universal gas constant, J/kmol/K
M = RR / gas['R_J_kgK']
tab = lambda rows: '\n'.join(f'            ({t:g} {v:.7e})' for t, v in rows)
write('constant/thermophysicalProperties', 'dictionary', f"""// Helium, ideal gas, R = {gas['R_J_kgK']} J/kg/K (molWeight = RR / R), cp = {gas['cp_J_kgK']} J/kg/K,
// mu(T) and kappa(T): CoolProp tables of params_L5.yaml, linear interpolation
thermoType
{{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       tabulated;
    thermo          hTabulated;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}}

dpdt yes;

mixture
{{
    specie
    {{
        molWeight   {M:.10g};
    }}
    thermodynamics
    {{
        Hf          0;
        Sf          0;
        Cp          ((1 {gas['cp_J_kgK']}) (400 {gas['cp_J_kgK']}));
    }}
    transport
    {{
        mu
        (
{tab(gas['mu_table_T_K__Pa_s'])}
        );
        kappa
        (
{tab(gas['k_table_T_K__W_mK'])}
        );
    }}
}}
""")
write('constant/turbulenceProperties', 'dictionary', 'simulationType  laminar;\n')

# ---- porous zones, solid model, monitors ----------------------------------
pmx, phx = P['porous_matrix'], P['porous_hx']
kcu = lambda T: 398 - 0.0567 * (T - 300)   # copper, DeltaEC Users Guide 13.3


def screen(s):
    return f"""        porosity        {s['porosity']};
        asf             {s['a_sf_m1']};
        hsfModel        screenGedeonWood;
        d_re            {s['d_re_m']};
        d_h             {s['d_h_m']};
        nuBetaFactor    {s['nu_beta_factor']};
        ksFrac          {P['solids']['ksFrac']};"""


def hx(T):
    return f"""        porosity        {phx['porosity']};
        asf             {phx['a_sf_m1']};
        hsfModel        wakao;
        d_h             {phx['d_h_m']};
        fixedTs         {T};
        kSolid          {kcu(T):.6g};    // copper, 398 - 0.0567 (T - 300)"""


write('constant/ltneProperties', 'dictionary', f"""active          true;
solidModel      stainlessDeltaEC;   // cp_ss(T), k_ss(T): DeltaEC Users Guide 13.5
rhoS            7990;               // held constant (params_L5.yaml allows it)

zones
{{
    hot_hx
    {{
{hx(Thot)}
    }}
    matrix_500
    {{
{screen(pmx['screen_500'])}
    }}
    matrix_635
    {{
{screen(pmx['screen_635'])}
    }}
    cold_hx
    {{
{hx(Tcold)}
    }}
}}

monitors
{{
    axis        (0 0 1);
    faceZones   (hotFace joint coldFace);
    patches     (hotPiston coldPiston);
}}
""")


def drag(name, zone, d, f2):
    return f"""{name}
{{
    type            explicitPorositySource;
    explicitPorositySourceCoeffs
    {{
        selectionMode   cellZone;
        cellZone        {zone};
        type            DarcyForchheimer;
        d   ({d} {d} {d});
        f   ({f2} {f2} {f2});
        coordinateSystem
        {{
            origin  (0 0 0);
            e1      (1 0 0);
            e3      (0 0 1);
        }}
    }}
}}
"""


write('constant/fvOptions', 'dictionary',
      drag('dragHotHx', 'hot_hx', phx['inv_alpha_m2'], phx['C2_m1'])
      + drag('drag500', 'matrix_500', pmx['screen_500']['inv_alpha_m2'], pmx['screen_500']['C2_m1'])
      + drag('drag635', 'matrix_635', pmx['screen_635']['inv_alpha_m2'], pmx['screen_635']['C2_m1'])
      + drag('dragColdHx', 'cold_hx', phx['inv_alpha_m2'], phx['C2_m1']))

# ---- pistons: x(t) = |x| [cos(wt + Ph) - cos(Ph) exp(-t/T)] ---------------
dr = P['drive']
T = 1.0 / f


def piston(name, zp, zf, amp, ph, scale):
    # ESI sine: a sin(2 pi f (t - t0)) s + l;  sin(w (t - t0)) = cos(w t + Ph)  =>  t0 = -(Ph + 90)/(360 f)
    t0 = -(ph + 90.0) / (360.0 * f)
    return f"""    {name}
    {{
        piston      {zp};
        fixed       {zf};
        rampTime    {T:.15g};
        displacement
        {{
            type        sine;
            amplitude   {amp};
            frequency   {f};
            t0          {t0:.15g};
            scale       {scale};    // displacement along +z (the machine's flow direction), see README
            level       0;
        }}
    }}"""


write('constant/dynamicMeshDict', 'dictionary', f"""// Two pistons; each moves only its own chamber (pistonLinear), start-up per the L5 README
dynamicFvMesh    dynamicMotionSolverFvMesh;
motionSolverLibs (ltnePistonMotion);
motionSolver     pistonLinear;

axis    (0 0 1);

pistons
{{
{piston('hotPiston', zlev[0], Z['hot_chamber']['z'][1], dr['hot_piston']['displacement_amp_m'], dr['hot_piston']['displacement_phase_deg'], 1)}
{piston('coldPiston', zlev[-1], Z['cold_chamber']['z'][0], dr['cold_piston']['displacement_amp_m'], dr['cold_piston']['displacement_phase_deg'], 1)}
}}
""")

# ---- initial fields ------------------------------------------------------------
prof = P['initial_conditions']['T_matrix_profile_z_m__T_K']
zc = []
for k, n in enumerate(order):
    z0, z1 = zlev[k], zlev[k + 1]
    zc += [z0 + (i + 0.5) * (z1 - z0) / ncells[n] for i in range(ncells[n])]


def T_at(z):
    if z <= prof[0][0]:
        return Thot
    if z >= prof[-1][0]:
        return Tcold
    for (za, Ta), (zb, Tb) in zip(prof, prof[1:]):
        if za <= z <= zb:
            return Ta + (Tb - Ta) * (z - za) / (zb - za)


Tinit = [T_at(z) for z in zc]
body = lambda dims, internal, piston_bc: f"""dimensions      {dims};

internalField   {internal};

boundaryField
{{
    hotPiston
    {{
{piston_bc}
    }}
    coldPiston
    {{
{piston_bc}
    }}
    sides
    {{
        type            empty;
    }}
}}
"""
zg = '        type            zeroGradient;'
nonuni = 'nonuniform List<scalar>\n' + str(len(Tinit)) + '\n(\n' + '\n'.join(f'{t:.6f}' for t in Tinit) + '\n)'
write('0.orig/T', 'volScalarField', body('[0 0 0 1 0 0 0]', nonuni, zg))
write('0.orig/Ts', 'volScalarField', body('[0 0 0 1 0 0 0]', nonuni, zg))
write('0.orig/p', 'volScalarField', body('[1 -1 -2 0 0 0 0]', f'uniform {pm}', zg))
write('0.orig/U', 'volVectorField', body('[0 1 -1 0 0 0 0]', 'uniform (0 0 0)',
      '        type            movingWallVelocity;\n        value           uniform (0 0 0);'))

# cell centres of the matrix (for results.py)
with open(os.path.join(case, 'cellCentresZ.txt'), 'w') as fz:
    fz.write('\n'.join(f'{z:.9f}' for z in zc) + '\n')
print(f'mkCase: {len(zc)} cells, matrix refine {refine}, T = {T:.12g} s')
