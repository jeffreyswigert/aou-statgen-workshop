# Statistical genetics on All of Us: hands-on with your Workbench

Materials for a one-hour workshop — **Lab 1** — run entirely on **real
All of Us v9 data** (Controlled Tier required): 20 minutes of instruction and
40 hands-on minutes in which you

1. **explore** a real variable (summary statistics and histograms),
2. **construct a phenotype** from raw CDR records — QC'd, plausibility-bounded,
   one row per person,
3. **build a PGI** with PLINK on a single chromosome, from GWAS summary
   statistics posted to the shared USC pod bucket, and
4. **run a basic regression** that incorporates the PGI.

The goal is confidence with your *actual* Workbench: real queries, real
files, real conventions, real rules.

## Lab 1 quick start (on your AoU Workbench VM)

Open a Terminal from the JupyterLab Launcher, then:

```bash
git clone https://github.com/jeffreyswigert/aou-statgen-workshop.git aou_cli_workshop
cd aou_cli_workshop
cp config.aou.example.sh config.aou.sh    # fill the values your instructor projects
export WORKSHOP_CONFIG=config.aou.sh      # per terminal!
bash scripts/00_preflight.sh
bash scripts/10_fetch_aou_genotypes.sh    # one HM3-filtered chromosome + ancestry file
bash scripts/11_build_phenotype.sh        # height from the CDR (source concept 903133)
bash scripts/12_pheno_eda.sh              # cleaning funnel, summary stats, histograms
bash scripts/13_score_real_pgi.sh         # posted GWAS weights -> PGI + ancestry KDE
bash scripts/14_pgi_regression.sh         # height_z ~ PGI + age + sex + 5 PCs
bash scripts/04_save.sh                   # disclosure gate is live in AoU mode
```

Follow along in `lab1_handout.pdf`; `aou_realdata_workshop.pdf` is the slide
deck. There is **no answer key** — your numbers are real; the handout gives
plausibility checks instead. Figures are PNGs in `results/`; open them from
the JupyterLab file browser.

Ground rules baked into the scripts: person-level files never leave the
workspace; printed counts are aggregate, rounded to the nearest 100, and
counts of 1–20 are suppressed; every query is byte-capped; and the save step
runs a disclosure screen that **blocks** on findings in AoU mode.

## What's here

- `lab1_handout.pdf` / `aou_realdata_workshop.pdf` — the workshop.
- `scripts/` — short, heavily commented Bash and Python; read each one before
  running it. Each ends with a TRY IT.
- `config.aou.example.sh` — template for the values your instructor supplies
  (bucket, billing project, CDR dataset, weights location).
- `docs/SOURCES.md` — the readings and every platform/software reference used.
- A **synthetic self-study track** and a **stretch exercise** (below).

## Optional self-study: the synthetic track

Two earlier, fully synthetic modules remain in this repo for practice without
Controlled Tier access, at home or in the free local sandbox. **No All of Us
participant records are involved** in this track, and none of its results
have biological meaning.

**A. First workflow** (`lab_handout.pdf`, `aou_cli_workshop.pdf`): inspect a
PLINK fileset, run sequential QC, fit a covariate-adjusted association scan,
save a reproducible run.

```bash
bash scripts/00_preflight.sh && bash scripts/02_qc.sh
bash scripts/03_association.sh && bash scripts/04_save.sh
```

Expected: 600 samples / 2,400 variants → 588 / 2,330 after QC; top hit
`SIMV001201` (allele G, beta ≈ 0.93, N = 587). Match `expected/` and it worked.

**B. PGIs on synthetic data** (`lab2_handout.pdf`, `aou_pgi_workshop.pdf`):
score deliberately imperfect consortium-style weights (`data/pgi_weights.txt`),
then compare the PGI across a randomized group (balanced, −0.01 SD) and a
self-selected one (shifted, +0.46 SD — selection and structure, not biology).

```bash
ls results/qc.pgen || bash scripts/02_qc.sh
bash scripts/07_score_pgi.sh && bash scripts/08_pgi_eda.sh
```

## Stretch exercise: summarize more real phenotypes

With your Lab 1 config in place, `data/pheno_menu.tsv` offers nine real
phenotypes spanning program measurements, EHR labs, surveys, and EHR
conditions, each annotated with its source type's trap:

```bash
bash scripts/06_pheno_summary.sh            # show the menu
bash scripts/06_pheno_summary.sh ldl        # aggregates only, byte-capped
```

The script resolves and prints concept names first (an ID is a claim until
the name confirms it) and suppresses counts of 1–20. Find the same phenotype
in the public [Data Browser](https://databrowser.researchallofus.org) to see
where concept IDs come from.

## Two habits this workshop teaches

**Compliance as a default.** `scripts/check_disclosure.py` runs inside every
save: it lists participant-level files that must stay in the workspace and
flags participant counts of 1–20 — direct, or derivable by subtraction between
reported numbers — which the AoU Data and Statistics Dissemination Policy
restricts. In AoU mode a finding blocks the save until fixed or explicitly
acknowledged after review. Adapt it to your own pipelines; it complements
manual review of text, figures, and percentages, never replaces it.

**Test the plumbing before you pay for a VM.** Every Lab 1 script (except the
BigQuery step, which substitutes a fixture) also runs on your laptop against
a local All of Us sandbox that mirrors the platform's paths, file names, and
environment variables with fake data. Source its `env.sh`, run the same
commands (`DEMO_WEIGHTS=1` for the scoring step), and even the cloud save
lands in a fake local bucket. Ask your instructor for the sandbox repository.

## After the workshop

These scripts demonstrate a workflow, not a complete AoU analysis protocol:
ordinary regression does not account for relatives, five PCs are a convention
rather than a guarantee, a one-chromosome PGI is deliberately partial, and
real phenotype definitions need release-specific care. To scale up: set
`SAMPLE_MOD=1` for the full cohort, loop `CHROM` over 1–22 and sum the
`.sscore` SUM columns, and swap in your own trait's concept ID and weights.
The readings in `docs/SOURCES.md` are the next step.
