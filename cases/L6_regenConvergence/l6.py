#!/usr/bin/env python3
"""L6 post-processing. Definitions: docs/VERIFICATION.md, L6.

  l6.py summarise <run dir> <steps per cycle>   fold new monitor rows into <run dir>/per_cycle.csv
  l6.py periodic <run dir>                      exit 0: periodic (cycle written to <run dir>/periodic.txt);
                                                2: cap of 300 cycles reached without it; 1: not yet
  l6.py final <case> <out>                      write the deliverables and results.csv into <out>

The per-cycle quantities reuse the L5 definitions (cases/L5_regenSlice/results.py).
"""
import csv, glob, importlib.util, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('l5results', os.path.join(HERE, '..', 'L5_regenSlice', 'results.py'))
L5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L5)

RUNS = ['G1', 'G2', 'G3', 'T2']
QOIS = ['H_hot', 'H_joint', 'H_cold', 'Qgs_abs', 'dp_amp']
FIELDS = L5.FIELDS + ['closure4', 'Qgs_net', 'Qgs_abs']
MIN_CYCLES, MAX_CYCLES, TOL, PAIRS = 40, 300, 1e-3, 5
FORMAL_ORDER, R = 2.0, 2.0


def summarise_cycle(k, rows):
    d = L5.summarise_cycle(k, rows)
    m = lambda key: sum(r[key] for r in rows) / len(rows)
    d['closure4'] = d['W_hot'] + d['W_cold'] + d['Qhot_gas'] + d['Qcold_gas']
    d['Qgs_net'], d['Qgs_abs'] = m('matrix_Qgs'), m('matrix_Qgs_abs')
    return d


def load(run):
    path = os.path.join(run, 'per_cycle.csv')
    if not os.path.exists(path):
        return []
    return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(open(path))]


