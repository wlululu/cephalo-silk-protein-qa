# Cephalo-Silk: Protein Image-Property QA

**Research reproducibility repository — private review draft.**

This repository accompanies *Cephalo-Silk: Protein Image-Property Analysis
through General-to-Spider Vision–Language Adaptation* (W. Lu and M. J. Buehler,
working draft). It covers **2,177 spider-silk proteins** and **7,024 general
proteins**, with seven categorical protein image–property QA tasks per protein.

## Scope and status

- **Reproducible here, CPU only:** recompute strict short-label scores for
  three matched zero-shot/fine-tuned experiment profiles, their per-question
  accuracies and protein-level paired bootstrap intervals.
- **Included:** saved reference labels/predictions for the three held-out profiles,
  distinct held-out ID manifests, summary statistics, scoring code and tests.
- **Not included:** raw training images, protein sequences, PDB files, complete
  model weights or full historical training environment. Raw notebook files are
  intentionally excluded because they contain workstation paths, embedded outputs
  and/or credentials.
- The two upstream image QA datasets are **private** at present. Do not claim
  full independent model training or inference reproduction from this repository.

## Reproduce the benchmark

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/score_benchmark.py \
    --input-dir data/evaluations \
    --out results/reproduced
```

Expected strict accuracy (zero-shot → fine-tuned):

| Profile | Held-out QA | Zero-shot | Fine-tuned | Gain |
|---|---:|---:|---:|---:|
| Spider-silk only | 1,519 | 41.80% | 93.09% | +51.28 pp |
| General-protein only | 4,914 | 30.63% | 87.36% | +56.74 pp |
| General-to-spider | 1,519 | 41.21% | 94.47% | +53.26 pp |

Each within-row comparison evaluates identical protein–question records.
Spider-only and staged rows retain distinct held-out spider-silk partitions;
they are **not paired with each other**. Strict scoring accepts *only a complete
categorical short answer* with case/terminal punctuation normalization. Large
gains partly reflect output-format compliance; they do not establish
corresponding semantic knowledge gains or image-input dependence.

## Files

- `scripts/strict_labels.py` — canonical categorical normalization.
- `scripts/score_benchmark.py` — six-run matched benchmark with paired bootstrap.
- `scripts/build_qa_from_properties.py` — **reference-definition helper** from
  existing annotations; not claimed to regenerate the original archived dataset.
- `scripts/render_pdb_isometric.py` — VMD batch image helper following the
  documented NewCartoon/isometric settings; not a pixel-wise reproduction proof.
- `data/evaluations/` — six sanitized CSVs with ID, question, gold, prediction
  (original protein sequences removed).
- `data/splits/` — three exact held-out protein-ID manifests extracted from
  historical evaluations; these do not contain the training protein list.
- `results/` — tabulated publication numbers and paired-bootstrap results.
- `models/adapter_manifest.json` — SHA-256 and base-checkpoint dependencies;
  **adapter weights are not stored in Git**.
- `docs/REPRODUCIBILITY.md` — provenance and known limitations.

## Data and model links

- Spider-silk QA: https://huggingface.co/datasets/wlululu/spidrion_image_QA.hf (**private**)
- General-protein QA: https://huggingface.co/datasets/wlululu/forcegen_image_QA.hf (**private**)
- Base VLM: https://huggingface.co/lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k
- General-only merged model used *underneath the staged adapter*:
  https://huggingface.co/wlululu/Cephalo_protein_predict_all_losstrack50_splitbyProtein_general-merged_Epoch4 (**private**)

**Do not** load the staged adapter directly on the original Cephalo model:
its original `adapter_config.json` identifies the merged general-protein model
as its base. See `docs/MODEL_RELEASE.md`.

## Availability, licensing and release

This repository is an internal review artifact pending public-release permission
for datasets and any model adapters. See `LICENSE_NOT_SET.md` and
`docs/RELEASE_CHECKLIST.md`. No inference metrics are claimed beyond the saved
historical predictions.
