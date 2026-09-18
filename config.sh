# ---------------------------------------------------------------------------
# config.sh -- every setting the workshop scripts use, in one place.
#
# The scripts read these as environment variables. "export" makes a variable
# visible to the programs this shell starts. The pattern ${NAME:-fallback}
# means "use $NAME if it is already set, otherwise use the fallback" -- so you
# can override any of these for one run without editing this file:
#
#     PLINK2=/some/other/plink2 bash scripts/02_qc.sh
#
# Nothing here is secret; with real AoU data you would still never commit
# bucket contents or results, but the *names* of buckets are fine.
# ---------------------------------------------------------------------------

# Which dataset the scripts believe they are analyzing. "synthetic" relaxes a
# few safety rails; "aou" (see config.aou.example.sh) tightens them -- most
# importantly, the disclosure screen BLOCKS the save step on findings.
export DATA_MODE=synthetic

# The input genotype fileset, WITHOUT extension: data/toy means the trio
# data/toy.pgen + data/toy.pvar + data/toy.psam.
export INPUT_PREFIX=data/toy

# Phenotype and covariate tables (tab-separated, one row per person, joined to
# the genotypes by the IID sample key -- never by row order).
export PHENO_FILE=data/phenotypes.tsv
export COVAR_FILE=data/covariates.tsv

# A small JSON record of where the data came from; archived with every save.
export PROVENANCE_FILE=data/provenance.json

# Which plink2 executable to run. Default: whatever "plink2" is on your PATH.
# If the instructor staged a local build:  export PLINK2="$PWD/tools/plink2"
export PLINK2="${PLINK2:-plink2}"

# Compute settings passed to every plink2 call (see the p2 helper in
# scripts/common.sh). Small on purpose: this exercise needs seconds, and a
# polite reservation will not fight other processes on a shared or small VM.
export THREADS=2
export MEMORY_MB=1024

# --- Cloud settings: the instructor fills these from the workspace's own ---
# --- resource pages. They are OUR variable names, not names the platform ---
# --- promises to set for you.                                            ---

# Where scripts/04_save.sh copies the run archive. Must be a bucket this
# workspace is authorized to write to.
# WORKSHOP_BUCKET falls back to WORKSPACE_BUCKET when that is set, so the same
# scripts run unchanged inside the local AoU sandbox (source its env.sh first)
# and against a real authorized bucket. Verify the value before an AoU save.
export WORKSHOP_BUCKET="${WORKSHOP_BUCKET:-${WORKSPACE_BUCKET:-}}"

# The Google Cloud project that pays for storage/query operations, and the
# BigQuery dataset reference (project.dataset) of the Curated Data Repository.
# Both are needed only for cloud saving and the live-phenotype exercise.
export BILLING_PROJECT="${BILLING_PROJECT:-}"
export CDR_DATASET="${CDR_DATASET:-}"
