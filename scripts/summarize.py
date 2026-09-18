#!/usr/bin/env python3
"""Digest plink2's association report into two small, readable files.

Input:  results/assoc.trait.glm.linear (one row per variant tested)
Output: results/top_hits.tsv          (the strongest associations)
        results/analysis_summary.txt  (test counts + multiple-testing bar)

Worth internalizing here: we only keep rows where TEST is 'ADD' (the additive
allele-count effect -- the row you usually want) AND the p-value is a real,
finite number AND plink reported no error code. Filtering on validity BEFORE
sorting by p-value matters: a broken test can masquerade as a tiny p-value.
"""
import csv, math
from pathlib import Path

TOP_N = 5   # TRY IT: change to 20 and re-run -- python3 scripts/summarize.py
            # (safe to re-run alone; it only reads the existing .glm.linear)

p = Path('results/assoc.trait.glm.linear')
lines = p.read_text().splitlines()
header = lines[0].lstrip('#').split()          # first line names the columns
rows = [dict(zip(header, l.split())) for l in lines[1:]]

# Keep the additive-effect rows...
add = [r for r in rows if r['TEST'] == 'ADD']
# ...and of those, only tests that actually succeeded.
valid = [r for r in add
         if r.get('ERRCODE', '.') == '.'      # '.' means "no error"
         and r['P'] != 'NA'
         and math.isfinite(float(r['P']))]

# Smallest p-value first.
valid.sort(key=lambda r: float(r['P']))

cols = ['ID', 'A1', 'OBS_CT', 'BETA', 'SE', 'P', 'ERRCODE']
with open('results/top_hits.tsv', 'w') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(cols)
    for r in valid[:TOP_N]:
        w.writerow([r.get(c, '.') for c in cols])

# The Bonferroni bar: with this many tests, "significant" starts at 0.05/N.
Path('results/analysis_summary.txt').write_text(
    f'Additive tests: {len(add)}\n'
    f'Valid p-values: {len(valid)}\n'
    f'Failed tests: {len(add) - len(valid)}\n'
    f'Bonferroni threshold for this exercise: {0.05 / len(valid):.4g}\n'
    if valid else
    'No valid association tests. Inspect the PLINK log and ERRCODE.\n')

print(Path('results/analysis_summary.txt').read_text())
print(Path('results/top_hits.tsv').read_text())
