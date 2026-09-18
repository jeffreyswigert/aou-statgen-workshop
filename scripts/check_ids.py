#!/usr/bin/env python3
"""Validate joins by IDs, not row position. Prints counts, never identifiers."""
import sys
from pathlib import Path

def table(path):
    lines=[s.strip() for s in Path(path).read_text().splitlines() if s.strip() and not s.startswith('##')]
    h=lines[0].lstrip('#').split()
    if 'IID' not in h: raise ValueError(f'{path}: needs a header containing IID')
    rows=[dict(zip(h,s.split())) for s in lines[1:]]
    if any(len(s.split()) != len(h) for s in lines[1:]): raise ValueError(f'{path}: malformed row')
    keys=[(d.get('FID','0'),d['IID']) for d in rows]
    if len(keys)!=len(set(keys)): raise ValueError(f'{path}: duplicate sample keys')
    return h,rows,set(keys)
try:
    ph, pr, pids=table(sys.argv[1]); yh, yr, yids=table(sys.argv[2]); ch, cr, cids=table(sys.argv[3])
    for name in ['trait']:
        if name not in yh: raise ValueError('Phenotype file needs trait column')
    for name in ['age','sex','PC1','PC2','PC3','PC4','PC5']:
        if name not in ch: raise ValueError(f'Covariate file needs {name}')
    import math
    for rows, names in [(yr,['trait']),(cr,['age','sex','PC1','PC2','PC3','PC4','PC5'])]:
        for row in rows:
            for name in names:
                value = float(row[name])
                if not math.isfinite(value) or value == -9:
                    raise ValueError(f'{name}: missing/sentinel data; prepare complete cases first')
    # The supplied package deliberately has full matching coverage.
    if not pids <= yids or not pids <= cids: raise ValueError('Genotype samples lack phenotype/covariate rows')
    print(f'Unique genotype keys: {len(pids)}; matched phenotype/covariate keys: {len(pids & yids & cids)}')
except (ValueError,IndexError,KeyError) as e:
    sys.exit(str(e))
