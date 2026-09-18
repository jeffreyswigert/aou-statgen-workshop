#!/usr/bin/env python3
"""Validate that genotype, phenotype, and covariate files join BY SAMPLE ID.

Why this exists: a join by row position can "work" perfectly -- every command
succeeds -- while attaching person 3's genotypes to person 1's outcome. No
error is ever raised; the results are simply wrong. So before any modeling we
check, by ID: keys are unique, every column we need exists, every value is a
real number, and every genotyped sample has phenotype and covariate rows.

Prints only COUNTS, never identifiers -- safe to run and show with real data.

Usage: check_ids.py <psam> <phenotypes.tsv> <covariates.tsv>
"""
import sys
from pathlib import Path

def table(path):
    """Read a whitespace-delimited table; return (header, rows, key set)."""
    lines = [s.strip() for s in Path(path).read_text().splitlines()
             if s.strip() and not s.startswith('##')]
    h = lines[0].lstrip('#').split()           # header may start with '#'
    if 'IID' not in h:
        raise ValueError(f'{path}: needs a header containing IID')
    rows = [dict(zip(h, s.split())) for s in lines[1:]]
    # A row with the wrong number of fields usually means a stray space or a
    # missing value -- catch it here, not three scripts later.
    if any(len(s.split()) != len(h) for s in lines[1:]):
        raise ValueError(f'{path}: malformed row')
    # The sample key is (FID, IID) where FID exists, else just IID. Duplicate
    # keys would make any join ambiguous.
    keys = [(d.get('FID', '0'), d['IID']) for d in rows]
    if len(keys) != len(set(keys)):
        raise ValueError(f'{path}: duplicate sample keys')
    return h, rows, set(keys)

try:
    ph, pr, pids = table(sys.argv[1])   # genotype sample metadata (.psam)
    yh, yr, yids = table(sys.argv[2])   # phenotypes
    ch, cr, cids = table(sys.argv[3])   # covariates

    # The columns the analysis is about to ask for must exist BY NAME.
    for name in ['trait']:
        if name not in yh: raise ValueError('Phenotype file needs trait column')
    for name in ['age', 'sex', 'PC1', 'PC2', 'PC3', 'PC4', 'PC5']:
        if name not in ch: raise ValueError(f'Covariate file needs {name}')

    # Every value must be a real, finite number. -9 is a legacy "missing"
    # sentinel in this field; treating it as data would quietly poison means
    # and regressions, so we refuse it outright.
    import math
    for rows, names in [(yr, ['trait']), (cr, ['age', 'sex', 'PC1', 'PC2', 'PC3', 'PC4', 'PC5'])]:
        for row in rows:
            for name in names:
                value = float(row[name])
                if not math.isfinite(value) or value == -9:
                    raise ValueError(f'{name}: missing/sentinel data; prepare complete cases first')

    # The supplied package deliberately has full matching coverage. (A real
    # study usually has partial overlap -- then you REPORT the overlap and
    # decide the analysis sample explicitly, rather than requiring 100%.)
    if not pids <= yids or not pids <= cids:
        raise ValueError('Genotype samples lack phenotype/covariate rows')
    print(f'Unique genotype keys: {len(pids)}; matched phenotype/covariate keys: {len(pids & yids & cids)}')
except (ValueError, IndexError, KeyError) as e:
    sys.exit(str(e))   # exit nonzero with the message -- callers stop here
