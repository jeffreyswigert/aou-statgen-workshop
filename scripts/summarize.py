#!/usr/bin/env python3
import csv,math
from pathlib import Path
p=Path('results/assoc.trait.glm.linear')
lines=p.read_text().splitlines();header=lines[0].lstrip('#').split()
rows=[dict(zip(header,l.split())) for l in lines[1:]]
add=[r for r in rows if r['TEST']=='ADD']
valid=[r for r in add if r.get('ERRCODE','.')=='.' and r['P']!='NA' and math.isfinite(float(r['P']))]
valid.sort(key=lambda r:float(r['P']))
cols=['ID','A1','OBS_CT','BETA','SE','P','ERRCODE']
with open('results/top_hits.tsv','w') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(cols)
    for r in valid[:5]:w.writerow([r.get(c,'.') for c in cols])
Path('results/analysis_summary.txt').write_text(f'Additive tests: {len(add)}\nValid p-values: {len(valid)}\nFailed tests: {len(add)-len(valid)}\nBonferroni threshold for this exercise: {0.05/len(valid):.4g}\n' if valid else 'No valid association tests. Inspect the PLINK log and ERRCODE.\n')
print(Path('results/analysis_summary.txt').read_text())
print(Path('results/top_hits.tsv').read_text())
