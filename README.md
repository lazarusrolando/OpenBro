# OpenBro

> A cyberpunk-styled CLI for training and chatting with fine-tuned LLMs using LoRA (Low-Rank Adaptation).

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Overview

**OpenBro** is a lightweight, CLI framework for:

- **Fine-tuning** language models (TinyLlama) with LoRA adapters via `transformers` and `peft`
- **Chatting** interactively with your fine-tuned model through a slick, animated CLI

Built for CPU-friendly environments, it features a neon-soaked Rich UI with glitch animations, matrix loading screens, and streaming token generation.

---

## Features

- **LoRA Fine-Tuning** — Efficient adapter training on consumer hardware
- **Rich Cyberpunk CLI** — Glitch logos, neon gradients, live spinners, and token streaming
- **Interactive Chat** — Conversational interface with `/quit`, `/clear`, and `/train` shortcuts
- **Alpaca Format** — Standard instruction-following prompt format
- **CPU Optimized** — Runs on CPU with `low_cpu_mem_usage` and fp32 weights
- **Modular Design** — Separate training and inference scripts with shared logging

---

## Project Structure

```
OpenBro/
├── openbro.py          # Main CLI entry point (chat & train commands)
├── train.py              # LoRA fine-tuning script
├── logging_setup.py      # Centralized logging and warning suppression
├── setup.py              # Package installation config
├── openbro.bat         # Windows batch launcher
├── requirements-cpu.txt  # Python dependencies
├── data/
│   └── sample.jsonl      # Training dataset (Alpaca format)
├── tinyllama/            # Training checkpoints
├── finetuned_tinyllama/  # Saved LoRA adapters
└── README.md             # This file
```

---

## Installation

### 1. Clone or navigate to the project

```bash
git clone https://github.com/lazarusrolando/OpenBro.git
cd OpenBro
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements-cpu.txt
```

Or install as a package:

```bash
pip install -e .
```

### 4. Alternative: Install via curl | bash (Quick Install)

You can also install OpenBro globally with a single command:

**For Unix/Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/lazarusrolando/OpenBro/main/install.sh | bash
```

**For Windows PowerShell:**
```powershell
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/lazarusrolando/OpenBro/main/install.ps1'))
```

**For Windows Command Prompt:**
```cmd
powershell -Command "Invoke-WebRequest -Uri https://raw.githubusercontent.com/lazarusrolando/OpenBro/main/install.bat -UseBasicParsing | Invoke-Expression"
```

---

## Usage

### Launch the CLI

```bash
python openbro.py
```

## Or type openbro:

```bash
openbro
```

### Commands

#### `chat` (default)

Start an interactive chat session with the model.

```bash
python openbro.py chat
```

**Chat Shortcuts:**

| Command  | Action                          |
|----------|---------------------------------|
| `/quit`  | Exit the session                |
| `/clear` | Clear the terminal screen       |
| `/train` | Switch to training mode         |

#### `train`

Fine-tune the base model on your dataset.

```bash
python openbro.py train
```

Training outputs:
- Checkpoints saved to `./tinyllama/`
- LoRA adapters saved to `./finetuned_tinyllama/`

---

## Data Format

Training data should be a `.jsonl` file with Alpaca-style examples:

```json
{"instruction": "Translate English to French", "input": "Good morning!", "output": "Bonjour!"}
{"instruction": "Summarize the following sentence", "input": "Deep learning enables...", "output": "Deep learning lets computers learn patterns from data."}
```

Place your dataset at:

```
data/sample.jsonl
```

---

## Training Configuration

Default hyperparameters in `train.py`:

| Parameter                 | Value                               |
|---------------------------|-------------------------------------|
| Base Model                | TinyLlama/TinyLlama-1.1B-Chat-v1.0  |
| LoRA Rank (`r`)           | 8                                   |
| LoRA Alpha                | 16                                  |
| Target Modules            | q_proj, k_proj, v_proj, o_proj      |
| LoRA Dropout              | 0.05                                |
| Batch Size                | 1                                   |
| Gradient Accumulation     | 4                                   |
| Learning Rate             | 2e-4                                |
| Epochs                    | 3                                   |
| Optimizer                 | adamw_torch                         |
| LR Scheduler              | cosine                              |

Modify these directly in `train.py` to suit your needs.

---

## Inference Settings

Generation defaults in `openbro.py`:

| Parameter           | Value  |
|---------------------|--------|
| Max New Tokens      | 2000   |
| Temperature         | 0.9    |
| Top-p               | 0.5    |
| Repetition Penalty  | 1.15   |
| Device              | CPU    |

---

## Troubleshooting

### `torch` version warnings

If you see warnings about incompatible torch versions on import, they are automatically suppressed by `logging_setup.py`. Ensure you call `configure_logging()` before importing `torch`.

### `pin_memory` warning during training

Already fixed by setting `dataloader_pin_memory=False` in `TrainingArguments`.

### No LoRA adapters found

If adapters haven't been trained yet, the CLI falls back to the base model. Run `python openbro.py train` first.

### Model loading is slow

TinyLlama is ~1.1B parameters. On CPU, expect 30–90 seconds for initial load. The spinner animation will keep you company.

---

## License

MIT License — see `LICENSE` for details.

---

## Author

**Lazarus Rolando**

