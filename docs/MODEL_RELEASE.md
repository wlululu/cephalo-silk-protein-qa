# LoRA model repositories and lineage

Three PEFT LoRA adapters are maintained on Hugging Face. Their original source checkpoint paths and SHA-256 values are documented in [`models/adapter_manifest.json`](../models/adapter_manifest.json); weight files are hosted with the HF model repositories rather than duplicated in GitHub.

| Adaptation profile | Source checkpoint | LoRA adapter | Required base model |
| --- | --- | --- | --- |
| Spider-silk only | `checkpoint-13720` | [Spider LoRA](https://huggingface.co/wlululu/cephalo-silk-spider-lora) | [Original Cephalo](https://huggingface.co/lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k) |
| General-protein only | `checkpoint-44252` | [General LoRA](https://huggingface.co/wlululu/cephalo-silk-general-lora) | [Original Cephalo](https://huggingface.co/lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k) |
| General → spider-silk | `checkpoint-13720` (TwoStep) | [Staged LoRA](https://huggingface.co/wlululu/cephalo-silk-staged-lora) | [General-only merged checkpoint](https://huggingface.co/wlululu/Cephalo_protein_predict_all_losstrack50_splitbyProtein_general-merged_Epoch4) |

Each HF adapter includes the PEFT adapter weights and configuration and an accompanying model card. **Do not load the staged LoRA directly onto the unadapted Cephalo foundation checkpoint:** its original `adapter_config.json` refers to the general-protein-adapted merged model.

The repository's benchmark results were computed from saved historical predictions. Repeating live model inference additionally requires compatible inference libraries, model-loading code, image preprocessing, prompts and generation configuration. Model loading and evaluation should be validated independently of the offline scoring scripts.
