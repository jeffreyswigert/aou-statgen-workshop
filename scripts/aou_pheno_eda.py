#!/usr/bin/env python3
"""EDA for the real phenotype (session 3). Aggregates only on screen.

Reads results/aou_pheno.tsv. Writes:
  results/aou_pheno_summary.txt     distribution table, by sex
  results/aou_height_hist.png       histogram, whole analysis sample
  results/aou_height_kde_sex.png    kernel densities by recorded sex

Same discipline as the synthetic sessions, now with real stakes: printed
group sizes are rounded to the nearest 100, any count of 1-20 is suppressed
outright, and groups too small to show are folded into the text as such.
The person-level input file itself never leaves the workspace.
"""
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rows = [l.split('\t') for l in Path('results/aou_pheno.tsv').read_text().splitlines()[1:]]
h = np.array([float(r[1]) for r in rows])
sex = np.array([r[4] for r in rows])
age = np.array([float(r[3]) if r[3] else np.nan for r in rows])

rounded = lambda n: '<=20 (suppressed)' if 1 <= n <= 20 else f'~{round(n, -2):,}'

def block(name, x):
    q = np.percentile(x, [25, 50, 75])
    return (f'  {name:<22} n={rounded(len(x)):<12} mean={x.mean():7.2f}  sd={x.std():6.2f}  '
            f'IQR {q[0]:.1f} / {q[1]:.1f} / {q[2]:.1f}')

out = ['Real-phenotype EDA -- aggregates only; person-level file stays in the workspace', '',
       'Height (as recorded; sandbox rehearsal shows standardized fixture values):',
       block('everyone', h)]
for s in ('Male', 'Female', 'other'):
    m = sex == s
    out.append(block(s, h[m]) if m.sum() > 20 else
               f'  {s:<22} n={rounded(int(m.sum()))} -- too few to display separately')
if np.isfinite(age).sum() > 20:
    out += ['', block('age (years)', age[np.isfinite(age)])]
out += ['', 'Questions worth a minute: are the sex-specific means plausible for a US',
        'cohort? Is the SD? What would a spike or a second mode tell you about the',
        'concept or unit choices upstream?']
Path('results/aou_pheno_summary.txt').write_text('\n'.join(out) + '\n')
print('\n'.join(out))

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.hist(h, bins=60, color='#990000', alpha=0.8)
ax.set_xlabel('height (as recorded)'); ax.set_ylabel('people')
ax.set_title(f'Height, analysis sample (n {rounded(len(h))})')
fig.tight_layout(); fig.savefig('results/aou_height_hist.png', dpi=150)

def kde(x, grid):
    bw = 1.06 * x.std() * len(x) ** (-1 / 5)
    return np.exp(-0.5 * ((grid[:, None] - x) / bw) ** 2).sum(1) / (len(x) * bw * np.sqrt(2 * np.pi))

grid = np.linspace(h.min(), h.max(), 300)
fig, ax = plt.subplots(figsize=(7, 4.5))
for s, color in (('Male', '#666666'), ('Female', '#990000')):
    m = sex == s
    if m.sum() > 20:
        ax.plot(grid, kde(h[m], grid), color=color, lw=2, label=f'{s} (n {rounded(int(m.sum()))})')
ax.set_xlabel('height (as recorded)'); ax.set_ylabel('density')
ax.set_title('Height by recorded sex: why height standardizes within sex')
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig('results/aou_height_kde_sex.png', dpi=150)
print('Figures: results/aou_height_hist.png, results/aou_height_kde_sex.png '
      '(open from the JupyterLab file browser).')

# TRY IT: change bins=60 to bins=15 and to bins=300. What does each version
# hide or invent? On REAL data, also ask: could any bin be so sparse that the
# figure itself displays a small count? (Bars are counts too.)
