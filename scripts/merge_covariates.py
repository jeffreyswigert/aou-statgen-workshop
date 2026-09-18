#!/usr/bin/env python3
import csv
from pathlib import Path

def read(path):
    lines=Path(path).read_text().splitlines();h=lines[0].lstrip('#').split()
    return [dict(zip(h,l.split())) for l in lines[1:] if l.strip()]
a=read('data/base_covariates.tsv'); b={r['IID']:r for r in read('results/prep_pca.eigenvec')}
with open('data/covariates.tsv','w') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['#IID','age','sex']+[f'PC{i}' for i in range(1,6)])
    for r in a:w.writerow([r['IID'],r['age'],r['sex']]+[b[r['IID']][f'PC{i}'] for i in range(1,6)])
