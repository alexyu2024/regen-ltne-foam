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
    # ids with a letter suffix (e.g. L5.7a) are supplementary checks added by an amendment, not preregistered bars
    rx = re.compile(r'^\|\s*(%s\.\d+[a-z]?)\s*\|\s*(\S+)\s*\|\s*(==|<=|>=|<|>|report)\s*\|\s*(\S+)\s*\|\s*(.*?)\s*\|\s*$' % level)
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
    fails, failed, supp = 0, [], []
    for cid, metric, op, bar, desc, vline in bar_rows:
        r = res.get(metric)
        value = r['value'] if r else 'not read'
        src = r['source'] if r else 'not read'
        if op == 'report':
            try:
                status = 'REPORT (%s %s)' % ('<=' if float(value) <= float(bar) else '>', bar)
            except ValueError:
                status = 'REPORT (not read)'
            lines.append(f'| {cid} {metric} | report (docs/VERIFICATION.md:{vline}) | {value} | {status} | {src} |')
            continue
        try:
            ok = OPS[op](float(value), float(bar))
        except ValueError:
            ok = False
        fails += not ok
        if cid[-1].isalpha():
            m = re.search(r'Amendment \w+', desc)
            supp.append((cid, ok, m.group(0) if m else 'amendment'))
        elif not ok:
            failed.append(cid)
        lines.append(f'| {cid} {metric} | {op} {bar} (docs/VERIFICATION.md:{vline}) | {value} | '
                     f'{"PASS" if ok else "FAIL"} | {src} |')
    n = sum(1 for b in bar_rows if b[2] != 'report' and not b[0][-1].isalpha())
    summary = f'{n - len(failed)}/{n} PASS'
    if supp:
        summary += ' as preregistered' + (f' ({", ".join(failed)} FAIL)' if failed else '')
        for cid, ok, amendment in supp:
            summary += f'; supplementary check {cid} {"PASS" if ok else "FAIL"} ({amendment})'
    lines += ['', summary, '']
    open(os.path.join(out, 'STATUS.md'), 'w').write('\n'.join(lines))
    print('\n'.join(lines))
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
