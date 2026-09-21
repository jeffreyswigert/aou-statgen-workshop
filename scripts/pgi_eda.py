#!/usr/bin/env python3
"""Exploratory analysis of the PGI: distributions first, models second.

Run via 08_pgi_eda.sh. Joins the PGI (results/pgi.sscore) with phenotypes,
covariates, and the two group labels in data/groups.tsv -- by IID, as always.

Writes to results/:
  pgi_summary.txt           the EDA table: distributions, correlations,
                            incremental R-squared, and group comparisons
  pgi_hist_treatment.png    histogram of the PGI by RANDOMIZED treatment arm
                            (expect overlap: balance is the correct finding)
  pgi_kde_enrolled.png      kernel densities by SELF-SELECTED enrollment
                            (expect a shift: selection is correlated with
                            structure that leaked into the weights)
  pgi_decile_trait.png      mean trait by PGI decile -- the classic gradient

The figures are PNG files: open them from the JupyterLab file browser.

The one modeling number here is INCREMENTAL R-squared -- the social-science
standard for "how much does the PGI add?": R2(trait ~ covariates + PGI) minus
R2(trait ~ covariates). Reporting the PGI's raw R2 alone overstates its
contribution whenever covariates and PGI overlap.
"""
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')                      # no display on a VM; write files
import matplotlib.pyplot as plt

def read_table(path, key='#IID'):
    """Whitespace table -> {iid: {col: value}}, header may start with '#'."""
    lines = Path(path).read_text().splitlines()
    h = lines[0].lstrip('#').split()
    return {l.split()[0]: dict(zip(h, l.split())) for l in lines[1:] if l.strip()}

sc = read_table('results/pgi.sscore')
ph = read_table('data/phenotypes.tsv')
cv = read_table('data/covariates.tsv')
gr = read_table('data/groups.tsv')

# Everyone in the joined analysis set has all four rows. Sorting the IIDs
# makes every array below line up person-by-person.
iids = sorted(set(sc) & set(ph) & set(cv) & set(gr))
n_matched = len(iids)

col = lambda tab, name, cast=float: np.array([cast(tab[i][name]) for i in iids])
pgi_raw = col(sc, 'SCORE1_SUM')
trait = col(ph, 'trait')
treatment = col(gr, 'treatment', int)
enrolled = col(gr, 'enrolled', int)

# Standardize the PGI to mean 0, SD 1 *in this sample* -- the reporting
# convention in social-science genomics ("one SD of the PGI ...").  Remember
# it is sample-specific: the same person has a different standardized PGI in
# a different sample.
pgi = (pgi_raw - pgi_raw.mean()) / pgi_raw.std()

def r2(X, y):
    """R-squared of least squares y ~ [1, X]."""
    X = np.column_stack([np.ones(len(y))] + list(X))
    resid = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
    return 1 - resid.var() / y.var()

covs = [col(cv, c) for c in ('age', 'sex', 'PC1', 'PC2', 'PC3', 'PC4', 'PC5')]
r2_cov = r2(covs, trait)
r2_full = r2(covs + [pgi], trait)
r2_pgi = r2([pgi], trait)

def shown(n):   # counts of 1-20 are never printed (dissemination policy)
    return str(n) if n == 0 or n > 20 else '<=20 (suppressed)'

def group_block(name, g):
    """n / mean / sd of the standardized PGI in each group, plus the gap."""
    lines = [f'{name}:']
    short = name.split()[0]
    for v in (0, 1):
        s = pgi[g == v]
        lines.append(f'  {short}={v}: n={shown(len(s))}  mean PGI={s.mean():+.3f}  sd={s.std():.3f}')
    gap = pgi[g == 1].mean() - pgi[g == 0].mean()
    lines.append(f'  standardized difference: {gap:+.3f} SD')
    return lines

q = np.percentile(pgi, [25, 50, 75])
out = ['PGI exploratory analysis (all data synthetic)', '',
       f'People scored and matched across all files: {n_matched}',
       f'PGI (standardized): mean {pgi.mean():+.2f}, sd {pgi.std():.2f}, '
       f'quartiles {q[0]:+.2f} / {q[1]:+.2f} / {q[2]:+.2f}', '',
       f'corr(PGI, trait)                     = {np.corrcoef(pgi, trait)[0,1]:+.3f}',
       f'R2, trait ~ PGI alone                = {r2_pgi:.3f}',
       f'R2, trait ~ covariates               = {r2_cov:.3f}',
       f'R2, trait ~ covariates + PGI         = {r2_full:.3f}',
       f'INCREMENTAL R2 of the PGI            = {r2_full - r2_cov:.3f}', '']
