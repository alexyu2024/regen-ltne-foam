#!/usr/bin/env python3
"""L2 metrics. Usage: results.py <outdir>. Definitions: docs/VERIFICATION.md, L2."""
import os, re, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
from resultslib import Results, last_match

case = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
RUNS = ['v1', 'v2', 'v3', 'v4']
L, MU, D, F, AREA = 0.02, 1.99e-5, 1e9, 1e5, 1e-4
FOS = {'inletP': 'surfaceFieldValue.dat', 'outletP': 'surfaceFieldValue.dat',
       'inletFlux': 'surfaceFieldValue.dat', 'porousRho': 'volFieldValue.dat'}

if os.path.exists(os.path.join(case, 'log.build')):
    shutil.copy(os.path.join(case, 'log.build'), os.path.join(out, 'log.build'))
for run in RUNS:
    d = os.path.join(case, 'run_' + run)
    for f in ('log.blockMesh', 'log.setFields', 'log.ltneFoam'):
        if os.path.exists(os.path.join(d, f)):
            shutil.copy(os.path.join(d, f), os.path.join(out, f'{run}.{f}'))
    for fo, dat in FOS.items():
        src = os.path.join(d, 'postProcessing', fo, '0', dat)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(out, f'{run}.{fo}.dat'))

r = Results(out)


def series(name):
    """[(line number, time, value)] of a one-field function-object .dat file."""
    path = os.path.join(out, name)
    rows = []
    if os.path.exists(path):
        for i, l in enumerate(open(path)):
            if l.strip() and not l.startswith('#'):
                t, v = l.split()[:2]
                rows.append((i + 1, float(t), float(v)))
    return rows


for run in RUNS:
    ln, m = last_match(out, f'{run}.log.ltneFoam', r'^Time = (\S+)$')
    r.add(f'{run}_final_time', None if m is None else float(m.group(1)), f'{run}.log.ltneFoam', ln)

    s = {fo: series(f'{run}.{fo}.dat') for fo in FOS}
    if not all(s.values()):
        for k in ('rel_err', 'ratio', 'steady', 'dp'):
            r.add(f'{run}_{k}', None, f'{run}.inletP.dat', None)
        continue
    last = {fo: v[-1] for fo, v in s.items()}
    dp = last['inletP'][2] - last['outletP'][2]
    G = abs(last['inletFlux'][2]) / AREA
    rho = last['porousRho'][2]
    u = G / rho
    dp_cf = L * (MU * D * u + F * rho * u**2 / 2)
    src = [f'{run}.{fo}.dat:{last[fo][0]}' for fo in FOS]
    r.add(f'{run}_dp', dp, f'{run}.inletP.dat', f'{last["inletP"][0]} minus {src[1]}')
    r.add(f'{run}_rel_err', abs(dp / dp_cf - 1), f'{run}.inletP.dat', f'{last["inletP"][0]} with ' + ', '.join(src[1:]))
    r.add(f'{run}_ratio', (F * rho * u / 2) / (MU * D), f'{run}.porousRho.dat',
          f'{last["porousRho"][0]} with {src[2]}')

    i45 = min(range(len(s['inletP'])), key=lambda i: abs(s['inletP'][i][1] - 0.045))
    dp45 = s['inletP'][i45][2] - s['outletP'][i45][2]
    r.add(f'{run}_steady', abs(dp - dp45) / abs(dp), f'{run}.inletP.dat',
          f'{s["inletP"][i45][0]},{last["inletP"][0]} with {run}.outletP.dat:{s["outletP"][i45][0]},{last["outletP"][0]}')

bad = re.compile(r'FOAM FATAL|\bnan\b|\binf\b', re.IGNORECASE)
hits = []
for f in sorted(os.listdir(out)):
    if 'log.' in f:
        for i, l in enumerate(open(os.path.join(out, f), errors='replace')):
            if bad.search(l):
                hits.append(f'{f}:{i + 1}')
r.add('fatal_or_nan_count', len(hits), 'log.*', hits if hits else 'all lines of all logs')
r.write()
