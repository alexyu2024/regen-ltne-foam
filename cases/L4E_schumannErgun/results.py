#!/usr/bin/env python3
"""L4E metrics. Usage: results.py <outdir>.
Definitions: docs/VERIFICATION.md, L4E (Schumann single blow with Ergun drag)."""
import math, os, re, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
from resultslib import Results, last_match

case = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]
CP, W, P0, MU = 5193.0, 4.0026, 2e6, 1.99e-5
R = 8314.462618 / W
T0, T1, DT = 300.0, 310.0, 10.0
EPS, DP, L, AREA, DX = 0.4, 5e-4, 0.1, 1e-4, 0.1 / 200
HA, CS = 25.0 * 6.0 * (1.0 - EPS) / DP, (1.0 - EPS) * 7900.0 * 250.0
D_ERGUN = 150.0 * (1.0 - EPS) ** 2 / (EPS ** 3 * DP ** 2)      # 1/m2
F_ERGUN = 1.75 * (1.0 - EPS) / (EPS ** 3 * DP)                 # 1/m (= C2 / 2)
RHO1 = P0 / (R * T1)
G = RHO1 * 0.1
XI_PER_M, ETA_RATE = HA / (G * CP), HA / CS
PROBES = (0.05025, 0.09975)     # cell centres, in the order of probeLocations

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


def table(name):
    """[(line number, [floats])] of the data rows of an output file."""
    rows = []
    path = os.path.join(out, name)
    if os.path.exists(path):
        for i, l in enumerate(open(path)):
            if l.strip() and not l.startswith('#'):
                rows.append((i + 1, [float(v) for v in l.split()]))
    return rows


def main():
    os.makedirs(out, exist_ok=True)
    for f in ('log.build', 'log.blockMesh', 'log.ltneFoam'):
        if os.path.exists(os.path.join(case, f)):
            shutil.copy(os.path.join(case, f), os.path.join(out, f))
    for src, dst in (('postProcessing/probesTTs/0/T', 'probe_T.dat'),
                     ('postProcessing/probesTTs/0/Ts', 'probe_Ts.dat'),
                     ('postProcessing/inletP/0/surfaceFieldValue.dat', 'inletP.dat'),
                     ('postProcessing/inletFlux/0/surfaceFieldValue.dat', 'inletFlux.dat'),
                     ('postProcessing/bedRho/0/volFieldValue.dat', 'bedRho.dat')):
        if os.path.exists(os.path.join(case, src)):
            shutil.copy(os.path.join(case, src), os.path.join(out, dst))
    r = Results(out)
    ln, m = last_match(out, 'log.ltneFoam', r'^Time = (\S+)$')
    r.add('final_time', None if m is None else float(m.group(1)), 'log.ltneFoam', ln)
    bad, src = 0, None
    for f in ('log.blockMesh', 'log.ltneFoam'):
        if os.path.exists(os.path.join(out, f)):
            for i, l in enumerate(open(os.path.join(out, f))):
                if re.search(r'FOAM FATAL|\bnan\b|\binf\b', l, re.I):
                    bad += 1
                    src = src or f'{f}:{i + 1}'
    r.add('fatal_or_nan_count', bad, 'log.ltneFoam', src or 'all lines of log.blockMesh and log.ltneFoam')

    # Gas and solid breakthrough curves at the two probes
    for key, fname, col in (('gas_err', 'probe_T.dat', 0), ('solid_err', 'probe_Ts.dat', 1)):
        rows = table(fname)
        if not rows:
            r.add(key, None, fname, None)
            continue
        err, where = 0.0, None
        for lno, v in rows:
            t = v[0]
            if col == 0 and t < 2.0:      # gas: skip the first 2 s, as in L4
                continue
            for x, T in zip(PROBES, v[1:]):
                e = abs((T - T0) / DT - schumann(XI_PER_M * x, eta_at(x, t))[col])
                if e > err:
                    err, where = e, f'line {lno}, x = {x} m, t = {t:g} s'
        r.add(key, err, fname, f'{rows[0][0]}-{rows[-1][0]}; max at {where}')

    # Bed pressure drop against Ergun
    pin, flux, rho = table('inletP.dat'), table('inletFlux.dat'), table('bedRho.dat')
    if pin and flux and rho:
        n = min(len(pin), len(flux), len(rho))
        err, where, last = 0.0, None, None
        for (lp, vp), (_, vf), (_, vr) in zip(pin[:n], flux[:n], rho[:n]):
            t = vp[0]
            if t < 2.0:
                continue
            g = abs(vf[1]) / AREA
            u = g / vr[1]
            dp_e = (L - 0.5 * DX) * (MU * D_ERGUN * u + F_ERGUN * vr[1] * u * u)
            e = abs((vp[1] - P0) / dp_e - 1.0)
            if e > err:
                err, where = e, f'line {lp}, t = {t:g} s'
            last = (lp, vp[1] - P0, dp_e, g * DP / MU)
        r.add('dp_rel_err', err, 'inletP.dat', f'{pin[0][0]}-{pin[n - 1][0]}; max at {where}')
        r.add('dp_final_Pa', last[1], 'inletP.dat', f'line {last[0]}')
        r.add('dp_ergun_final_Pa', last[2], 'inletP.dat', f'line {last[0]}; Ergun with bedRho.dat and inletFlux.dat')
        r.add('Re_p', last[3], 'inletFlux.dat', f'G d_p / mu, line {last[0]}')
    else:
        for k in ('dp_rel_err', 'dp_final_Pa', 'dp_ergun_final_Pa', 'Re_p'):
            r.add(k, None, 'inletP.dat', None)
    r.write()


if __name__ == '__main__':
    main()
