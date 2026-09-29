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
