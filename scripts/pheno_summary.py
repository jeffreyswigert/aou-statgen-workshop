#!/usr/bin/env python3
"""Summary statistics for one REAL AoU phenotype from data/pheno_menu.tsv.

Queries the CDR through BigQuery and prints aggregates only -- never a
participant-level row. Every query is byte-capped. Counts of 1-20 are
suppressed on output (with complementary suppression, so a lone hidden cell
cannot be recovered by subtracting the visible ones from the total).

  bash scripts/06_pheno_summary.sh            # show the menu
  bash scripts/06_pheno_summary.sh height     # summarize one phenotype
  DRY_RUN=1 bash scripts/06_pheno_summary.sh height   # print SQL, query nothing

First lines of output are the resolved concept names straight from the CDR's
concept table: read them. A concept ID is a claim until the name confirms it.
"""
import csv, io, os, subprocess, sys
from pathlib import Path

MAX_BYTES = int(os.environ.get('MAX_BYTES_BILLED', 25_000_000_000))  # ~ $0.16
menu = {r['id']: r for r in csv.DictReader(open('data/pheno_menu.tsv'), delimiter='\t')}

if len(sys.argv) != 2 or sys.argv[1] not in menu:
    print(__doc__)
    print(f"{'id':<18}{'source':<15}label")
    for r in menu.values():
        print(f"{r['id']:<18}{r['source']:<15}{r['label']}")
    sys.exit(0 if len(sys.argv) == 1 else 1)

e = menu[sys.argv[1]]
ids = e['concept_ids']
cdr, bp = os.environ.get('CDR_DATASET', ''), os.environ.get('BILLING_PROJECT', '')
dry = os.environ.get('DRY_RUN') == '1'
if not dry and (not cdr or not bp):
    sys.exit('Set CDR_DATASET (project.dataset of the CDR) and BILLING_PROJECT '
             'in config.sh -- both are on your workspace resource pages.')

CONCEPT_SQL = (f"SELECT concept_id, concept_name, vocabulary_id "
               f"FROM `{cdr}.concept` WHERE concept_id IN ({ids}) ORDER BY concept_id")
if e['value_kind'] == 'numeric':
    MAIN_SQL = f"""WITH per_person AS (
  SELECT person_id, AVG(value_as_number) AS v
  FROM `{cdr}.{e['table']}`
  WHERE {e['concept_column']} IN ({ids}) AND value_as_number IS NOT NULL
  GROUP BY person_id)
SELECT COUNT(*) AS n_people, ROUND(AVG(v),2) AS mean, ROUND(STDDEV(v),2) AS sd,
  ROUND(APPROX_QUANTILES(v,4)[OFFSET(1)],1) AS p25,
  ROUND(APPROX_QUANTILES(v,4)[OFFSET(2)],1) AS median,
  ROUND(APPROX_QUANTILES(v,4)[OFFSET(3)],1) AS p75
FROM per_person"""
elif e['value_kind'] == 'categorical':
    MAIN_SQL = f"""SELECT c.concept_name AS answer, COUNT(DISTINCT o.person_id) AS n_people
FROM `{cdr}.{e['table']}` o
JOIN `{cdr}.concept` c ON c.concept_id = o.value_source_concept_id
WHERE o.{e['concept_column']} IN ({ids})
GROUP BY answer ORDER BY n_people DESC"""
else:  # case_count: people with any condition under these ancestor concepts
    MAIN_SQL = f"""SELECT COUNT(DISTINCT co.person_id) AS n_cases
FROM `{cdr}.condition_occurrence` co
JOIN `{cdr}.concept_ancestor` ca ON co.condition_concept_id = ca.descendant_concept_id
WHERE ca.ancestor_concept_id IN ({ids})"""

if dry:
    print(CONCEPT_SQL, MAIN_SQL, sep='\n\n')
    sys.exit(0)

def bq(sql):
    r = subprocess.run(['bq', f'--project_id={bp}', 'query', '--use_legacy_sql=false',
                        '--quiet', '--format=csv', f'--maximum_bytes_billed={MAX_BYTES}',
                        sql], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'bq failed:\n{r.stderr.strip()}')
    return list(csv.DictReader(io.StringIO(r.stdout)))

def shown(n):  # the dissemination policy prohibits counts of 1-20; 0 is fine
    return str(n) if n == 0 or n > 20 else '<=20 (suppressed)'

out = [f"{e['label']}  [{e['id']}]", f"source: {e['source']}"
       + (f"   unit: {e['unit']}" if e['unit'] else ''),
       '', 'Resolved concepts (confirm the names match your intent):']
out += [f"  {r['concept_id']}  {r['vocabulary_id']:<8} {r['concept_name']}"
        for r in bq(CONCEPT_SQL)] or ['  NONE RESOLVED -- wrong concept ID or CDR']
out.append('')

rows = bq(MAIN_SQL)
if e['value_kind'] == 'numeric':
    r = rows[0]
    if int(r['n_people']) <= 20:
        out.append(f"n_people = {shown(int(r['n_people']))}; statistics withheld.")
    else:
        out += [f"{k:>10}: {r[k]}" for k in ('n_people', 'mean', 'sd', 'p25', 'median', 'p75')]
elif e['value_kind'] == 'categorical':
    vis = [(r['answer'], int(r['n_people'])) for r in rows]
    hide = [r for r in vis if 1 <= r[1] <= 20]
    vis = [r for r in vis if r not in hide]
    if len(hide) == 1 and vis:      # complementary suppression: one hidden cell
        vis.sort(key=lambda r: r[1])  # is derivable from the others, so fold the
        hide.append(vis.pop(0))       # smallest visible cell in with it
    for a, n in sorted(vis, key=lambda r: -r[1]):
        out.append(f"  {n:>8}  {a}")
    if hide:
        out.append(f"  {shown(sum(n for _, n in hide)) if sum(n for _, n in hide) > 20 else '<=20 (suppressed)':>8}"
                   f"  ({len(hide)} answers combined for disclosure control)")
else:
    out.append(f"n_cases = {shown(int(rows[0]['n_cases']))}")

out += ['', f"note: {e['note']}",
        'Aggregates only; still subject to the AoU dissemination policy before sharing.']
Path('results').mkdir(exist_ok=True)
Path(f"results/pheno_{e['id']}_summary.txt").write_text('\n'.join(out) + '\n')
print('\n'.join(out))
