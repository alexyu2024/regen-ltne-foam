#!/usr/bin/env python3
"""L5D post-processing: decay ratio of the slow matrix thermal relaxation (docs/VERIFICATION.md, L5D).

  decay.py stop <run dir>      exit 0 when the stopping rule holds (or 1500 cycles), 1 to continue
  decay.py final <case> <out>  write decay.csv, per_cycle.csv, results.csv and trimmed logs into <out>
"""
import csv, glob, importlib.util, math, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('l5results', os.path.join(HERE, '..', 'L5_regenSlice', 'results.py'))
L5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L5)
MIN_CYCLES, MAX_CYCLES, WIN, TOL, FIT = 200, 1500, 50, 1e-4, 100


def series(pc, q):
    v = [r[q] for r in pc]
    d = [None] + [v[i] - v[i - 1] for i in range(1, len(v))]
    r = [None, None] + [d[i] / d[i - 1] if d[i - 1] else None for i in range(2, len(v))]
    return v, d, r


def window_change(r):
    a, b = r[-WIN:], r[-2 * WIN:-WIN]
    if len(r) < 2 * WIN + 2 or None in a or None in b:
        return None, None
    return sum(a) / WIN, abs(sum(a) / WIN - sum(b) / WIN)


def r_fit(d):
    """exp(slope) of ln|d_k| vs k over the last FIT cycles (least squares)."""
    pts = [(k, math.log(abs(x))) for k, x in enumerate(d) if x][-FIT:]
    n = len(pts)
    if n < 10:
        return None
    mk = sum(k for k, _ in pts) / n
    my = sum(y for _, y in pts) / n
    s = sum((k - mk) * (y - my) for k, y in pts) / sum((k - mk) ** 2 for k, _ in pts)
    return math.exp(s)


def stop(run):
    pc = L5.load_per_cycle(run)
    _, _, r = series(pc, 'Tjoint_mean') if pc else ([], [], [])
    mean, ch = window_change(r) if pc else (None, None)
    print(f'decay: {len(pc)} cycles, r mean50 {mean}, window change {ch}')
    if len(pc) >= MAX_CYCLES or (len(pc) >= MIN_CYCLES and ch is not None and ch < TOL):
        return 0
    return 1


def final(case, out):
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
    from resultslib import Results
    os.makedirs(out, exist_ok=True)
    run = os.path.join(case, 'run')
    pc = L5.load_per_cycle(run)
    shutil.copy(os.path.join(run, 'per_cycle.csv'), os.path.join(out, 'per_cycle.csv'))
    T, dT, rT = series(pc, 'Tjoint_mean')
    with open(os.path.join(out, 'decay.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cycle', 'Tjoint_mean_K', 'd_K', 'r'])
        for i, row in enumerate(pc):
            w.writerow([int(row['cycle']), repr(T[i]), '' if dT[i] is None else repr(dT[i]),
                        '' if rT[i] is None else repr(rT[i])])
    n = len(pc)
    last = f'{n - FIT + 2}-{n + 1} (cycles {n - FIT + 1}-{n})'
    r = Results(out)
    r.add('cycles_run', n, 'decay.csv', f'2-{n + 1}')
    rf = r_fit(dT)
    mean, ch = window_change(rT)
    r.add('r_fit_Tjoint', rf, 'decay.csv', last)
    r.add('r_mean50_Tjoint', mean, 'decay.csv', f'{n - WIN + 2}-{n + 1}')
    r.add('r_window_change', ch, 'decay.csv', f'{n - 2 * WIN + 2}-{n + 1}'
          + ('' if ch is not None and ch < TOL else ' (not stationary to 1e-4)'))
    tau = -1 / math.log(rf) if rf and 0 < rf < 1 else None
    r.add('tau_cycles', tau, 'decay.csv', last)
    r.add('tau_s', tau / L5.F if tau else None, 'decay.csv', last)
    r.add('Tjoint_inf_K', T[-1] + dT[-1] * rf / (1 - rf) if rf and rf < 1 else None, 'decay.csv', f'{n + 1}, r_fit')
    r.add('Tjoint_last_K', T[-1] if T else None, 'decay.csv', n + 1)
    for q in ('H_joint', 'H_hot'):
        r.add(f'r_fit_{q}', r_fit(series(pc, q)[1]), 'per_cycle.csv', last)

    bad = re.compile(r'FOAM FATAL|\bnan\b|\binf\b|Floating point exception|Segmentation fault', re.IGNORECASE)
    banner = re.compile(r'^trapFpe: Floating point exception trapping enabled')
    hits, skipped = [], 0
    for path in sorted(glob.glob(os.path.join(case, 'log.*')) + glob.glob(os.path.join(run, 'log.*'))):
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
    if sys.argv[1] == 'stop':
        sys.exit(stop(sys.argv[2]))
    final(sys.argv[2], sys.argv[3])
