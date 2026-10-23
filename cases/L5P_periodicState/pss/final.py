"""Write <out>/results.csv for tools/verify.py L5P from the files the study wrote into <out>.

  python3 -m pss.final <out>      (<out> = results/L5P)
Rows whose input does not exist yet (a method not run) are written as not read.
"""
import csv, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from resultslib import Results  # noqa: E402

C40_REF = 27.865715
CRASH = re.compile(r'FOAM FATAL|\bnan\b|\binf\b|Floating point exception|Segmentation fault', re.IGNORECASE)
BANNER = re.compile(r'^trapFpe: Floating point exception trapping enabled')


def jload(path):
    return json.load(open(path)) if os.path.exists(path) else None


def main(out):
    r = Results(out)
    nat = os.path.join(out, 'natural')
    pc = list(csv.DictReader(open(os.path.join(nat, 'per_cycle.csv'))))
    row40 = [i for i, x in enumerate(pc) if int(float(x['cycle'])) == 40]
    if row40:
        v = float(pc[row40[0]]['Tjoint_mean'])
        r.add('c40_Tjoint_diff_K', abs(v - C40_REF), 'natural/per_cycle.csv', f'{row40[0] + 2} (cycle 40)')
    else:
        r.add('c40_Tjoint_diff_K', None, 'natural/per_cycle.csv', None)

    ref = jload(os.path.join(out, 'reference.json'))
    for key in ('ref_cycles', 'ref_remaining_max_frac', 'nat_k', 'nat_total', 'nat_within_from', 'nat_mass_drift_max'):
        val = None if ref is None else ref.get(key)
        r.add(key, val, 'reference.json', key if val is not None else None)

    noise = os.path.join(out, 'noise.csv')
    rows = list(csv.DictReader(open(noise))) if os.path.exists(noise) else []
    for t in ('N1', 'N2', 'N3'):
        hit = [(i, x) for i, x in enumerate(rows) if x['test'] == t]
        r.add(f'noise_{t}_K', float(hit[0][1]['max_dx_K']) if hit else None, 'noise.csv',
              hit[0][0] + 2 if hit else None)
    ns = jload(os.path.join(out, 'noise_summary.json'))
    r.add('noise_N4_floor', ns and ns['N4_floor'], 'noise_summary.json', 'N4_floor' if ns else None)

    # crash scan: the natural run's logs (trimmed copies) and every map evaluation (scanned when it ran)
    hits, skipped, files = [], 0, sorted(glob.glob(os.path.join(nat, 'log.*')))
    for path in files:
        for i, l in enumerate(open(path, errors='replace')):
            l = l[9:] if re.match(r'^ *\d+  ', l) else l
            if BANNER.match(l):
                skipped += 1
            elif CRASH.search(l):
                hits.append(f'{os.path.relpath(path, out)}:{i + 1}')
    evals = 0
    for j in [ns] + [jload(p) for p in sorted(glob.glob(os.path.join(out, '*_summary.json')))
                     if not p.endswith('noise_summary.json')]:
        if j:
            hits += j.get('crash_hits', [])[:j.get('crash_count', 0)] or ([f'{j.get("crash_count")} hits'] if j.get('crash_count') else [])
            evals += 1
    r.add('crash_count', len(hits), 'natural/log.*',
          hits if hits else f'all lines of {len(files)} natural logs ({skipped} trapFpe banner lines skipped) and of '
                            f'every map evaluation of {evals} study runs (scanned when they ran)')

    for name in ('np1', 'np2', 'np3', 'brr3', 'brr6', 'gm0', 'gm3'):
        s = jload(os.path.join(out, f'{name}_summary.json'))
        r.add(f'{name}_total', s and s['total'], f'{name}_summary.json', 'total' if s else None)
        r.add(f'{name}_pass', s and s.get('passed'), f'{name}_summary.json',
              'passed' if s and 'passed' in s else None)
    r.write()


if __name__ == '__main__':
    main(sys.argv[1])
