"""Helpers for the per-level results.py scripts: every value is stored with the file and line(s) it was read from."""
import csv, glob, os, re, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def copy_logs(case, out, patterns):
    """Copy the files a level cites from the case directory into out (flat), so they survive Allclean."""
    os.makedirs(out, exist_ok=True)
    for pat in patterns:
        for f in sorted(glob.glob(os.path.join(case, pat))):
            shutil.copy(f, os.path.join(out, os.path.basename(f)))


def last_match(out, name, regex):
    """(line number, match) of the last line of out/name matching regex, or (None, None)."""
    path = os.path.join(out, name)
    found = (None, None)
    if os.path.exists(path):
        rx = re.compile(regex)
        for i, l in enumerate(open(path, errors='replace')):
            m = rx.search(l.rstrip('\n'))
            if m:
                found = (i + 1, m)
    return found


def min_field(out, name, field):
    """Minimum of the 'min' column over all rows of a fieldMinMax .dat file for one field,
    and the line numbers it was taken from. Rows are tab-separated: Time, field, min, ..."""
    path = os.path.join(out, name)
    if not os.path.exists(path):
        return None, None
    cols, vals, lines = None, [], []
    for i, l in enumerate(open(path)):
        parts = [p.strip() for p in l.lstrip('#').rstrip('\n').split('\t')]
        if l.startswith('#'):
            if parts and parts[0] == 'Time':
                cols = parts
            continue
        if cols and len(parts) == len(cols) and parts[cols.index('field')] == field:
            vals.append(float(parts[cols.index('min')]))
            lines.append(i + 1)
    if not vals:
        return None, None
    return min(vals), f'{lines[0]}-{lines[-1]} (rows with field {field})'


class Results:
    """Collects metric, value and source; writes out/results.csv."""

    def __init__(self, out):
        self.out = out
        self.path = os.path.join(out, 'results.csv')
        self.rows = []

    def add(self, metric, value, name, where):
        src = os.path.relpath(os.path.join(self.out, name), REPO)
        if where is None:
            value, src = None, src + ' (not found)'
        elif isinstance(where, list):
            src += ':' + ','.join(str(w) for w in where)
        else:
            src += f':{where}'
        self.rows.append((metric, 'not read' if value is None else repr(value), src))

    def write(self, mode='w'):
        with open(self.path, mode, newline='') as f:
            w = csv.writer(f)
            if mode == 'w':
                w.writerow(('metric', 'value', 'source'))
            w.writerows(self.rows)
