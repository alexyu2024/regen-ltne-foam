#!/usr/bin/env python3
"""L0 metrics. Usage: results.py <outdir>. Reads the logs copied to <outdir>, writes <outdir>/results.csv."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
from resultslib import Results, copy_logs, last_match, min_field

case = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]
copy_logs(case, out, ['log.*', 'postProcessing/minMax/0/fieldMinMax.dat'])
r = Results(out)

# L0.1: the line Allrun writes after building
ln, m = last_match(out, 'log.build', r'^ltneFoam binary: (\S+)$')
r.add('solver_built', None if ln is None else int(os.path.basename(m.group(1)) == 'ltneFoam'), 'log.build', ln)

# L0.2 and L0.3
path = os.path.join(out, 'log.ltneFoam')
if os.path.exists(path):
    lines = open(path).read().splitlines()
    ends = [i + 1 for i, l in enumerate(lines) if l.strip() == 'End']
    r.add('end_line_count', len(ends), 'log.ltneFoam', ends if ends else 'whole file')
    ln, m = last_match(out, 'log.ltneFoam', r'^Time = (\S+)$')
    r.add('final_time', None if m is None else float(m.group(1)), 'log.ltneFoam', ln)
else:
    r.add('end_line_count', None, 'log.ltneFoam', None)
    r.add('final_time', None, 'log.ltneFoam', None)

# L0.4
bad = re.compile(r'FOAM FATAL|\bnan\b|\binf\b', re.IGNORECASE)
hits = []
for f in sorted(os.listdir(out)):
    if f.startswith('log.'):
        for i, l in enumerate(open(os.path.join(out, f), errors='replace')):
            if bad.search(l):
                hits.append(f'{f}:{i + 1}')
r.add('fatal_or_nan_count', len(hits), 'log.*', hits if hits else 'all lines')

# L0.5-7
for key, field in (('p_min', 'p'), ('T_min', 'T'), ('Ts_min', 'Ts')):
    v, rows = min_field(out, 'fieldMinMax.dat', field)
    r.add(key, v, 'fieldMinMax.dat', rows)
r.write()
