#!/usr/bin/env python3
"""LRG: real- against ideal-gas helium on the L5 slice (docs/VERIFICATION.md, LRG).

Uses the L5P tools (package pss/, fetched by runLong.sh from the L5P branch at a pinned commit) unchanged, with one
change for a real-gas run: the gas mass is sum eps rho V with the solver's rho (or, where rho is not written, the
real-gas table's rho(p, T), bilinear as in src/ltneRealGas), not p / (R T).

  lrg.py extract <run>                                  fold new cycle-boundary states into <run>/cycles.csv
  lrg.py restartcheck <run> <refdir> <n_r> <n_ref> <out> LRG.1: the ideal-gas continuation against the reference
  lrg.py switch <ideal run> <real run> <n_ref>          prepare the real-gas run at n_ref; writes switch.json
  lrg.py accept <run> <out>                             Amendment A2 test on the real-gas run; exit 0 if accepted
  lrg.py final <case> <out>                             results.csv and the deliverables
"""
import csv, glob, json, os, re, shutil, subprocess, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pss import case as C, cycles as CY, foamio, study as ST  # noqa: E402

L5 = os.path.join(HERE, '..', 'L5_regenSlice')
TABLE = os.path.join(HERE, '..', '..', 'src', 'ltneRealGas', 'tables', 'helium_CoolProp.dat')


# ---- real-gas table (same layout and bilinear interpolation as src/ltneRealGas/realGasTable.H) ----
class Table:
    def __init__(self, path):
        s = open(path).read()
        g = lambda k, f=float: f(re.search(rf'^{k}\s+([0-9.eE+-]+);', s, re.M).group(1))
        self.Tmin, self.dT, self.nT = g('Tmin'), g('dT'), g('nT', int)
        self.pMin, self.dp, self.np = g('pMin'), g('dp'), g('np', int)
        m = re.search(r'^rho\s*\n\s*(\d+)\s*\n\(\s*\n(.*?)\n\);', s, re.M | re.S)
        self.rho = np.array(m.group(2).split(), dtype=float)
        assert self.rho.size == int(m.group(1)) == self.nT * self.np

    def rho_at(self, p, T):
        x = (np.asarray(T) - self.Tmin) / self.dT
        y = (np.asarray(p) - self.pMin) / self.dp
        if np.any(x < 0) or np.any(y < 0) or np.any(x > self.nT - 1) or np.any(y > self.np - 1):
            raise ValueError('state outside the real-gas table')
        i = np.minimum(x.astype(int), self.nT - 2)
        j = np.minimum(y.astype(int), self.np - 2)
        wx, wy = x - i, y - j
        k = i * self.np + j
        f = self.rho
        return (1 - wx) * ((1 - wy) * f[k] + wy * f[k + 1]) + wx * ((1 - wy) * f[k + self.np] + wy * f[k + self.np + 1])


def is_real(case):
    return 'tabulatedRealGas' in open(os.path.join(case, 'constant', 'thermophysicalProperties')).read()


_perfect_gas_mass = C.gas_mass


def gas_mass(case, time, p, T):
    """sum eps rho V; real gas: the solver's rho (or the table), ideal gas: the L5P p / (R T)."""
    if not is_real(case):
        return _perfect_gas_mass(case, time, p, T)
    _, V = foamio.cell_geometry(case, time, C.N, C.AREA)
    rp = os.path.join(case, time, 'rho')
    rho = foamio.read_field(rp, C.N) if os.path.exists(rp) else Table(TABLE).rho_at(p, T)
    return float(np.sum(C.EPS * rho * V)), V


C.gas_mass = gas_mass        # pss.cycles.row_for calls C.gas_mass


def rows(run):
    return {r['cycle']: r for r in ST.natural_rows(run)}


def restartcheck(run, refdir, n_r, n_ref, out):
    a, b = rows(run), rows(refdir)
    tol = ST.tolerances(b[n_ref]['p_mean'])
    worst, at = 0.0, None
    for k in range(n_r + 1, n_ref + 1):
        if k not in a or k not in b:
            raise SystemExit(f'restartcheck: cycle {k} missing ({"run" if k not in a else "reference"})')
        for q in ST.QS:
            e = abs(a[k][q] - b[k][q]) / max(abs(b[k][q]), tol[q])
            if e > worst:
                worst, at = e, (k, q)
    json.dump({'n_r': n_r, 'n_ref': n_ref, 'restart_check_rel': worst, 'worst_at': at}, open(out, 'w'), indent=1)
    print(f'restartcheck: cycles {n_r + 1}-{n_ref}, max relative difference {worst:.3e} at {at}')
    return worst


