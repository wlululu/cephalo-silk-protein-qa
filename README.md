# Cephalo-Silk: Protein Image–Property Question Answering

Code, benchmark results, datasets and model references accompanying the manuscript *Cephalo-Silk: Protein Image-Property Analysis through General-to-Spider Vision–Language Adaptation* (Wei Lu and Markus J. Buehler).

The study includes **2,177 spider-silk proteins** and **7,024 general proteins**, with **seven categorical image–property QA tasks per protein**. This repository provides the reference benchmark scripts, held-out prediction records and scoring results. Protein-image QA datasets and LoRA adapters are distributed through the linked Hugging Face repositories.

## Reproduce the benchmark scores

Use Python 3.10+ with `numpy` and `pandas` (a Python 3.12 virtual environment is recommended):

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/score_benchmark.py --input-dir data/evaluations --out results/reproduced
```

For an existing uv-managed `.venv`, substitute `.venv/bin/python` for `python`.

| Adaptation profile | Held-out proteins | QA records | Base Cephalo zero-shot | Fine-tuned | Difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| Spider-silk only | 217 | 1,519 | 41.80% | 93.09% | +51.28 pp |
| General-protein only | 702 | 4,914 | 30.63% | 87.36% | +56.74 pp |
| General → spider-silk | 217 | 1,519 | 41.21% | 94.47% | +53.26 pp |

The zero-shot and fine-tuned results are paired **within each adaptation profile**. The spider-only and staged profiles have distinct held-out protein sets; they should not be treated as a paired comparison of training strategies. Results use strict whole-response categorical labels, so measured improvements can include response-format effects. See [methodology and interpretation](docs/REPRODUCIBILITY.md).

## Contents

- [`scripts/score_benchmark.py`](scripts/score_benchmark.py): matched six-run scoring, per-task evaluation, paired protein-level bootstrap intervals and integrity checks.
- [`scripts/strict_labels.py`](scripts/strict_labels.py): categorical response normalization.
- [`data/evaluations/`](data/evaluations/): saved zero-shot and fine-tuned predictions with protein IDs, questions and gold labels.
- [`data/splits/`](data/splits/): held-out test protein identifiers for the three reported profiles.
- [`results/`](results/): benchmark tables and paired-bootstrap summaries.
- [`tests/`](tests/): benchmark regression and utility tests.
- [`scripts/build_qa_from_properties.py`](scripts/build_qa_from_properties.py): reference label-construction helper from precomputed DSSP and ProtParam descriptors.
- [`scripts/render_pdb_isometric.py`](scripts/render_pdb_isometric.py): example protein-structure rendering helper using VMD.
- [`models/adapter_manifest.json`](models/adapter_manifest.json): original LoRA checkpoint metadata and weights checksums.
- [`docs/`](docs/): details on benchmark reproducibility, model dependencies and publication release checks.

## Datasets and models

| Resource | Repository |
| --- | --- |
| Spider-silk protein image–QA dataset | [spidrion_image_QA.hf](https://huggingface.co/datasets/wlululu/spidrion_image_QA.hf) |
| General-protein image–QA dataset | [forcegen_image_QA.hf](https://huggingface.co/datasets/wlululu/forcegen_image_QA.hf) |
| Spider-only LoRA | [cephalo-silk-spider-lora](https://huggingface.co/wlululu/cephalo-silk-spider-lora) |
| General-only LoRA | [cephalo-silk-general-lora](https://huggingface.co/wlululu/cephalo-silk-general-lora) |
| General → spider-silk LoRA | [cephalo-silk-staged-lora](https://huggingface.co/wlululu/cephalo-silk-staged-lora) |
| Foundation VLM | [Cephalo-Llama-3.2-11B-Vision-Instruct-128k](https://huggingface.co/lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k) |
| Merged general-protein base for staged LoRA | [Cephalo general-merged Epoch4](https://huggingface.co/wlululu/Cephalo_protein_predict_all_losstrack50_splitbyProtein_general-merged_Epoch4) |

**Model dependency:** The staged adapter was trained on the **merged general-protein-adapted checkpoint**, rather than directly on the unadapted Cephalo model. Its `adapter_config.json` should not be redirected to the original foundation model. See [model details](docs/MODEL_RELEASE.md).

## Scientific interpretation

The benchmark assesses short categorical responses to protein renderings. Secondary-structure labels are derived from structural annotation, whereas physicochemical labels are derived from sequence-level ProtParam descriptors. Classification accuracy should not be interpreted as experimental validation of structural or materials properties. The saved-prediction scoring workflow is distinct from repeating GPU inference or model training; see [reproducibility](docs/REPRODUCIBILITY.md).

## Citation

Please cite the accompanying manuscript using the provisional [citation template](CITATION.cff). Its final journal, DOI and publication metadata will be added after acceptance/publication.