def summarise(run, steps):
    have = {int(r['cycle']) for r in load(run)}
    by = {}
    for r in L5.monitor_rows(run):
        by.setdefault(L5.cycle_of(r['time']), []).append(r)
    new = [summarise_cycle(k, v) for k, v in sorted(by.items()) if k not in have and len(v) == steps]
    path = os.path.join(run, 'per_cycle.csv')
    exists = os.path.exists(path)
    with open(path, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            w.writeheader()
        for d in new:
            w.writerow({k: (repr(d[k]) if isinstance(d[k], float) else d[k]) for k in FIELDS})
    return len(new)


def max_change(pc):
    """Largest relative QoI change over the last PAIRS consecutive cycle pairs."""
    last = pc[-(PAIRS + 1):]
    return max(abs(last[i][q] - last[i - 1][q]) / abs(last[i][q]) for i in range(1, PAIRS + 1) for q in QOIS)


def periodic(run):
    pc = load(run)
    n = len(pc)
    if n >= MIN_CYCLES and max_change(pc) < TOL:
        open(os.path.join(run, 'periodic.txt'), 'w').write(f'{int(pc[-1]["cycle"])}\n')
        print(f'periodic: {run} at cycle {int(pc[-1]["cycle"])}, max change {max_change(pc):.3e}')
        return 0
    print(f'periodic: {run} not yet, cycles {n}, max change {max_change(pc) if n > PAIRS else None}')
    return 2 if n >= MAX_CYCLES else 1


def gci(f1, f2, f3):
    """Celik et al. (2008) with a constant ratio R: (p, GCI_fine, e32/e21)."""
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0:
        return None, None, None
    p = abs(math.log(abs(e32 / e21))) / math.log(R)
    return p, 1.25 * abs((f1 - f2) / f1) / (R ** p - 1), e32 / e21


def final(case, out):
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
    from resultslib import Results
    os.makedirs(out, exist_ok=True)
    r = Results(out)
    last = {}
    for run in RUNS:
        d = os.path.join(case, run)
        pc = load(d)
        with open(os.path.join(out, f'per_cycle_{run}.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for row in pc:
                w.writerow({k: repr(row[k]) for k in FIELDS})
        per = os.path.join(d, 'periodic.txt')
        if os.path.exists(per):
            k = int(open(per).read())
            r.add(f'cycles_{run}', k, f'per_cycle_{run}.csv', f'{k - PAIRS + 1}-{k + 1} (cycles {k - PAIRS}-{k})')
        else:
            r.add(f'cycles_{run}', f'not reached ({len(pc)} cycles)', f'per_cycle_{run}.csv', f'2-{len(pc) + 1}')
        last[run] = (pc[-1], len(pc) + 1) if pc else (None, None)

    # grid convergence (G3 fine, G2 medium, G1 coarse) and time step (G2 vs T2), on the last cycle of each run
    src_g = 'per_cycle_G3.csv:{}, per_cycle_G2.csv:{}, per_cycle_G1.csv:{}'.format(
        last['G3'][1], last['G2'][1], last['G1'][1])
    with open(os.path.join(out, 'gci.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['qoi', 'phi_G3_fine', 'phi_G2', 'phi_G1_coarse', 'e32_over_e21', 'apparent_order', 'gci_fine',
                    'phi_T2', 'dt_rel_change'])
        for i, q in enumerate(QOIS):
            f1, f2, f3 = (last[g][0][q] if last[g][0] else None for g in ('G3', 'G2', 'G1'))
            p = g_ = ratio = None
            if None not in (f1, f2, f3):
                p, g_, ratio = gci(f1, f2, f3)
            t2 = last['T2'][0][q] if last['T2'][0] else None
            dt = abs(t2 - f2) / abs(t2) if None not in (t2, f2) else None
            w.writerow([q, f1, f2, f3, ratio, p, g_, t2, dt])
            r.add(f'gci_{q}', g_, 'gci.csv', f'{i + 2} ({src_g})')
            r.add(f'p_err_{q}', None if p is None else abs(p - FORMAL_ORDER), 'gci.csv', f'{i + 2} ({src_g})')
            r.add(f'dt_rel_{q}', dt, 'gci.csv',
                  f'{i + 2} (per_cycle_T2.csv:{last["T2"][1]} vs per_cycle_G2.csv:{last["G2"][1]})')

    for run in ('G2', 'G3'):
        row, line = last[run]
        r.add(f'closure4_{run}_W', row['closure4'] if row else None, f'per_cycle_{run}.csv', line)
        r.add(f'closure6_{run}_W', row['closure'] if row else None, f'per_cycle_{run}.csv', line)

    # crash patterns over all logs of all runs; logs kept trimmed (first 200, last 100 lines, numbered)
    bad = re.compile(r'FOAM FATAL|\bnan\b|\binf\b|Floating point exception|Segmentation fault', re.IGNORECASE)
    banner = re.compile(r'^trapFpe: Floating point exception trapping enabled')
    hits, skipped = [], 0
    logs = sorted(glob.glob(os.path.join(case, 'log.*')) + glob.glob(os.path.join(case, '*', 'log.*')))
    for path in logs:
        lines = open(path, errors='replace').readlines()
        for i, l in enumerate(lines):
            if banner.match(l):
                skipped += 1
            elif bad.search(l):
                hits.append(f'{os.path.relpath(path, case)}:{i + 1}')
        name = os.path.relpath(path, case).replace(os.sep, '_') + '.trimmed'
        with open(os.path.join(out, name), 'w') as f:
            for i, l in enumerate(lines):
                if i < 200 or i >= len(lines) - 100:
                    f.write(f'{i + 1:7d}  {l}')
    r.add('crash_count', len(hits), 'log.*', hits if hits else
          f'all lines of all logs of all runs; {skipped} trapFpe banner lines skipped')
    r.write()


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'summarise':
        print(f'summarise {sys.argv[2]}: {summarise(sys.argv[2], int(sys.argv[3]))} new cycles')
    elif mode == 'periodic':
        sys.exit(periodic(sys.argv[2]))
    elif mode == 'final':
        final(sys.argv[2], sys.argv[3])