def switch(ideal, real, n_ref):
    t = [d for d in foamio.time_dirs(ideal) if C.T_CYCLE * (n_ref - 0.5) < float(d) < C.T_CYCLE * (n_ref + 0.5)]
    if len(t) != 1:
        raise SystemExit(f'switch: no unique time directory for cycle {n_ref} in {ideal}: {t}')
    t = t[0]
    if os.path.exists(real):
        shutil.rmtree(real)
    os.makedirs(real)
    for d in ('constant', 'system', '0.orig', t):
        shutil.copytree(os.path.join(ideal, d), os.path.join(real, d))
    for f in ('cellCentresZ.txt', 'Allrun.continue'):
        if os.path.exists(os.path.join(ideal, f)):
            shutil.copy(os.path.join(ideal, f), real)
    # the gas model only: the files mkCase.py --gas real writes for the gas
    tmp = os.path.join(real, '_mkcase')
    os.makedirs(os.path.join(tmp, 'system'))
    shutil.copy(os.path.join(real, 'system', 'controlDict'), os.path.join(tmp, 'system'))
    subprocess.run([sys.executable, os.path.join(L5, 'mkCase.py'), tmp, '--gas', 'real'], check=True,
                   stdout=subprocess.DEVNULL)
    old = open(os.path.join(real, 'constant', 'ltneProperties')).read().splitlines()
    new = open(os.path.join(tmp, 'constant', 'ltneProperties')).read().splitlines()
    extra = [l for l in new if l not in old]
    if len(new) != len(old) + 1 or len(extra) != 1 or not extra[0].startswith('enthalpyReferenceCp'):
        raise SystemExit(f'switch: ltneProperties differs by more than enthalpyReferenceCp: {extra}')
    for f in ('thermophysicalProperties', 'helium_CoolProp.dat', 'ltneProperties'):
        shutil.copy(os.path.join(tmp, 'constant', f), os.path.join(real, 'constant', f))
    cd = os.path.join(real, 'system', 'controlDict')
    txt = open(cd).read()
    if 'ltneRealGas' not in txt:
        txt = re.sub(r'^(application\s+\S+;\n)', r'\1libs            (ltneRealGas);\n', txt, count=1, flags=re.M)
        open(cd, 'w').write(txt)
    shutil.rmtree(tmp)
    # equal initial mean pressure: p and T unchanged; rho removed so the real-gas EOS recomputes it
    removed = [f for f in ('rho', 'rho_0') if os.path.exists(os.path.join(real, t, f))]
    for f in removed:
        os.remove(os.path.join(real, t, f))
    _, f = C.read_state(real, t)
    _, V = foamio.cell_geometry(real, t, C.N, C.AREA)
    M_ideal = float(np.sum(C.EPS * f['p'] / (C.R_GAS * f['T']) * V))
    M_real0 = float(np.sum(C.EPS * Table(TABLE).rho_at(f['p'], f['T']) * V))
    p_mean = float(np.sum(C.EPS * f['p'] * V) / np.sum(C.EPS * V))
    s = {'n_ref': n_ref, 'time': t, 'rho_removed': removed, 'M_ideal': M_ideal, 'M_real0': M_real0,
         'inventory_rel': M_real0 / M_ideal - 1, 'p_mean_switch': p_mean,
         'T_range_K': [float(f['T'].min()), float(f['T'].max())], 'p_range_Pa': [float(f['p'].min()), float(f['p'].max())]}
    json.dump(s, open(os.path.join(real, 'switch.json'), 'w'), indent=1)
    print(f'switch at cycle {n_ref} (t = {t}): inventory real/ideal - 1 = {s["inventory_rel"]:+.4e}, removed {removed}')


def accept(run, out):
    n = len(ST.natural_rows(run))
    if n < 201:            # the A2 fits need 200 per-cycle changes and the remaining distance q(N) - q(N - 50)
        print(f'accept: only {n} real-gas cycles; at least 201 are needed for the Amendment A2 test')
        return 1
    ST.reference(run, out)     # writes reference.json whether or not the test passes
    j = json.load(open(os.path.join(out, 'reference.json')))
    print(f'accept: cycle {j["ref_cycles"]}, r_A2 {j["r_A2"]}, max R_q/tol {j["ref_remaining_max_frac"]:.4f}, '
          f'accepted {j["accepted"]}')
    return 0 if j['accepted'] else 1


