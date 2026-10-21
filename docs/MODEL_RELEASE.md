# PEFT LoRA adapters and their base-model dependencies

Three **private** Hugging Face model repositories have been created for the archived adapters. Their historical `adapter_model.safetensors` and `adapter_config.json` are independent of the evaluation CSVs; the model weights are not stored in this Git repository.

| Profile | Historical checkpoint | Hugging Face adapter | Base checkpoint in original PEFT config |
| --- | --- | --- | --- |
| Spider-silk only | `checkpoint-13720` | [cephalo-silk-spider-lora](https://huggingface.co/wlululu/cephalo-silk-spider-lora) | [original Cephalo](https://huggingface.co/lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k) |
| General-protein only | `checkpoint-44252` | [cephalo-silk-general-lora](https://huggingface.co/wlululu/cephalo-silk-general-lora) | [original Cephalo](https://huggingface.co/lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k) |
| General → spider-silk | `checkpoint-13720` (TwoStep) | [cephalo-silk-staged-lora](https://huggingface.co/wlululu/cephalo-silk-staged-lora) | [general-only **merged** model](https://huggingface.co/wlululu/Cephalo_protein_predict_all_losstrack50_splitbyProtein_general-merged_Epoch4) |

**Do not mount the staged LoRA directly on the unadapted Cephalo checkpoint.** Its original adapter configuration points to a checkpoint in which general-protein fine-tuning was already merged into the model. The staged path requires access to that merged model **or a separately validated reconstruction** through an equivalent merge procedure. These alternatives have not been shown to give identical predictions here.

Each standalone LoRA release should have:

- `adapter_model.safetensors`
- `adapter_config.json` (unchanged original PEFT base-model dependency)
- `README.md` / Hugging Face Model Card with task, provenance, limitations and upstream model identifiers

The source checkpoint sizes and SHA-256 values are recorded in [`../models/adapter_manifest.json`](../models/adapter_manifest.json). Those hashes describe the **historical source archives**; the Hub-uploaded weights have not been independently compared by SHA-256 in this repository. Likewise, HF repository creation and Model Card metadata **do not prove** successful GPU loading or faithful live inference. Model releases and downstream licensing/redistribution remain subject to review.

The six sets of benchmark results in `data/evaluations/` are **saved historical outputs**, not fresh predictions made from newly uploaded Hub adapters. A definitive model release should independently load all three adapters, check image preprocessing and decoding, compare records to the frozen evaluation set, and pin checkpoint revisions.
