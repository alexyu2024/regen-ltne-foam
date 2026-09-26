#!/usr/bin/env python3
"""Check a level's results against its bars in docs/VERIFICATION.md.

Usage: verify.py <level> <outdir>   e.g. verify.py L0 results/L0
Reads <outdir>/results.csv, writes <outdir>/STATUS.md, exits 1 on any miss.
"""
import csv, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPS = {
    '==': lambda v, b: abs(v - b) <= 1e-9 * max(1.0, abs(b)),
    '<=': lambda v, b: v <= b, '>=': lambda v, b: v >= b,
    '<': lambda v, b: v < b, '>': lambda v, b: v > b,
}


def bars(level):
    rx = re.compile(r'^\|\s*(%s\.\d+)\s*\|\s*(\S+)\s*\|\s*(==|<=|>=|<|>)\s*\|\s*(\S+)\s*\|\s*(.*?)\s*\|\s*$' % level)
    rows = []
    for i, l in enumerate(open(os.path.join(REPO, 'docs', 'VERIFICATION.md'))):
        m = rx.match(l)
        if m:
            rows.append(m.groups() + (i + 1,))
    return rows


def main():
    level, out = sys.argv[1], sys.argv[2]
    bar_rows = bars(level)
    if not bar_rows:
        sys.exit(f'no bars for {level} in docs/VERIFICATION.md')
    res = {}
    path = os.path.join(out, 'results.csv')
    if os.path.exists(path):
        for row in csv.DictReader(open(path)):
            res[row['metric']] = row
    lines = [f'# {level} status', '',
             '| check | bar | value | status | value source |', '|---|---|---|---|---|']
    fails = 0
    for cid, metric, op, bar, desc, vline in bar_rows:
        r = res.get(metric)
        value = r['value'] if r else 'not read'
        src = r['source'] if r else 'not read'
        try:
            ok = OPS[op](float(value), float(bar))
        except ValueError:
            ok = False
        fails += not ok
        lines.append(f'| {cid} {metric} | {op} {bar} (docs/VERIFICATION.md:{vline}) | {value} | '
                     f'{"PASS" if ok else "FAIL"} | {src} |')
    lines += ['', f'{len(bar_rows) - fails}/{len(bar_rows)} PASS', '']
    open(os.path.join(out, 'STATUS.md'), 'w').write('\n'.join(lines))
    print('\n'.join(lines))
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
