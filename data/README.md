# Benchmark input records

The six files in `evaluations/` record the reference label and raw saved model prediction for each held-out protein/question pair. They contain protein identifiers, question text, ground-truth categories and model responses; protein sequence fields were excluded from this compact benchmark export.

The three files in `splits/` preserve the historical held-out **test** protein identifiers for spider-only, general-only and General → Spider evaluation profiles. Spider-only and staged profiles use different held-out sets.

The full protein image–QA datasets are linked in the root [README](../README.md). The scoring command reads the local prediction CSVs and does not require GPU access.
