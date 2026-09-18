#!/usr/bin/env python3
import os,csv
from pathlib import Path

def count(p):return sum(1 for s in Path(p).open() if s.strip() and not s.startswith('#'))
rows=[]
for label,p in [('input',os.environ['INPUT_PREFIX']),('eligible_sites','results/sites'),('sample_filter','results/samples'),('variant_filter','results/qc')]:
    rows.append([label,count(p+'.psam'),count(p+'.pvar')])
with open('results/qc_counts.tsv','w') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['stage','samples','variants']);w.writerows(rows)
print(Path('results/qc_counts.tsv').read_text())
