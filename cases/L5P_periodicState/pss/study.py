"""L5P study driver (docs/VERIFICATION.md, L5P).

  python3 -m pss.study noise  <start run> <work> <out>        noise tests N1-N4 from the cycle-40 state
  python3 -m pss.study method <name> <start run> <work> <out> one method (np1 np2 np3 brr3 brr6 gm0 gm3) from
                                                              cycle 40, with its verification cycles
  python3 -m pss.study reference <natural out> <out>          reference acceptance and the natural count
  python3 -m pss.study score <out> <method>...                score finished methods against the reference

<start run> is a run directory holding the cycle-40 state of the natural run (runNatural.sh with L5P_RUN).
Every map evaluation is logged with its quantities in <out>/<name>_evals.csv.
"""
import csv, json, os, sys

import numpy as np

from . import case as C
from . import cyclemap as CM
from . import foamio
from . import methods as MT

START_CYCLE = 40
QS = ['Q_hot', 'Q_cold'] + [f'dT_seg{i}' for i in range(1, 5)] + [f'Ts_seg{i}_mean' for i in range(1, 5)] \
    + ['T_joint', 'p_mean']
TOL = dict(Q_hot=0.005, Q_cold=0.0005, T_joint=0.02, **{f'dT_seg{i}': 0.02 for i in range(1, 5)},
           **{f'Ts_seg{i}_mean': 0.02 for i in range(1, 5)})
P_REL, DRIFT, REMAIN = 1e-3, 1.5e-3, 0.2
R_L5D = 0.99670
# Amendment A2 (docs/VERIFICATION.md): r_A2 = slowest valid L5D-style fit over all quantities, windows 100 and 200;
# drift tolerance 0.45 tol (1 - r_A2) per cycle
A2_WINDOWS, A2_DRIFT = (100, 200), 0.45
WORKERS = int(os.environ.get('L5P_WORKERS', '3'))


def tolerances(p_ref):
    t = dict(TOL)
    t['p_mean'] = P_REL * p_ref
    return t


def start_state(run):
    times = [t for t in foamio.time_dirs(run) if round(float(t) * C.F) == START_CYCLE]
    if not times:
        sys.exit(f'{run}: no cycle-{START_CYCLE} time directory')
    return CM.State(run, times[0])


def write_csv(path, rows, fields=None):
    fields = fields or list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()})


# ---------------------------------------------------------------- methods
def method(name, start_run, work, out):
    os.makedirs(out, exist_ok=True)
    # the methods' own drift test uses r_A2 of the accepted natural reference (Amendment A2); it is a property of
    # the slow mode, not of the reference values, which the methods never see
    refj = json.load(open(os.path.join(out, 'reference.json')))
    if not refj.get('accepted'):
        sys.exit('no accepted reference (L5P.3): methods do not start')
    r_sys = refj['r_A2']
    s0 = start_state(start_run)
    C.check_eos(start_run)
    cmap = CM.CycleMap(os.path.join(work, name), s0.mass, workers=WORKERS)
    run = MT.Run(cmap, name)
    evals, vrounds = [], []

    def record(states):
        for s in states:
            q = s.quantities()
            evals.append({'count': cmap.count, 'dir': os.path.basename(s.case), **q})

    # every evaluation is recorded as it finishes
    _orig = cmap.run_many

    def run_many(jobs):
        res = _orig(jobs)
        record(res)
        cmap.cleanup(keep=[j[0] for j in jobs] + res)
        return res
    cmap.run_many = run_many

    def verify(run, pt):
        """NV natural cycles from pt; the method's own D and NR test (no reference)."""
        rows, s = [], None
        for j in range(MT.NV):
            s = run.phi(pt, f'v{len(vrounds)}_{j}')
            pt = (s, None)
            rows.append(s.quantities())
        ok, det = MT.drift_checks(rows, drift_tolerances(tolerances(rows[-1]['p_mean']), r_sys))
        vrounds.append({'round': len(vrounds) + 1, 'end_count': run.used(), 'self_ok': ok,
                        'first_cycle_count': run.used() - MT.NV + 1,
                        'fails': ';'.join(q for q, d in det.items() if not (d[2] and d[3]))})
        return ok, pt

    kind, par = name.rstrip('0123456789'), int(name.lstrip('abcdefghijklmnopqrstuvwxyz') or 0)
    fn = {'np': MT.newton_picard, 'brr': MT.brr, 'gm': MT.graves_morris}[kind]
    status = 'ended'
    try:
        fn(run, (s0, None), par, verify)
    except MT.Budget:
        status = 'budget'
    write_csv(os.path.join(out, f'{name}_hist.csv'), run.hist)
    write_csv(os.path.join(out, f'{name}_evals.csv'), evals)
    write_csv(os.path.join(out, f'{name}_verify.csv'), vrounds or [{'round': 0}])
    summary = {'name': name, 'status': status, 'method_and_verify_cycles': run.used(),
               'total': START_CYCLE + run.used(), 'verification_rounds': len(vrounds),
               'jump_mass_err_max': getattr(cmap, 'jump_mass_err', 0.0),
               'crash_count': len(cmap.crash_hits), 'crash_hits': cmap.crash_hits[:20],
               'log_lines_scanned': cmap.log_lines, 'trapFpe_banners_skipped': cmap.banners,
               'mass_err_max': max(abs(e['mass'] - s0.mass) / s0.mass for e in evals) if evals else None}
    json.dump(summary, open(os.path.join(out, f'{name}_summary.json'), 'w'), indent=1)
    print(json.dumps(summary))


