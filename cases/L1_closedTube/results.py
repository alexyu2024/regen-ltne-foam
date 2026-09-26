#!/usr/bin/env python3
"""L1 metrics. Usage: results.py <outdir>. Definitions: docs/VERIFICATION.md, L1."""
import cmath, math, os, re, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
from resultslib import Results, last_match

case = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
STEPS = {'a': 1000, 'b': 250, 'c': 50, 'd': 10000}
F, AREA, GAMMA = 50.0, 1e-4, 5193.0 / (5193.0 - 8314.46 / 4.0026)

# Copy the cited files, prefixed by run name
for f in ('log.build',):
    if os.path.exists(os.path.join(case, f)):
        shutil.copy(os.path.join(case, f), os.path.join(out, f))
for run in STEPS:
    d = os.path.join(case, 'run_' + run)
    for f in ('log.blockMesh', 'log.ltneFoam'):
        if os.path.exists(os.path.join(d, f)):
            shutil.copy(os.path.join(d, f), os.path.join(out, f'{run}.{f}'))
    dat = os.path.join(d, 'postProcessing', 'ltneDiagnostics', '0', 'ltne.dat')
    if os.path.exists(dat):
        shutil.copy(dat, os.path.join(out, f'{run}.ltne.dat'))

r = Results(out)


def read_diag(name):
    """Columns and rows (line number, dict) of an ltne.dat file."""
    cols, rows = None, []
    path = os.path.join(out, name)
    if not os.path.exists(path):
        return rows
    for i, l in enumerate(open(path)):
        if l.startswith('#'):
            cols = l[1:].split()
        elif l.strip():
            rows.append((i + 1, dict(zip(cols, map(float, l.split())))))
    return rows


def harmonic(t, x):
    """Mean and first-harmonic amplitude at F of samples over one period."""
    n = len(x)
    c = sum(xi * cmath.exp(-2j * math.pi * F * ti) for ti, xi in zip(t, x))
    return sum(x) / n, 2 * abs(c) / n


p1 = {}
for run, n in STEPS.items():
    ln, m = last_match(out, f'{run}.log.ltneFoam', r'^Time = (\S+)$')
    r.add(f'{run}_final_time', None if m is None else float(m.group(1)), f'{run}.log.ltneFoam', ln)

    rows = read_diag(f'{run}.ltne.dat')
    if len(rows) < n + 1:
        for k in ('p1_rel_err', 'mass_cycle', 'energy_cycle', 'p1_iso_rel_err'):
            r.add(f'{run}_{k}', None, f'{run}.ltne.dat', None)
        continue
    cyc = rows[-n:]                      # last cycle, t in (0.04, 0.06]
    start = rows[-n - 1]                 # t = 0.04
    src = f'{cyc[0][0]}-{cyc[-1][0]}'
    t = [v['time'] for _, v in cyc]
    p = [v['pAvg'] for _, v in cyc]
    V = [v['gasVolume'] for _, v in cyc]
    pm, pa = harmonic(t, p)
    Vm, Va = harmonic(t, V)
    p1[run] = pa
    r.add(f'{run}_p1_rel_err', abs(pa / (GAMMA * pm * Va / Vm) - 1), f'{run}.ltne.dat', src)

    C = sum(pi * Vi**GAMMA for pi, Vi in zip(p, V)) / n
    _, pisoa = harmonic(t, [C / Vi**GAMMA for Vi in V])
    r.add(f'{run}_p1_iso_rel_err', abs(pa / pisoa - 1), f'{run}.ltne.dat', src)

    s, e = start[1], cyc[-1][1]
    r.add(f'{run}_mass_cycle', abs(e['gasMass'] - s['gasMass']) / s['gasMass'],
          f'{run}.ltne.dat', [start[0], cyc[-1][0]])
    dE = (e['gasInternalEnergy'] + e['gasKineticEnergy']) - (s['gasInternalEnergy'] + s['gasKineticEnergy'])
    dW = e['boundaryWork'] - s['boundaryWork']
    r.add(f'{run}_energy_cycle', abs(dE - dW) / (pm * Va), f'{run}.ltne.dat', [start[0], cyc[-1][0]] + [src])

    if run == 'd':
        hmin = min(v['pistonSpace_Vmin'] for _, v in cyc) / AREA * 1e3
        hmax = max(v['pistonSpace_Vmax'] for _, v in cyc) / AREA * 1e3
        r.add('d_hmin_mm', hmin, 'd.ltne.dat', src)
        r.add('d_hmax_mm', hmax, 'd.ltne.dat', src)
        r.add('d_h_ratio', hmax / hmin, 'd.ltne.dat', src)

if 'a' in p1 and 'c' in p1:
    r.add('c_p1_vs_a', abs(p1['c'] / p1['a'] - 1), 'c.ltne.dat', 'with a.ltne.dat, rows as c_p1_rel_err and a_p1_rel_err')
else:
    r.add('c_p1_vs_a', None, 'c.ltne.dat', None)

bad = re.compile(r'FOAM FATAL|\bnan\b|\binf\b', re.IGNORECASE)
hits = []
for f in sorted(os.listdir(out)):
    if 'log.' in f:
        for i, l in enumerate(open(os.path.join(out, f), errors='replace')):
            if bad.search(l):
                hits.append(f'{f}:{i + 1}')
r.add('fatal_or_nan_count', len(hits), 'log.*', hits if hits else 'all lines of all logs')
r.write()
