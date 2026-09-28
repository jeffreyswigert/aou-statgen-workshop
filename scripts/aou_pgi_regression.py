#!/usr/bin/env python3
"""A basic regression incorporating the PGI (lab step 4).

Model:  height_z ~ PGI + age + female + PC1..PC5

Where each piece comes from, and the decision it carries:
  height_z   results/aou_pheno.tsv -- already standardized WITHIN sex, so
             the outcome is in within-sex SD units.
  PGI        results/aou_pgi.sscore, standardized to mean 0 / SD 1 here, so
             the headline coefficient reads "SD of height per SD of PGI".
  age, sex   the phenotype file. Rows missing either are DROPPED and
             counted. People recorded outside Male/Female are excluded from
             this model (their height_z was never defined -- see
             build_aou_pheno.py); a real study states its own choice.
  PC1..PC5   parsed from lab_data/ancestry_preds.tsv, whose pca_features
             column is a STRINGIFIED list ("[-0.009, ...]") keyed by
             research_id -- two real-file quirks handled in code below.

Output: results/aou_pgi_regression.txt -- coefficient table (estimate,
classical OLS SE, t), R2, and the PGI's incremental R2 over the covariates.
Printed Ns are rounded to the nearest 100; counts of 1-20 never print.

What this model deliberately is NOT: ordinary OLS assumes independent
people (relatives violate that), five PCs are a convention rather than a
guarantee against structure, and a one-chromosome PGI
is a partial index. The mechanics are real; the estimate is a classroom
estimate.

TRY IT: drop the PCs from COVARS below and re-run. On real data the PGI
coefficient will move -- that movement is structure, and it is exactly why
the PCs are in the model.
"""
import numpy as np
from pathlib import Path

COVARS = ['age', 'female'] + [f'PC{i}' for i in range(1, 6)]

def read_keyed(path):
    lines = Path(path).read_text().splitlines()
    h = lines[0].lstrip('#').split('\t')
    return h, [l.split('\t') for l in lines[1:] if l.strip()]

sh, srows = read_keyed('results/aou_pgi.sscore')
score = {r[0]: float(r[sh.index('SCORE1_SUM')]) for r in srows}
ph, prows = read_keyed('results/aou_pheno.tsv')
pheno = {r[0]: r for r in prows}
# ancestry_preds: key column is research_id (same values as person_id), and
# pca_features holds the PCs as one bracketed string per person.
ah, arows = read_keyed('lab_data/ancestry_preds.tsv')
ai = ah.index('pca_features')
pcs = {r[0]: [float(x) for x in r[ai].strip('[]').split(',')[:5]] for r in arows}

rows, n_dropped = [], 0
for iid in sorted(set(score) & set(pheno) & set(pcs)):
    r = pheno[iid]                       # person_id, height_cm, height_z, age, sex
    if r[2] and r[3] and r[4] in ('Male', 'Female'):
        rows.append([float(r[2]), score[iid], float(r[3]),
                     1.0 if r[4] == 'Female' else 0.0] + pcs[iid])
    else:
        n_dropped += 1

y = np.array([r[0] for r in rows])
X = np.array([r[1:] for r in rows])
X[:, 0] = (X[:, 0] - X[:, 0].mean()) / X[:, 0].std()      # standardize the PGI
n, k = X.shape

def fit(Xs):
    """OLS with intercept: returns beta, classical SEs, R2."""
    M = np.column_stack([np.ones(len(y)), Xs])
    beta, *_ = np.linalg.lstsq(M, y, rcond=None)
    resid = y - M @ beta
    r2 = 1 - resid.var() / y.var()
    sigma2 = resid @ resid / (len(y) - M.shape[1])
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(M.T @ M)))
    return beta, se, r2

beta, se, r2_full = fit(X)
_, _, r2_cov = fit(X[:, 1:])            # covariates only, no PGI

rounded = lambda m: '<=20 (suppressed)' if 1 <= m <= 20 else f'~{round(m, -2):,}'
names = ['(intercept)', 'PGI'] + COVARS
out = ['Regression: height_z ~ PGI + age + female + PC1..PC5  (real data; classroom estimate)',
       f'Analysis N: {rounded(n)}   (rows dropped for missing age/sex or non-M/F: {rounded(n_dropped)})', '',
       f"{'term':<12}{'estimate':>10}{'SE':>9}{'t':>8}"]
out += [f'{nm:<12}{b:>10.4f}{s:>9.4f}{b / s:>8.2f}' for nm, b, s in zip(names, beta, se)]
out += ['',
        f'R2 with PGI    = {r2_full:.4f}',
        f'R2 covariates  = {r2_cov:.4f}',
        f'incremental R2 = {r2_full - r2_cov:.4f}', '',
        'Reading the headline row: a person one SD higher in this PGI is '
        f'{beta[1]:+.3f} SD taller,',
        'conditional on age, sex, and five PCs. Association, not cause; one',
        'chromosome, not a full index; independent-samples OLS, not a family model.']
Path('results/aou_pgi_regression.txt').write_text('\n'.join(out) + '\n')
print('\n'.join(out))
