# Copy to config.aou.sh, fill values, then export WORKSHOP_CONFIG=config.aou.sh.
export DATA_MODE=aou
export INPUT_PREFIX=lab_data/cohort
export PHENO_FILE=lab_data/phenotypes.tsv
export COVAR_FILE=lab_data/covariates.tsv
export PROVENANCE_FILE=lab_data/provenance.json
export PLINK2="${PLINK2:-plink2}"
export THREADS=2
export MEMORY_MB=1024
# Copy these values from the selected workspace. No guessed platform defaults.
export WORKSHOP_BUCKET=''
export BILLING_PROJECT=''
export CDR_DATASET=''

# --- Session 3 (live v9 data). Defaults are the real resource paths; the ---
# --- local sandbox redirects them by setting the same variables.         ---
# Which chromosome to stage and score (small ones keep the lab fast).
export CHROM="${CHROM:-22}"
# HapMap3-filtered per-chromosome PLINK filesets (shared SSGAC resource).
export GENO_SRC="${GENO_SRC:-gs://ssgac-shared-genotype-resources-2026/hm3_filtered_plink1}"
# AoU v9 genetic-ancestry predictions (requester-pays bucket: fetches bill
# BILLING_PROJECT).
export ANC_SRC="${ANC_SRC:-gs://vwb-aou-datasets-controlled/v9/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv}"
# PGI weight file: GWAS summary statistics the instructor posts to the
# shared USC pod bucket, converted to three columns (rsID, effect allele,
# weight; one header line). Point WEIGHTS_URI at that gs:// object -- it may
# live in the pod's shared bucket rather than this workspace's own.
export WEIGHTS_URI="${WEIGHTS_URI:-${WORKSHOP_BUCKET:+$WORKSHOP_BUCKET/pgi_workshop/height_weights.txt}}"
# Phenotype teaching subset: keep 1 person in SAMPLE_MOD (by person_id).
# 10 => ~a tenth of the cohort: fast queries, quick joins. 1 => everyone.
export SAMPLE_MOD="${SAMPLE_MOD:-10}"
