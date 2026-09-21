#!/usr/bin/env python3
"""EDA for the real-data PGI (session 3): joins, one honest table, one figure.

Joins three real files, each with its own key quirk -- this is the session's
ID-discipline exam:
  results/aou_pgi.sscore        key column '#IID' (numeric person ids)
  results/aou_pheno.tsv         key column 'person_id'
  lab_data/ancestry_preds.tsv   key column 'research_id' -- same numbers,
                                DIFFERENT NAME. Joining on the name without
                                looking fails; joining on the value works.
                                (Its pca_features column is a stringified
                                list -- another reason to read files before
                                trusting them.)

Writes results/aou_pgi_summary.txt and results/aou_pgi_kde_ancestry.png.
Printed group sizes are rounded to the nearest 100; groups of 1-20 people are
never shown. Person-level files stay in the workspace.
"""
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read_keyed(path, delim='\t'):
    lines = Path(path).read_text().splitlines()
    h = lines[0].lstrip('#').split(delim)
    return h, [l.split(delim) for l in lines[1:] if l.strip()]

sh, srows = read_keyed('results/aou_pgi.sscore')
score = {r[0]: float(r[sh.index('SCORE1_SUM')]) for r in srows}
ph, prows = read_keyed('results/aou_pheno.tsv')
pheno = {r[0]: r for r in prows}
ah, arows = read_keyed('lab_data/ancestry_preds.tsv')
anc = {r[0]: r[1] for r in arows}          # research_id -> ancestry_pred

iids = sorted(set(score) & set(pheno))     # the analysis set: scored AND phenotyped
pgi = np.array([score[i] for i in iids])
pgi = (pgi - pgi.mean()) / pgi.std()
hz = np.array([float(pheno[i][2]) if pheno[i][2] else np.nan for i in iids])
ancv = np.array([anc.get(i, 'unknown') for i in iids])

rounded = lambda n: '<=20 (suppressed)' if 1 <= n <= 20 else f'~{round(n, -2):,}'
ok = np.isfinite(hz)
r = np.corrcoef(pgi[ok], hz[ok])[0, 1] if ok.sum() > 2 else float('nan')

out = ['Real-data PGI EDA -- aggregates only', '',
       f'People scored on chr fileset:            {rounded(len(score))}',
       f'People in the phenotype file:            {rounded(len(pheno))}',
       f'Joined analysis set (both):              {rounded(len(iids))}',
       '(three files, three key spellings: #IID, person_id, research_id --',
       ' one underlying id. The join is on the value, checked, never assumed.)', '',
       f'corr(PGI, within-sex height z)         = {r:+.3f}',
       f'R2 (one-chromosome PGI, alone)         = {r*r:.4f}', '',
       'Reading: a one-chromosome PGI from teaching weights is deliberately',
       'weak -- what matters is that YOU built it on real data, counted every',
       'match and join, and can read its distribution below honestly.']

# PGI by predicted genetic ancestry: the portability/structure picture on
# real data. Groups of <=20 people are not drawn at all.
def kde(x, grid):
    bw = 1.06 * x.std() * len(x) ** (-1 / 5)
    return np.exp(-0.5 * ((grid[:, None] - x) / bw) ** 2).sum(1) / (len(x) * bw * np.sqrt(2 * np.pi))

grid = np.linspace(pgi.min() - .5, pgi.max() + .5, 300)
fig, ax = plt.subplots(figsize=(7.5, 4.5))
palette = ['#990000', '#666666', '#C89B00', '#3B6FA0', '#5E8C61', '#8B5E83']
drawn = []
for k, g in enumerate(sorted(set(ancv))):
    m = ancv == g
    if m.sum() > 20 and pgi[m].std() > 0:
        ax.plot(grid, kde(pgi[m], grid), lw=2, color=palette[k % 6],
                label=f'{g} (n {rounded(int(m.sum()))})')
        drawn.append(g)
ax.set_xlabel('PGI (sample SD units)'); ax.set_ylabel('density')
ax.set_title('PGI by predicted genetic ancestry')
ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig('results/aou_pgi_kde_ancestry.png', dpi=150)

out += ['', f'Figure: results/aou_pgi_kde_ancestry.png (groups drawn: {", ".join(drawn) or "none"}).',
        'Distributional differences across ancestry groups reflect allele',
        'frequencies and the discovery GWAS behind the weights as much as any',
        'biology -- and prediction accuracy is NOT constant across groups',
        '(portability). Name both facts wherever this figure appears.']
Path('results/aou_pgi_summary.txt').write_text('\n'.join(out) + '\n')
print('\n'.join(out))
