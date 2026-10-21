# Cephalo-Silk: Protein Image–Property Question Answering

Research code, held-out predictions and benchmark records accompanying the working manuscript *Cephalo-Silk: Protein Image-Property Analysis through General-to-Spider Vision–Language Adaptation* (W. Lu and M. J. Buehler).

The study uses **2,177 spider-silk proteins** and **7,024 general proteins**, with **seven categorical QA tasks per protein**. This repository provides a lightweight, CPU-reproducible evaluation of saved predictions; it is **not** a complete release of the training datasets, model-inference pipeline or historical training environment.

## Reproduce the reported benchmark

Requires Python 3.10+ (Python 3.11 recommended). From the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/score_benchmark.py --input-dir data/evaluations --out results/reproduced
```

Expected strict-label accuracy:

| Adaptation profile | Held-out proteins | QA records | Original Cephalo zero-shot | Fine-tuned | Observed difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| Spider-silk only | 217 | 1,519 | 41.80% | 93.09% | +51.28 percentage points |
| General-protein only | 702 | 4,914 | 30.63% | 87.36% | +56.74 percentage points |
| General → spider-silk | 217 | 1,519 | 41.21% | 94.47% | +53.26 percentage points |

Each zero-shot/fine-tuned comparison uses the **same protein–question records within its profile**. Spider-only and staged rows use **different held-out sets** and must not be treated as a paired comparison of training strategies. Strict scoring recognizes only complete categorical labels (case and trailing punctuation normalized), so much of the observed improvement may reflect **response-format compliance** rather than demonstrated image-grounded scientific reasoning. See [reproducibility details](docs/REPRODUCIBILITY.md).

## What the repository contains

- [`scripts/strict_labels.py`](scripts/strict_labels.py): task-specific categorical normalization.
- [`scripts/score_benchmark.py`](scripts/score_benchmark.py): matched six-run evaluation, per-question summaries and paired bootstrap CIs resampled at the protein level.
- [`data/evaluations/`](data/evaluations/): **six** historical prediction CSVs, reduced to protein ID, question, reference label and raw prediction; protein sequences removed.
- [`data/splits/`](data/splits/): three historical **test-set** protein-ID manifests (not full train/test split provenance).
- [`results/`](results/): reported aggregate results and bootstrap summaries; generated outputs can be recreated via the command above.
- [`models/adapter_manifest.json`](models/adapter_manifest.json): source checkpoints, SHA-256 hashes and Hugging Face model IDs. Model weights are **not** stored in this Git repository.
- [`scripts/build_qa_from_properties.py`](scripts/build_qa_from_properties.py) and [`scripts/render_pdb_isometric.py`](scripts/render_pdb_isometric.py): independently curated reference helpers, **not** verified end-to-end reconstructions of the historical dataset or images.
- [`docs/`](docs/): experimental provenance, reported training settings, model dependencies and release requirements.

## Data and model repositories

| Resource | Location | Status as of 2026-10-21 |
| --- | --- | --- |
| Spider-silk image–QA dataset | [Hugging Face dataset](https://huggingface.co/datasets/wlululu/spidrion_image_QA.hf) | Private; dataset-level integrity and redistribution review outstanding |
| General-protein image–QA dataset | [Hugging Face dataset](https://huggingface.co/datasets/wlululu/forcegen_image_QA.hf) | Private; dataset-level integrity and redistribution review outstanding |
| Spider-only LoRA | [Hugging Face model](https://huggingface.co/wlululu/cephalo-silk-spider-lora) | Private; independent loading test outstanding |
| General-only LoRA | [Hugging Face model](https://huggingface.co/wlululu/cephalo-silk-general-lora) | Private; independent loading test outstanding |
| General → spider LoRA | [Hugging Face model](https://huggingface.co/wlululu/cephalo-silk-staged-lora) | Private; independent loading test outstanding |
| Base Cephalo model | [lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k](https://huggingface.co/lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k) | Public |
| General-only **merged** base for the staged adapter | [Hugging Face model](https://huggingface.co/wlululu/Cephalo_protein_predict_all_losstrack50_splitbyProtein_general-merged_Epoch4) | Private |

**Important:** The staged LoRA's `adapter_config.json` identifies the **general-only merged model**, *not the original Cephalo checkpoint*, as its base. See [model release and dependencies](docs/MODEL_RELEASE.md). Links to Private Hugging Face resources are accessible only to authorized accounts.

## Scientific boundaries and release status

The two HF datasets' exact published snapshots, source permissions and matching to the manuscript's curated counts have **not** yet been independently audited. The current code reproduces **scores from saved predictions**, not live inference or model training. Protein-sequence overlap, image-ablated evaluation and deterministic training reconstruction remain future validation items.

This repository may be temporarily **public for review**; public visibility does **not** imply an open-source license or permission to reuse upstream data. The software/data license is pending author approval. Please see [`LICENSE_NOT_SET.md`](LICENSE_NOT_SET.md) and the [release checklist](docs/RELEASE_CHECKLIST.md). Do not upload private credentials, upstream model weights or historical notebooks that contain embedded tokens.

## Citation

See [`CITATION.cff`](CITATION.cff) for the reproducibility package citation. The associated manuscript is a working draft; no publication DOI is claimed here.