# ---------------------------------------------------------------- noise
def noise(start_run, work, out):
    os.makedirs(out, exist_ok=True)
    s0 = start_state(start_run)
    cmap = CM.CycleMap(os.path.join(work, 'noise'), s0.mass, workers=WORKERS)

    def xmean(s):
        Tm, Tsm = C.cycle_mean_profiles(s.case, s.time)
        return np.concatenate([Tsm[C.MATRIX], Tm])
    rows = []
    a, b = cmap.run_many([(s0, None, 'N1a'), (s0, None, 'N1b')])
    rows.append({'test': 'N1', 'max_dx_K': float(np.max(np.abs(a.x - b.x))),
                 'max_dxmean_K': float(np.max(np.abs(xmean(a) - xmean(b))))})
    # N2: two cycles continuous from cycle 40 against 1 + 1 with a restart
    import shutil, subprocess
    d = os.path.join(work, 'noise', 'N2cont')
    cmap.prepare(s0, None, 'N2cont')
    cd = os.path.join(d, 'system', 'controlDict')
    txt = open(cd).read().replace(f'endTime         {repr((START_CYCLE + 1) / C.F)};',
                                  f'endTime         {repr((START_CYCLE + 2) / C.F)};')
    open(cd, 'w').write(txt)
    cont = cmap._run(d)
    cmap.count += 2
    b2 = cmap.run(a, None, 'N2b')
    rows.append({'test': 'N2', 'max_dx_K': float(np.max(np.abs(cont.x - b2.x))),
                 'max_dxmean_K': float(np.max(np.abs(xmean(cont) - xmean(b2))))})
    c = cmap.run(s0, s0.x.copy(), 'N3')
    rows.append({'test': 'N3', 'max_dx_K': float(np.max(np.abs(c.x - a.x))),
                 'max_dxmean_K': float(np.max(np.abs(xmean(c) - xmean(a))))})
    # N4: finite-difference products along the first natural difference and a random direction
    dirs = {'natural': a.x - s0.x, 'random': np.random.default_rng(0).standard_normal(C.NX)}
    eps = [1, 0.3, 0.1, 0.03, 0.01, 1e-3, 1e-4, 1e-5]
    floor = None
    for dn, v in dirs.items():
        v = v / float(np.max(np.abs(v)))
        res = cmap.run_many([(s0, s0.x + e * v, f'N4{dn}{i}') for i, e in enumerate(eps)])
        Mv = [(r.x - a.x) / e for r, e in zip(res, eps)]
        Mvm = [(xmean(r) - xmean(a)) / e for r, e in zip(res, eps)]
        for i, e in enumerate(eps):
            row = {'test': f'N4_{dn}', 'eps_K': e, 'Mv_norm': float(np.linalg.norm(Mv[i])),
                   'vMv': float(v @ Mv[i] / (v @ v))}
            if i:
                row['rel_change'] = float(np.linalg.norm(Mv[i] - Mv[i - 1]) / np.linalg.norm(Mv[i - 1]))
                row['rel_change_mean'] = float(np.linalg.norm(Mvm[i] - Mvm[i - 1]) / np.linalg.norm(Mvm[i - 1]))
                floor = row['rel_change'] if floor is None else min(floor, row['rel_change'])
            rows.append(row)
    write_csv(os.path.join(out, 'noise.csv'), rows,
              ['test', 'eps_K', 'max_dx_K', 'max_dxmean_K', 'Mv_norm', 'vMv', 'rel_change', 'rel_change_mean'])
    json.dump({'cycles': cmap.count, 'N4_floor': floor, 'crash_count': len(cmap.crash_hits),
               'crash_hits': cmap.crash_hits[:20], 'log_lines_scanned': cmap.log_lines}, open(os.path.join(out, 'noise_summary.json'), 'w'))
    print(open(os.path.join(out, 'noise.csv')).read())


