# Benchmark result tables

These CSVs summarize the **six saved historical prediction sets** in `../data/evaluations/`. They are not the output of a new model-inference run.

From the repository root, run:

```bash
python scripts/score_benchmark.py --input-dir data/evaluations --out results/reproduced
```

The regenerated summaries will be written under `results/reproduced/` (ignored by Git). `six_run_summary.csv` and `six_run_per_task.csv` report accuracies and format compliance; `matched_comparison.csv` records within-profile differences; `paired_bootstrap_effects.csv` records protein-resampled 95% intervals (10,000 replicates; seed 20261021); `integrity_checks.csv` records matching checks.

The historical reference tables may use a different column layout from newly regenerated tables, but their numerical conclusions should agree. See [`../docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md) for scope and limitations.
