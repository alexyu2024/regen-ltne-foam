#!/usr/bin/env python3
"""L4E breakthrough figure. Usage: plot.py <outdir> <png>. Needs matplotlib (not used by CI)."""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
png = sys.argv[2]
from results import PROBES, T0, DT, XI_PER_M, schumann, eta_at, table   # results reads <outdir> = sys.argv[1]

fig, ax = plt.subplots(figsize=(6.4, 4.0))
colors = ('#1f77b4', '#d62728')
for fname, col, style, label in (('probe_T.dat', 0, '-', 'gas'), ('probe_Ts.dat', 1, '--', 'solid')):
    rows = table(fname)
    t = [v[0] for _, v in rows]
    for k, x in enumerate(PROBES):
        sim = [(v[1 + k] - T0) / DT for _, v in rows]
        ref = [schumann(XI_PER_M * x, eta_at(x, tt))[col] for tt in t[::25]]
        ax.plot(t, sim, style, color=colors[k], lw=1.6, label=f'ltneFoam {label}, x = {x * 1000:.2f} mm')
        ax.plot(t[::25], ref, 'o' if col == 0 else 's', mfc='none', color=colors[k], ms=4,
                label=f'Schumann {label}, x = {x * 1000:.2f} mm')
ax.set_xlabel('t, s')
ax.set_ylabel(r'$\theta = (T - T_0) / (T_1 - T_0)$')
ax.set_xlim(0, 150)
ax.set_ylim(-0.02, 1.02)
ax.grid(alpha=0.3)
ax.legend(fontsize=7, loc='lower right')
ax.set_title('L4E single blow: breakthrough curves (lines) vs Schumann (markers)', fontsize=9)
fig.tight_layout()
fig.savefig(png, dpi=150)
