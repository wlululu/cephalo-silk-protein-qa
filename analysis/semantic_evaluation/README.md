# Semantic-label evaluation of archived protein QA predictions

Evaluation performed 2026-10-30 on original data from repository commit
`ef4f2945b8673d98b77f8fbfca862175b0c87a3d`.

This is a **supplementary, ground-truth-blind semantic scoring analysis** of
all six original saved zero-shot and fine-tuned prediction sets. It does not
replace historical strict-label scores, change training/test splits, or run
model inference. Input predictions and split manifests remain in the root
repository `data/evaluations/` and `data/splits/` (not duplicated here).

## Findings

| Profile | Zero-shot strict | Zero-shot semantic | Fine-tuned semantic | Full-sample gain | Matched-answer gain (95% CI) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Spider-only | 41.80% | 62.80% | 93.09% | 30.28 pp | 11.53 pp (9.20, 13.78) |
| General-only | 30.63% | 54.56% | 87.36% | 32.80 pp | 18.72 pp (17.30, 20.19) |
| General-to-spider | 41.21% | 65.44% | 94.47% | 29.03 pp | 12.68 pp (10.57, 14.69) |

Full-sample gains include **answer availability**, and matched-answer gains
condition on both models providing an extractable response. Neither establishes
causal dependence on the protein image. Unresolved zero-shot responses count
as incorrect in the primary full-set endpoint. Per-property and class-aware
results (including important minority-class weaknesses) are in `results/`.

## Contents

- `scripts/semantic_labels.py`: task-specific parsing, including negation,
  contradictory statements, and numeric threshold claims.
- `scripts/adjudication_policy.json`: content-hash-keyed blind adjudications.
- `scripts/freeze_extraction.py`: freezes interpretations without gold labels.
- `scripts/analyze.py`: joins frozen predictions to golds, computes metrics,
  protein-level paired bootstrap (10,000 draws), sensitivity results.
- `scripts/validate.py` and `scripts/test_semantics.py`: integrity / rules checks.
- `blind_unique_responses.csv`: deduplicated question-response-only corpus
  used for ground-truth-blind extraction.
- `results/frozen_extraction.csv`, `results/extraction_freeze.json`, and
  `results/blind_adjudications.csv`: extraction audit and provenance.
- `results/six_run_metrics.csv`, `results/per_property_metrics.csv`,
  `results/per_class_metrics.csv`, `results/paired_protein_bootstrap.csv`,
  `results/gain_decomposition.csv`, and `results/sensitivity.csv`: key results.
- `results/source_manifest.json`: original input hashes.

Generated row-level annotations (`results/*_annotated.csv`), PDFs, figures,
and a duplicate of the entire source repository are intentionally **not**
committed. The annotations can be recreated with `analyze.py`.

## Reproduce from the repository root

Requires Python >=3.11; install the separately pinned analysis dependencies:

```bash
python3 -m pip install -r analysis/semantic_evaluation/requirements.txt
python3 analysis/semantic_evaluation/scripts/test_semantics.py
python3 analysis/semantic_evaluation/scripts/freeze_extraction.py
python3 analysis/semantic_evaluation/scripts/analyze.py --source .
python3 analysis/semantic_evaluation/scripts/validate.py
```

`freeze_extraction.py` must run before `analyze.py`; the latter verifies
content hashes in `results/extraction_freeze.json` before joining ground truth.
`analyze.py` regenerates the omitted `results/*_annotated.csv`, and updates
metrics in this analysis directory, without touching root benchmark data.
`validate.py` validates against the six source CSVs in the **repository root**.
If the original CSVs were subsequently edited, the hash check must fail;
use the archived source commit to reproduce the 2026-10-30 snapshot.

For full exact strict-scoring reproduction, run the existing root scorer:

```bash
python3 scripts/score_benchmark.py --input-dir data/evaluations \
  --out analysis/semantic_evaluation/results/strict_reproduction
```

## Scientific cautions

These rules were developed on archived question-response text without using
reference labels to choose predictions, but were not independently validated
by double-blind human annotation. Bootstrap CIs reflect archived protein
sampling, not extraction-rule, training-seed, or sequence-homology uncertainty.
The observed gains are in categorical label agreement, not experimental
protein properties or established image-grounded molecular reasoning.
