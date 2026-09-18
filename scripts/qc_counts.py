#!/usr/bin/env python3
"""Write the QC funnel: samples and variants remaining after each stage.

Reads nothing but the .psam (one line per sample) and .pvar (one line per
variant) files that each QC stage produced -- counting lines in those text
files IS counting samples and variants. Output: results/qc_counts.tsv.

This little table is the audit trail: every exclusion, with its stage. If you
cannot narrate it, you are not done with QC.
"""
import os, csv
from pathlib import Path

def count(p):
    # Count non-empty lines, skipping header lines that start with '#'.
    return sum(1 for s in Path(p).open() if s.strip() and not s.startswith('#'))

# The four fileset prefixes, in the order the stages ran. Each contributes one
# row: (stage label, sample count from .psam, variant count from .pvar).
rows = []
for label, p in [('input', os.environ['INPUT_PREFIX']),
                 ('eligible_sites', 'results/sites'),
                 ('sample_filter', 'results/samples'),
                 ('variant_filter', 'results/qc')]:
    rows.append([label, count(p + '.psam'), count(p + '.pvar')])

with open('results/qc_counts.tsv', 'w') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(['stage', 'samples', 'variants'])
    w.writerows(rows)
print(Path('results/qc_counts.tsv').read_text())

# TRY IT: with real data this innocent table is a disclosure hazard -- two of
# its rows differ by 12 samples, a participant count the AoU policy says may
# not be derivable from published numbers. Run the screen and see it flagged:
#   python3 scripts/check_disclosure.py results