def final(case, out):
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
    from resultslib import Results
    os.makedirs(out, exist_ok=True)
    ideal, real, ref = (os.path.join(case, d) for d in ('run_ideal', 'run_real', 'l5p_ref'))
    for src, dst in ((os.path.join(ideal, 'per_cycle.csv'), 'ideal_continuation_per_cycle.csv'),
                     (os.path.join(ideal, 'cycles.csv'), 'ideal_continuation_cycles.csv'),
                     (os.path.join(real, 'per_cycle.csv'), 'real_per_cycle.csv'),
                     (os.path.join(real, 'cycles.csv'), 'real_cycles.csv'),
                     (os.path.join(real, 'switch.json'), 'switch.json'),
                     (os.path.join(case, 'restartcheck.json'), 'restartcheck.json'),
                     (os.path.join(case, 'accept', 'reference.json'), 'real_acceptance.json'),
                     (os.path.join(ref, 'reference.json'), 'ideal_reference.json')):
        if os.path.exists(src):
            shutil.copy(src, os.path.join(out, dst))
    r = Results(out)
    rc = json.load(open(os.path.join(out, 'restartcheck.json')))
    sw = json.load(open(os.path.join(out, 'switch.json')))
    if not os.path.exists(os.path.join(out, 'real_acceptance.json')):
        raise SystemExit('final: no acceptance test was run on the real-gas run (accept/reference.json missing)')
    ra = json.load(open(os.path.join(out, 'real_acceptance.json')))
    ia = json.load(open(os.path.join(out, 'ideal_reference.json')))
    n_ref = sw['n_ref']
    r.add('restart_check_rel', rc['restart_check_rel'], 'restartcheck.json', f'cycles {rc["n_r"] + 1}-{rc["n_ref"]}')
    r.add('inventory_rel', sw['inventory_rel'], 'switch.json', 'inventory_rel')
    rr = ST.natural_rows(real)
    r.add('rg_cycles', rr[-1]['cycle'] - n_ref, 'real_cycles.csv', f'cycles {rr[0]["cycle"]}-{rr[-1]["cycle"]}')
    r.add('rg_remaining_max_frac', ra['ref_remaining_max_frac'], 'real_acceptance.json', 'ref_remaining_max_frac')
    r.add('rg_mass_drift_max', max(abs(x['mass'] - sw['M_real0']) / sw['M_real0'] for x in rr), 'real_cycles.csv',
          f'gas_mass_kg, cycles {rr[0]["cycle"]}-{rr[-1]["cycle"]} vs switch.json M_real0')
    for x, tag in (('Q_hot', 'hot'), ('Q_cold', 'cold')):
        qi, qr = ia['ref'][x], ra['ref'][x]
        Ri = ia['remaining_frac'][x] * ia['tol'][x]
        Rr = ra['remaining_frac'][x] * ra['tol'][x]
        r.add(f'Q_{tag}_ideal_W', qi, 'ideal_reference.json', f'ref.{x} (L5P reference, cycle {ia["ref_cycles"]})')
        r.add(f'Q_{tag}_real_W', qr, 'real_acceptance.json', f'ref.{x} (cycle {ra["ref_cycles"]})')
        r.add(f'dQ_{tag}_rel', (qr - qi) / qi, 'real_acceptance.json', f'vs ideal_reference.json; equal initial mean pressure')
        r.add(f'dQ_{tag}_unc', (Rr + Ri) / abs(qi), 'real_acceptance.json',
              f'remaining distances {Rr:.3e} W (real) + {Ri:.3e} W (ideal)')
    pi = ia['ref']['p_mean']
    r.add('p_mean_drift_rel', (ra['ref']['p_mean'] - pi) / pi, 'real_acceptance.json', 'ref.p_mean vs ideal_reference.json')
    bad = re.compile(r'FOAM FATAL|\bnan\b|\binf\b|Floating point exception|Segmentation fault', re.IGNORECASE)
    banner = re.compile(r'^trapFpe: Floating point exception trapping enabled')
    hits, skipped = [], 0
    for path in sorted(glob.glob(os.path.join(case, 'log.*')) + glob.glob(os.path.join(case, 'run_*', 'log.*'))):
        lines = open(path, errors='replace').readlines()
        for i, l in enumerate(lines):
            if banner.match(l):
                skipped += 1
            elif bad.search(l):
                hits.append(f'{os.path.relpath(path, case)}:{i + 1}')
        with open(os.path.join(out, os.path.relpath(path, case).replace(os.sep, '_') + '.trimmed'), 'w') as f:
            for i, l in enumerate(lines):
                if i < 200 or i >= len(lines) - 100:
                    f.write(f'{i + 1:7d}  {l}')
    r.add('crash_count', len(hits), 'log.*', hits if hits else f'all lines of all logs; {skipped} trapFpe banner lines skipped')
    r.write()


if __name__ == '__main__':
    a = sys.argv
    if a[1] == 'extract':
        print(f'cycles: {CY.extract(a[2])} new cycle(s)')
    elif a[1] == 'restartcheck':
        restartcheck(a[2], a[3], int(a[4]), int(a[5]), a[6])
    elif a[1] == 'switch':
        switch(a[2], a[3], int(a[4]))
    elif a[1] == 'accept':
        sys.exit(accept(a[2], a[3]))
    elif a[1] == 'final':
        final(a[2], a[3])
    else:
        sys.exit(__doc__)
