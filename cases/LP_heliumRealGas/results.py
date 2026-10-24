#!/usr/bin/env python3
"""LP results: real-gas helium thermo vs NIST (docs/VERIFICATION.md, LP). Usage: results.py <outdir>"""
import csv, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from resultslib import Results, copy_logs

out = sys.argv[1]
copy_logs(HERE, out, ['log.*', 'propsCheck.dat', 'nist_helium.csv'])
r = Results(out)

# NIST rows (line numbers in nist_helium.csv) and model rows (line numbers in propsCheck.dat)
nist_lines = [l for l in open(os.path.join(HERE, 'nist_helium.csv'))]
hdr = next(i for i, l in enumerate(nist_lines) if l.startswith('T,'))
nist = [(hdr + 2 + k, row) for k, row in enumerate(csv.DictReader(nist_lines[hdr:]))]
model, cell = [], None
path = os.path.join(HERE, 'propsCheck.dat')
if os.path.exists(path):
    for i, l in enumerate(open(path)):
        if l.startswith('#'):
            continue
        v = l.split()
        if v[0] == 'cell':
            cell = (i + 1, [float(x) for x in v[1:]])
        else:
            model.append((i + 1, [float(x) for x in v]))

names = ['22', '50', '80', '22c', '50c', '80c']
for k, tag in enumerate(names):
    nl, nrow = nist[k]
    if k < len(model):
        ml, (T, p, rho, cp, h, Trec) = model[k]
        if abs(T - float(nrow['T'])) > 1e-9 or abs(p - float(nrow['p'])) > 1e-6:
            sys.exit(f'point {k}: model (T, p) = ({T}, {p}) does not match nist_helium.csv line {nl}')
        src = f'{ml} vs nist_helium.csv:{nl}'
        r.add(f'rho_rel_{tag}', abs(rho / float(nrow['rho']) - 1), 'propsCheck.dat', src)
        r.add(f'cp_rel_{tag}', abs(cp / float(nrow['cp']) - 1), 'propsCheck.dat', src)
    else:
        r.add(f'rho_rel_{tag}', None, 'propsCheck.dat', None)
        r.add(f'cp_rel_{tag}', None, 'propsCheck.dat', None)

if model:
    r.add('T_roundtrip_max_K', max(abs(v[5] - v[0]) for _, v in model), 'propsCheck.dat',
          f'{model[0][0]}-{model[-1][0]} (column 6 vs column 1)')
else:
    r.add('T_roundtrip_max_K', None, 'propsCheck.dat', None)

if cell and abs(cell[1][0] - 50) < 1e-6 and abs(cell[1][1] - 750000) < 1e-3:
    cl, (T, p, mu, kappa) = cell
    nl, nrow = nist[1]
    r.add('mu_rel_50', abs(mu / float(nrow['mu']) - 1), 'propsCheck.dat', f'{cl} vs nist_helium.csv:{nl}')
    r.add('kappa_rel_50', abs(kappa / float(nrow['kappa']) - 1), 'propsCheck.dat', f'{cl} vs nist_helium.csv:{nl}')
else:
    r.add('mu_rel_50', None, 'propsCheck.dat', None)
    r.add('kappa_rel_50', None, 'propsCheck.dat', None)
r.write()
