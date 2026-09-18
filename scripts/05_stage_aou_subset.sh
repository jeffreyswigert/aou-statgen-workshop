#!/usr/bin/env bash
# Only a SMALL, instructor-prepared bundle in an authorized workspace bucket.
# Usage: bash scripts/05_stage_aou_subset.sh gs://BUCKET/path/to/prepared-subset
set -euo pipefail
cd "$(dirname "$0")/.."
uri="${1:?Supply the instructor-prepared subset folder gs:// URI}"
[[ "$uri" == gs://* ]] || exit 1
command -v gcloud >/dev/null
mkdir -p lab_data
for name in cohort.psam cohort.pvar phenotypes.tsv covariates.tsv provenance.json; do
  gcloud storage cp "${uri%/}/$name" "lab_data/$name"
done
# Inspect metadata BEFORE copying genotype bytes. Refuse biobank-scale inputs.
python3 - <<'PY'
from pathlib import Path
import json
count=lambda f:sum(1 for s in Path(f).open() if s.strip() and not s.startswith('#'))
n=count('lab_data/cohort.psam');m=count('lab_data/cohort.pvar')
assert 100 <= n <= 5000, 'Instructor subset must contain 100..5000 samples'
assert 100 <= m <= 50000, 'Instructor subset must contain 100..50000 variants'
p=json.loads(Path('lab_data/provenance.json').read_text())
for k in ['cdr_release','genome_build','callset','source_uri','sample_selection','site_filtering','genotype_filtering','pc_source','phenotype_definition','relatedness_strategy']:
 assert p.get(k), f'provenance.json needs {k}'
assert p.get('data_mode')=='aou', 'Expected an AoU subset manifest'
print(f'Metadata validated: {n} samples, {m} variants. Keep all results inside the Workbench.')
PY
python3 scripts/check_ids.py lab_data/cohort.psam lab_data/phenotypes.tsv lab_data/covariates.tsv
gcloud storage cp "${uri%/}/cohort.pgen" lab_data/cohort.pgen
printf 'Prepared subset staged. Use config.aou.sh in a fresh workshop directory.\n'