# ---------------------------------------------------------------- reference and natural count
def natural_rows(nat_out):
    pc = {int(float(r['cycle'])): r for r in csv.DictReader(open(os.path.join(nat_out, 'per_cycle.csv')))}
    cy = {int(r['cycle']): r for r in csv.DictReader(open(os.path.join(nat_out, 'cycles.csv')))}
    rows = []
    for k in sorted(set(pc) & set(cy)):
        a, b = pc[k], cy[k]
        q = {'cycle': k, 'Q_hot': float(a['Qhot_gas']) + float(a['Qhot_solid']),
             'Q_cold': float(a['Qcold_gas']) + float(a['Qcold_solid']), 'T_joint': float(a['Tjoint_mean']),
             'p_mean': float(b['p_mean_Pa']), 'mass': float(b['gas_mass_kg'])}
        for i in range(1, 5):
            q[f'dT_seg{i}'] = float(b[f'dT_seg{i}'])
            q[f'Ts_seg{i}_mean'] = float(b[f'Ts_seg{i}_mean'])
        rows.append(q)
    return rows


def r_fit(values, n):
    """L5D r_fit over the last n per-cycle changes: exp of the least-squares slope of ln|d_k|. None unless d_k
    keeps one sign over the window and r < 1 (Amendment A2)."""
    import math
    d = [values[i] - values[i - 1] for i in range(len(values) - n, len(values))]
    if len(d) < n or any(x == 0 for x in d) or len({x > 0 for x in d}) > 1:
        return None
    k = range(n)
    y = [math.log(abs(x)) for x in d]
    mk, my = (n - 1) / 2, sum(y) / n
    r = math.exp(sum((a - mk) * (b - my) for a, b in zip(k, y)) / sum((a - mk) ** 2 for a in k))
    return r if r < 1 else None


def r_a2(rows):
    """(r_A2, {quantity: {window: fit}}): the slowest valid fit over all quantities and both windows."""
    fits = {q: {n: r_fit([r[q] for r in rows], n) for n in A2_WINDOWS} for q in QS}
    valid = [f for d in fits.values() for f in d.values() if f is not None]
    return (max(valid) if valid else None), fits


def drift_tolerances(tol, r):
    """Amendment A2: 0.45 tol (1 - r) per cycle."""
    return {q: A2_DRIFT * tol[q] * (1 - r) for q in QS}


def passes_V(rows, ref, tol, k_index, drift_tol):
    """V(k) on a list of per-cycle rows; rows[k_index] is cycle k. Returns (E, D, NR) booleans."""
    v = rows[k_index + 1:k_index + 1 + MT.NV]
    if len(v) < MT.NV:
        return None
    e = all(abs(r[q] - ref[q]) <= tol[q] for r in v[MT.SKIP:] for q in QS)
    ok, det = MT.drift_checks(v, drift_tol)
    return e, all(d[2] for d in det.values()), all(d[3] for d in det.values())


