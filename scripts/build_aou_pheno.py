#!/usr/bin/env python3
"""Clean the raw CDR pulls into one analysis row per person (session 3).

Input (from 11_build_phenotype.sh):
  results/raw_height.csv   person_id, value_as_number   (many rows per person)
  results/raw_person.csv   person_id, year_of_birth, sex_at_birth

Output: results/aou_pheno.tsv -- person_id, height_cm, height_z, age, sex.
PERSON-LEVEL REAL DATA: it stays inside the workspace, always.

The cleaning chain, each step a decision a paper must state:
  1. one row per person: the MEDIAN over that person's measurements
     (robust to a stray bad visit; mean and first-visit are rival choices),
  2. plausibility bounds 100-250 cm (program PM height is recorded in cm),
  3. sex kept as recorded for Male/Female, everything else pooled as 'other'
     (too few people for separate strata in a class subset -- a real study
     makes a deliberate, documented choice here),
  4. height_z: standardized WITHIN sex (the convention for height-like
     traits, since pooled-sex height is bimodal), 'other' left unstandardized,
  5. age: survey-era year minus year of birth -- a crude teaching proxy;
     real work uses age at measurement.

Printed counts are ROUNDED to the nearest 100 (and counts of 1-20 are never
printed at all): the funnel remains readable without any cell, or difference
of cells, disclosing a small participant count. Exact Ns live only in the
files that stay in the workspace.

--from-sandbox: no CDR in the sandbox; adapt its pre-built height.pheno and
covar.txt into the same output schema so sessions rehearse end to end.
"""
import csv, statistics, sys
from pathlib import Path

OUT = Path('results/aou_pheno.tsv')
rounded = lambda n: '<=20' if 1 <= n <= 20 else str(round(n, -2))

def write_out(rows):
    with OUT.open('w') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['person_id', 'height_cm', 'height_z', 'age', 'sex'])
        w.writerows(rows)

if '--from-sandbox' in sys.argv:
    # Real .pheno files (and the sandbox's, on purpose) can contain literal
    # 'NA' -- treating it as a number crashes; treating it as data poisons
    # means. Drop those rows, and COUNT what was dropped.
    pheno, n_na = {}, 0
    for l in Path('lab_data/height.pheno').read_text().splitlines():
        fid, iid, v = l.split()
        if v == 'NA':
            n_na += 1
        else:
            pheno[iid] = float(v)
    print(f'Dropped rows with NA phenotype: {rounded(n_na)}')
    covar = {l.split()[1]: (l.split()[2], l.split()[3])
             for l in Path('lab_data/covar.txt').read_text().splitlines()}
    sexmap = {'1': 'Male', '2': 'Female'}    # plink-style 1/2 coding -> labels
    rows = [[iid, f'{v:.4f}', f'{v:.4f}', covar.get(iid, ('', ''))[1],
             sexmap.get(covar.get(iid, ('', ''))[0], 'other')]
            for iid, v in sorted(pheno.items())]
    write_out(rows)
    print(f'SANDBOX phenotype adapted: ~{rounded(len(rows))} people '
          '(values are pre-standardized fixture numbers, not centimeters).')
    sys.exit(0)

heights = {}
with open('results/raw_height.csv') as f:
    for r in csv.DictReader(f):
        heights.setdefault(r['person_id'], []).append(float(r['value_as_number']))
n_people_raw, n_records = len(heights), sum(map(len, heights.values()))

person = {r['person_id']: r for r in csv.DictReader(open('results/raw_person.csv'))}

rows, n_implausible = [], 0
for pid, vals in heights.items():
    h = statistics.median(vals)
    if not 100 <= h <= 250:
        n_implausible += 1
        continue
    p = person.get(pid, {})
    sex = p.get('sex_at_birth', '')
    sex = sex if sex in ('Male', 'Female') else 'other'
    yob = p.get('year_of_birth', '')
    age = str(2026 - int(yob)) if yob.isdigit() else ''
    rows.append([pid, h, sex, age])

# Standardize within sex (step 4).
final = []
for sex in ('Male', 'Female', 'other'):
    grp = [r for r in rows if r[2] == sex]
    if sex != 'other' and len(grp) > 1:
        mu = statistics.mean(r[1] for r in grp)
        sd = statistics.stdev(r[1] for r in grp)
    for r in grp:
        z = f'{(r[1] - mu) / sd:.4f}' if sex != 'other' else ''
        final.append([r[0], f'{r[1]:.1f}', z, r[3], r[2]])
final.sort(key=lambda r: int(r[0]))
write_out(final)

print(f"""Cleaning funnel (counts rounded to the nearest 100; 1-20 suppressed):
  height records pulled            ~{rounded(n_records)}
  people with any measurement      ~{rounded(n_people_raw)}
  removed: implausible (<100/>250) ~{rounded(n_implausible)}
  people in analysis file          ~{rounded(len(final))}
Wrote results/aou_pheno.tsv (person-level -- stays in the workspace).
Next: bash scripts/12_pheno_eda.sh""")
