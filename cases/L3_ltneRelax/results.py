#!/usr/bin/env python3
"""L3 metrics. Usage: results.py <outdir>. Definitions: docs/VERIFICATION.md, L3."""
import math, os, re, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
from resultslib import Results, last_match

case = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
CP, CV = 5193.0, 5193.0 - 8314.462618 / 4.0026
EPS, RHOS, HA, TG0, TS0 = 0.7, 7900.0, 1000.0 * 24000.0, 300.0, 320.0
RUNS = {'r': 500.0, 'b': 5.0}

if os.path.exists(os.path.join(case, 'log.build')):
    shutil.copy(os.path.join(case, 'log.build'), os.path.join(out, 'log.build'))
for run in RUNS:
    d = os.path.join(case, 'run_' + run)
    for f in ('log.blockMesh', 'log.ltneFoam'):
        if os.path.exists(os.path.join(d, f)):
            shutil.copy(os.path.join(d, f), os.path.join(out, f'{run}.{f}'))
    dat = os.path.join(d, 'postProcessing', 'ltneDiagnostics', '0', 'ltne.dat')
    if os.path.exists(dat):
        shutil.copy(dat, os.path.join(out, f'{run}.ltne.dat'))

r = Results(out)
for run, cs in RUNS.items():
    ln, m = last_match(out, f'{run}.log.ltneFoam', r'^Time = (\S+)$')
    r.add(f'{run}_final_time', None if m is None else float(m.group(1)), f'{run}.log.ltneFoam', ln)

    path = os.path.join(out, f'{run}.ltne.dat')
    rows, cols = [], None
    if os.path.exists(path):
        for i, l in enumerate(open(path)):
            if l.startswith('#'):
                cols = l[1:].split()
            elif l.strip():
                rows.append((i + 1, dict(zip(cols, map(float, l.split())))))
    if len(rows) < 2:
        for k in ('err_g', 'err_s', 'energy', 'Teq'):
            r.add(f'{run}_{k}', None, f'{run}.ltne.dat', None)
        continue

    first = rows[0][1]
    V = first['gasVolume'] / EPS
    rho = first['gasMass'] / first['gasVolume']
    Cg, Cs = EPS * rho * CV, (1 - EPS) * RHOS * cs
    Teq = (Cg * TG0 + Cs * TS0) / (Cg + Cs)
    tau = 1 / (HA * (1 / Cg + 1 / Cs))
    E0 = first['gasInternalEnergy'] + first['gasKineticEnergy'] + first['solidEnergy']
    Q = Cg * V * abs(TG0 - Teq)
    eg = es = ee = 0.0
    for _, v in rows:
        t = v['time']
        Tg = (v['gasInternalEnergy'] / v['gasMass'] + CP * 298.15) / CV
        Ts = v['solidEnergy'] / (Cs * V)
        x = math.exp(-t / tau)
        eg = max(eg, abs(Tg - (Teq + (TG0 - Teq) * x)) / abs(TS0 - TG0))
        es = max(es, abs(Ts - (Teq + (TS0 - Teq) * x)) / abs(TS0 - TG0))
        E = v['gasInternalEnergy'] + v['gasKineticEnergy'] + v['solidEnergy']
        ee = max(ee, abs(E - E0) / Q)
    src = f'{rows[0][0]}-{rows[-1][0]}'
    r.add(f'{run}_err_g', eg, f'{run}.ltne.dat', src)
    r.add(f'{run}_err_s', es, f'{run}.ltne.dat', src)
    r.add(f'{run}_energy', ee, f'{run}.ltne.dat', src)
    last = rows[-1][1]
    r.add(f'{run}_Teq', (last['gasInternalEnergy'] / last['gasMass'] + CP * 298.15) / CV,
          f'{run}.ltne.dat', rows[-1][0])

bad = re.compile(r'FOAM FATAL|\bnan\b|\binf\b', re.IGNORECASE)
hits = []
for f in sorted(os.listdir(out)):
    if 'log.' in f:
        for i, l in enumerate(open(os.path.join(out, f), errors='replace')):
            if bad.search(l):
                hits.append(f'{f}:{i + 1}')
r.add('fatal_or_nan_count', len(hits), 'log.*', hits if hits else 'all lines of all logs')
r.write()
