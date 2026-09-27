#!/usr/bin/env python3
"""L4 metrics. Usage: results.py <outdir>. Definitions: docs/VERIFICATION.md, L4 (Schumann single blow)."""
import math, os, re, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
from resultslib import Results, last_match

case = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
CP, W, P0 = 5193.0, 4.0026, 2e6
R = 8314.462618 / W
T0, T1, DT = 300.0, 310.0, 10.0
EPS, L, AREA = 0.7, 0.1, 1e-4
HA, CS = 20.0 * 8000.0, 0.3 * 7900.0 * 500.0
RHO1 = P0 / (R * T1)
G = RHO1 * 0.1
XI_PER_M, ETA_RATE = HA / (G * CP), HA / CS

for f in ('log.build', 'log.blockMesh', 'log.ltneFoam'):
    if os.path.exists(os.path.join(case, f)):
        shutil.copy(os.path.join(case, f), os.path.join(out, f))
for src, dst in (('postProcessing/ltneDiagnostics/0/ltne.dat', 'ltne.dat'),
                 ('postProcessing/outletT/0/surfaceFieldValue.dat', 'outletT.dat')):
    if os.path.exists(os.path.join(case, src)):
        shutil.copy(os.path.join(case, src), os.path.join(out, dst))


def poisson(a, kmax):
    p = [math.exp(-a)]
    for k in range(1, kmax + 1):
        p.append(p[-1] * a / k)
    return p


def schumann(xi, eta):
    """(theta_g, theta_s) at xi, eta >= 0."""
    if eta <= 0:
        return math.exp(-xi), 0.0
    kmax = int(xi + eta + 12 * math.sqrt(xi + eta + 1) + 40)
    px, pe = poisson(xi, kmax), poisson(eta, kmax)
    ts = g = cdf = 0.0
    for k in range(kmax + 1):
        cdf += pe[k]
        ts += px[k] * (1.0 - cdf)
        g += px[k] * pe[k]
    return g + ts, ts


def eta_at(x, t):
    return ETA_RATE * (t - EPS * RHO1 * x / G)


r = Results(out)
ln, m = last_match(out, 'log.ltneFoam', r'^Time = (\S+)$')
r.add('final_time', None if m is None else float(m.group(1)), 'log.ltneFoam', ln)

# Outlet breakthrough curve
rows = []
if os.path.exists(os.path.join(out, 'outletT.dat')):
    for i, l in enumerate(open(os.path.join(out, 'outletT.dat'))):
        if l.strip() and not l.startswith('#'):
            t, v = l.split()[:2]
            rows.append((i + 1, float(t), float(v)))
if rows:
    xiL = XI_PER_M * L
    err, t_half, prev = 0.0, None, (0.0, 0.0)
    for _, t, T in rows:
        th = (T - T0) / DT
        if t >= 2.0:
            err = max(err, abs(th - schumann(xiL, eta_at(L, t))[0]))
        if t_half is None and th >= 0.5:
            t_half = prev[0] + (0.5 - prev[1]) * (t - prev[0]) / (th - prev[1])
        prev = (t, th)
    src = f'{rows[0][0]}-{rows[-1][0]}'
    r.add('out_err', err, 'outletT.dat', src)
    r.add('t_half', t_half, 'outletT.dat', src)
    # exact t_half by bisection on the outlet solution
    lo, hi = 1.0, 150.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if schumann(xiL, eta_at(L, mid))[0] < 0.5 else (lo, mid)
    r.add('t_half_exact', 0.5 * (lo + hi), 'outletT.dat', 'computed from the inputs')
else:
    for k in ('out_err', 't_half', 't_half_exact'):
        r.add(k, None, 'outletT.dat', None)

# Solid energy and whole-run energy balance
diag, cols = [], None
if os.path.exists(os.path.join(out, 'ltne.dat')):
    for i, l in enumerate(open(os.path.join(out, 'ltne.dat'))):
        if l.startswith('#'):
            cols = l[1:].split()
        elif l.strip():
            diag.append((i + 1, dict(zip(cols, map(float, l.split())))))
if diag and rows:
    N, V = 400, AREA * L
    Es0 = diag[0][1]['solidEnergy']
    es_err = 0.0
    for _, v in diag[::100]:
        t = v['time']
        s = 0.0
        for j in range(N + 1):
            x = L * j / N
            w = 1 if j in (0, N) else (4 if j % 2 else 2)
            s += w * schumann(XI_PER_M * x, eta_at(x, t))[1]
        integral = s * (L / N) / 3.0
        es_err = max(es_err, abs(v['solidEnergy'] - Es0 - CS * AREA * DT * integral) / (CS * V * DT))
    r.add('Es_err', es_err, 'ltne.dat', f'{diag[0][0]}-{diag[-1][0]} (every 100th row)')

    def E(v):
        return v['gasInternalEnergy'] + v['gasKineticEnergy'] + v['solidEnergy']
    inflow = 0.0
    pts = [(0.0, T0)] + [(t, T) for _, t, T in rows]
    for (ta, Ta), (tb, Tb) in zip(pts, pts[1:]):
        inflow += G * AREA * CP * (T1 - 0.5 * (Ta + Tb)) * (tb - ta)
    r.add('energy_err', abs(E(diag[-1][1]) - E(diag[0][1]) - inflow) / (CS * V * DT), 'ltne.dat',
          f'{diag[0][0]},{diag[-1][0]} with outletT.dat:{rows[0][0]}-{rows[-1][0]}')
else:
    for k in ('Es_err', 'energy_err'):
        r.add(k, None, 'ltne.dat', None)

bad = re.compile(r'FOAM FATAL|\bnan\b|\binf\b', re.IGNORECASE)
hits = []
for f in sorted(os.listdir(out)):
    if 'log.' in f:
        for i, l in enumerate(open(os.path.join(out, f), errors='replace')):
            if bad.search(l):
                hits.append(f'{f}:{i + 1}')
r.add('fatal_or_nan_count', len(hits), 'log.*', hits if hits else 'all lines of all logs')
r.write()