def reference(nat_out, out):
    os.makedirs(out, exist_ok=True)
    rows = natural_rows(nat_out)
    n = rows[-1]['cycle']
    ref = rows[-1]
    tol = tolerances(ref['p_mean'])
    back = {r['cycle']: r for r in rows}[n - 50]
    # the registered rule (r = 0.99670), kept on record
    remain_reg = {q: abs(ref[q] - back[q]) / 50 * R_L5D / (1 - R_L5D) / tol[q] for q in QS}
    # Amendment A2: the measured late decay ratio
    r, fits = r_a2(rows)
    remain = {q: (abs(ref[q] - back[q]) / 50 * r / (1 - r) / tol[q]) if r else float('inf') for q in QS}
    dtol = drift_tolerances(tol, r) if r else None
    M0 = rows[0]['mass']
    k_nat = None
    accepted = max(remain.values()) <= REMAIN
    for i, row in enumerate(rows):
        if not accepted or row['cycle'] < START_CYCLE:
            continue
        res = passes_V(rows, ref, tol, i, dtol)
        if res is None:
            break
        if all(res):
            k_nat = row['cycle']
            break
    summ = {'ref_cycles': n, 'rule': 'Amendment A2', 'accepted': accepted, 'r_A2': r,
            'r_fits': {q: {str(w): f for w, f in d.items()} for q, d in fits.items()},
            'ref_remaining_max_frac': max(remain.values()), 'remaining_frac': remain,
            'ref_remaining_max_frac_registered_rule': max(remain_reg.values()),
            'remaining_frac_registered_rule': remain_reg, 'drift_tol': dtol,
            'ref': {q: ref[q] for q in QS}, 'tol': tol, 'nat_k': k_nat,
            'nat_total': None if k_nat is None else k_nat + MT.NV,
            'nat_within_from': None if k_nat is None else k_nat + MT.SKIP + 1,
            'nat_mass_drift_max': max(abs(r['mass'] - M0) / M0 for r in rows)}
    # distance to the reference per cycle, in units of tol (for the plots and the conclusion)
    write_csv(os.path.join(out, 'natural_distance.csv'),
              [{'cycle': r['cycle'], **{q: abs(r[q] - ref[q]) / tol[q] for q in QS}} for r in rows])
    json.dump(summ, open(os.path.join(out, 'reference.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))


def score(out, names):
    refj = json.load(open(os.path.join(out, 'reference.json')))
    ref, tol = refj['ref'], refj['tol']
    for name in names:
        summ = json.load(open(os.path.join(out, f'{name}_summary.json')))
        ev = list(csv.DictReader(open(os.path.join(out, f'{name}_evals.csv'))))
        rows = [{q: float(e[q]) for q in QS} for e in ev[-MT.NV:]]
        if summ['status'] != 'ended' or len(rows) < MT.NV:
            res = (False, False, False)
        else:
            res = passes_V([None] + rows, ref, tol, 0, refj['drift_tol'])
        m_ok = max(summ['mass_err_max'] or 0, summ['jump_mass_err_max'] or 0) <= 1e-9
        summ.update(E=res[0], D=res[1], NR=res[2], M=m_ok, passed=int(all(res) and m_ok),
                    final_dist={q: abs(rows[-1][q] - ref[q]) / tol[q] for q in QS} if rows else None)
        json.dump(summ, open(os.path.join(out, f'{name}_summary.json'), 'w'), indent=1)
        print(name, json.dumps({k: summ[k] for k in ('status', 'total', 'E', 'D', 'NR', 'M', 'passed')}))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'noise':
        noise(*sys.argv[2:5])
    elif cmd == 'method':
        method(*sys.argv[2:6])
    elif cmd == 'reference':
        reference(*sys.argv[2:4])
    elif cmd == 'score':
        score(sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)
