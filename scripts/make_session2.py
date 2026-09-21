#!/usr/bin/env python3
"""Generate the session-2 data: PGI weights and group assignments.

Run via 07_score_pgi.sh only if the files are missing -- data/ ships ready.
Python standard library only; everything is seeded, so rebuilds are identical.

Two files:

data/pgi_weights.txt -- plays the role of PUBLISHED DISCOVERY-GWAS weights
  from a large external consortium (in real life: the PGI Repository or a
  GWAS catalog). Deliberately realistic, which means deliberately imperfect:
    * covers only ~5 of every 6 of our variants (panels never match fully),
    * ~500 rows name the OTHER allele as the effect allele, with the sign
      flipped accordingly -- a legitimate, equivalent orientation that PLINK
      harmonizes because the effect allele is NAMED (the lesson: orientation
      is a non-issue when alleles are named; unstated strand is what bites),
    * 15 rows carry rsIDs our data has never heard of (ID-scheme mismatch),
    * weights = the true planted effect + noise + a small leak of the
      between-stratum frequency difference, mimicking a discovery GWAS with
      imperfect ancestry control -- THE reason PGI distributions can shift
      across groups for non-causal reasons.

data/groups.tsv -- two group labels per person:
    treatment  randomized 0/1 (a fair coin): the PGI should be BALANCED here,
               and finding nothing is the correct result.
    enrolled   self-selected program participation, more likely in stratum B
               and among high-trait people: the PGI should SHIFT here -- not
               because enrollment changes anyone's genome, but because
               selection is correlated with structure the weights leak.

The stratum of person i is simply i % 2 (see make_synthetic.py), and variants
101-700 are the ones whose allele frequencies differ by stratum.
"""
import random
from pathlib import Path

r = random.Random(20260921)
out = Path('data')
n, m = 600, 2400
ids = [f'SIM{i+1:04d}' for i in range(n)]
group = [i % 2 for i in range(n)]          # matches make_synthetic.py exactly

# --- weights ---------------------------------------------------------------
# Expected ALT-frequency difference (stratum1 - stratum0) is +0.26 at the
# structured variants (see make_synthetic.py: +0.18 vs -0.08), else 0.
LEAK = 0.012        # tuned so the stratum PGI gap is ~1 SD -- visible, not silly
rows = []
for j in range(m):
    if j != 1200 and r.random() < 1/6:      # panel overlap is never complete
        continue
    d = 0.26 if 100 <= j < 700 else 0.0
    w = (0.9 if j == 1200 else 0.0) + r.gauss(0, 0.03) + LEAK * d * r.uniform(0.5, 1.5)
    eff, oth = 'G', 'A'                     # our data is REF=A / ALT=G throughout
    if r.random() < 0.25:                   # equivalent flipped orientation
        eff, oth, w = 'A', 'G', -w
    rows.append([f'SIMV{j+1:06d}', '22', eff, oth, f'{w:.6f}'])
for k in range(15):                         # IDs from a different naming scheme
    rows.append([f'rs{7000000+k}', '22', 'G', 'A', f'{r.gauss(0, 0.03):.6f}'])
r.shuffle(rows)
with (out / 'pgi_weights.txt').open('w') as f:
    f.write('SNP\tCHR\teffect_allele\tother_allele\tbeta\n')
    f.writelines('\t'.join(row) + '\n' for row in rows)

# --- groups ----------------------------------------------------------------
# Trait median split for the self-selection mechanism, computed from the
# shipped phenotype file so this script never re-generates the trait.
pheno = {l.split()[0]: float(l.split()[1])
         for l in (out / 'phenotypes.tsv').read_text().splitlines()[1:]}
med = sorted(pheno.values())[n // 2]
with (out / 'groups.tsv').open('w') as f:
    f.write('#IID\ttreatment\tenrolled\n')
    for i, iid in enumerate(ids):
        treatment = r.randrange(2)
        p_enroll = 0.15 + 0.45 * group[i] + 0.15 * (pheno[iid] > med)
        f.write(f'{iid}\t{treatment}\t{int(r.random() < p_enroll)}\n')

print(f'Wrote data/pgi_weights.txt ({len(rows)} rows) and data/groups.tsv ({n} people). All synthetic.')
