#!/usr/bin/env bash
# 11_build_phenotype.sh (Lab 1, live data) -- build a REAL phenotype from the v9 CDR.
#
# Two BigQuery pulls, then Python cleaning:
#   1. standing height records: program physical-measurement SOURCE concept
#      903133 -- NOT the standard LOINC concept, which silently pools in EHR
#      heights (the worked example of why concept choice is a decision),
#   2. person table: year of birth and sex at birth,
# then scripts/build_aou_pheno.py reduces to ONE ROW PER PERSON, applies
# plausibility bounds, and writes results/aou_pheno.tsv (person-level: it
# STAYS IN THE WORKSPACE).
#
# By default only persons with person_id % SAMPLE_MOD == 0 are pulled --
# a fast teaching subset (~a tenth of the cohort). SAMPLE_MOD=1 pulls all.
source "$(dirname "$0")/common.sh"


command -v bq >/dev/null || { echo 'bq (BigQuery CLI) not found -- run on the AoU Workbench VM.' >&2; exit 1; }
: "${CDR_DATASET:?Set CDR_DATASET (project.dataset of the CDR) in your config}"
: "${BILLING_PROJECT:?Set BILLING_PROJECT in your config}"

run_bq() {  # capped CSV query -> file. ~$0.16 max per query at the default cap.
  local out="$1"; shift
  bq --project_id="$BILLING_PROJECT" query --use_legacy_sql=false --quiet \
     --format=csv --max_rows=10000000 \
     --maximum_bytes_billed="${MAX_BYTES_BILLED:-25000000000}" "$1" > "$out"
  # An empty result here means a wrong dataset reference or concept -- stop
  # now, not at the join.
  [[ $(wc -l < "$out") -gt 1 ]] || { echo "Query returned nothing: $out" >&2; exit 1; }
}

echo "Pulling height measurements (source concept 903133), 1/${SAMPLE_MOD} of persons ..."
run_bq results/raw_height.csv "
  SELECT person_id, value_as_number
  FROM \`$CDR_DATASET.measurement\`
  WHERE measurement_source_concept_id = 903133
    AND value_as_number IS NOT NULL
    AND MOD(person_id, $SAMPLE_MOD) = 0"

echo 'Pulling year of birth and sex at birth ...'
run_bq results/raw_person.csv "
  SELECT p.person_id, p.year_of_birth, c.concept_name AS sex_at_birth
  FROM \`$CDR_DATASET.person\` p
  JOIN \`$CDR_DATASET.concept\` c ON c.concept_id = p.sex_at_birth_concept_id
  WHERE MOD(p.person_id, $SAMPLE_MOD) = 0"

python3 scripts/build_aou_pheno.py

# What we did NOT do, deliberately, and a real study must decide: units were
# trusted (program PM height is centimeters by construction); repeated visits
# were collapsed by median; remote self-report is pooled with clinic
# measurement (they share concept 903133 -- separable via measurement_ext
# src_id); age is survey-year minus birth year, a crude teaching proxy.