out += group_block('treatment (randomized)', treatment) + ['']
out += group_block('enrolled (self-selected)', enrolled) + ['',
       'Reading: the randomized arms should match (balance IS the finding);',
       'the enrolled groups differ -- not because enrolling edits genomes, but',
       'because self-selection correlates with structure the weights carry.',
       'Same rule as ever: aggregates only; screen before anything leaves.']
Path('results/pgi_summary.txt').write_text('\n'.join(out) + '\n')
print('\n'.join(out))

# --- figures ---------------------------------------------------------------
# Histogram by randomized arm: two overlapping distributions.
fig, ax = plt.subplots(figsize=(7, 4.5))
bins = np.linspace(pgi.min(), pgi.max(), 30)
for v, color in ((0, '#666666'), (1, '#990000')):
    ax.hist(pgi[treatment == v], bins=bins, alpha=0.55, color=color,
            label=f'treatment={v} (n={ (treatment==v).sum() })')
ax.set_xlabel('PGI (sample SD units)'); ax.set_ylabel('people')
ax.set_title('PGI by randomized treatment arm: balanced, as it should be')
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig('results/pgi_hist_treatment.png', dpi=150)

# Kernel density by enrollment. A KDE is just a smoothed histogram: put a
# small Gaussian bump on every observation and add them up. The bandwidth
# (bump width) below is Silverman's rule of thumb; it is a smoothing CHOICE.
def kde(x, grid):
    bw = 1.06 * x.std() * len(x) ** (-1 / 5)     # TRY IT: halve or double bw
    return np.exp(-0.5 * ((grid[:, None] - x) / bw) ** 2).sum(1) / (len(x) * bw * np.sqrt(2 * np.pi))

grid = np.linspace(pgi.min() - .5, pgi.max() + .5, 300)
fig, ax = plt.subplots(figsize=(7, 4.5))
for v, color in ((0, '#666666'), (1, '#990000')):
    ax.plot(grid, kde(pgi[enrolled == v], grid), color=color, lw=2,
            label=f'enrolled={v} (n={ (enrolled==v).sum() })')
    ax.fill_between(grid, kde(pgi[enrolled == v], grid), color=color, alpha=0.15)
ax.set_xlabel('PGI (sample SD units)'); ax.set_ylabel('density')
ax.set_title('PGI by self-selected enrollment: shifted -- selection, not biology')
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig('results/pgi_kde_enrolled.png', dpi=150)

# Mean trait by PGI decile, with a standard-error bar per decile: the classic
# "gradient" figure. Deciles are ~60 people each here, so no cell is small.
edges = np.percentile(pgi, np.linspace(0, 100, 11))
dec = np.clip(np.searchsorted(edges, pgi, side='right') - 1, 0, 9)
means = [trait[dec == d].mean() for d in range(10)]
ses = [trait[dec == d].std() / np.sqrt((dec == d).sum()) for d in range(10)]
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.errorbar(range(1, 11), means, yerr=ses, fmt='o-', color='#990000', capsize=3)
ax.set_xticks(range(1, 11))
ax.set_xlabel('PGI decile (1 = lowest)'); ax.set_ylabel('mean trait (arbitrary units)')
ax.set_title('Trait gradient across PGI deciles')
fig.tight_layout(); fig.savefig('results/pgi_decile_trait.png', dpi=150)

print('Figures written: results/pgi_hist_treatment.png, pgi_kde_enrolled.png, '
      'pgi_decile_trait.png -- open them from the JupyterLab file browser.')

# TRY IT:
#  * Change the KDE bandwidth (bw) and watch smoothing become a judgment call.
#  * Re-draw the histogram by 'sex' instead of 'treatment' -- one line.
#  * Plot ventiles (20 bins) in the gradient figure; when do cells get small
#    enough that the disclosure rule would start biting on real data?
