#!/usr/bin/env python3

"""OpenBro"""

from logging_setup import configure_logging
logger = configure_logging()

import random
import time
import threading
import os
import json
import shutil
import platform
import importlib.metadata as metadata
import shlex
import re

import click
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from transformers.utils import logging as hf_logging
from peft import PeftModel

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.style import Style
from rich import box
from rich.prompt import Prompt
from rich.markup import escape
from rich.table import Table

import train as train_module

hf_logging.set_verbosity_error()

# ════════════════════════════════════════════════════════════
#  PALETTE
# ════════════════════════════════════════════════════════════
C = {
    "lime":    "#00FF9C",
    "pink":    "#FF2D78",
    "cyan":    "#00D4FF",
    "gold":    "#FFB800",
    "orange":  "#FF6600",
    "muted":   "#4A4A6A",
    "white":   "#E0E0FF",
    "dkpurple":"#1A1A3A",
}

console = Console()

# ════════════════════════════════════════════════════════════
#  ASCII ART & LOGO
# ════════════════════════════════════════════════════════════
LOGO = r"""
 ██████╗ ██████╗ ███████╗███╗   ██╗██████╗ ██████╗  ██████╗ 
██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔═══██╗
██║   ██║██████╔╝█████╗  ██╔██╗ ██║██████╔╝██████╔╝██║   ██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██╔══██╗██╔══██╗██║   ██║
╚██████╔╝██║     ███████╗██║ ╚████║██████╔╝██║  ██║╚██████╔╝
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝ 
"""

TAGLINE = "  ◈  Custom AI  ·  LoRA Fine-Tuning  ·  SFTTrainer  ◈"

GLITCH_POOL = list("!@#$%^&*<>?/|[]{}~`░▒▓█▄▀■□▪")

# ════════════════════════════════════════════════════════════
#  AUTO-GENERATED MESSAGES
# ════════════════════════════════════════════════════════════
BOOT_MSGS = [
    "⚡  Weight tensors crystallized. Standing by.",
    "🧬  LoRA adapters fused. Trainable delta: active.",
    "🌌  Embedding space folded. Dimension: ∞.",
    "🔮  Attention heads aligned. Context window: open.",
    "🦾  PEFT layers injected. Efficiency: 10× baseline.",
    "💀  Gradient tape initialized. Ready to back-prop.",
    "🌊  Loss landscape mapped. Minima: reachable.",
    "🎯  Tokenizer calibrated. Vocab coverage: 99.8%.",
    "✨  Feed-forward layers primed. Activation: GELU.",
    "🚀  Inference engine armed. Launch on your command.",
]

GEN_MSGS = [
    "🧠  Sampling from latent space...",
    "🔥  Temperature adjusted. Creativity: high.",
    "🌊  Decoding token stream...",
    "⚙️   Beam search engaged.",
    "💡  Probability mass concentrated.",
]

TRAIN_MSGS = [
    "📉  Loss descending. Keep going.",
    "🏋️   Weights lifting. Gradients: healthy.",
    "🔄  Backprop loop complete. Delta: applied.",
    "📈  Convergence curve bending. Patience: rewarded.",
]

# ════════════════════════════════════════════════════════════
#  ANIMATIONS
# ════════════════════════════════════════════════════════════
def _glitch(text: str, intensity: float) -> str:
    out = []
    for ch in text:
        if ch not in (" ", "\n") and random.random() < intensity:
            out.append(random.choice(GLITCH_POOL))
        else:
            out.append(ch)
    return "".join(out)


def _neon_gradient(t: float) -> str:
    """Cycle: cyan → lime → pink based on t ∈ [0,1]"""
    if t < 0.33:
        return C["cyan"]
    elif t < 0.66:
        return C["lime"]
    else:
        return C["pink"]


def animate_logo(frames: int = 18):
    """Glitch-dissolve boot animation for the logo."""
    with Live(console=console, refresh_per_second=24, transient=False) as live:
        for i in range(frames):
            progress = i / max(frames - 1, 1)
            glitch_i = max(0.0, (1.0 - progress) * 0.45)
            color = C["orange"]
            logo_text = _glitch(LOGO, glitch_i)
            t = Text(logo_text + "\n" + TAGLINE, style=Style(color=color, bold=True))
            panel = Panel(
                Align.center(t),
                border_style=color,
                box=box.DOUBLE_EDGE,
                padding=(0, 2),
            )
            live.update(panel)
            time.sleep(0.045)


def pulse_spinner(label: str, seconds: float = 1.2):
    """Pulsing dots spinner for short waits."""
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + seconds
    i = 0
    with Live(console=console, refresh_per_second=20, transient=True) as live:
        while time.time() < end:
            live.update(Text(f" {frames[i % len(frames)]}  {label}", style=C["cyan"]))
            i += 1
            time.sleep(0.05)


def typewriter(text: str, style: str = C["white"], delay: float = 0.018):
    """Typewriter effect for single-line text."""
    buf = ""
    with Live(console=console, refresh_per_second=60, transient=False) as live:
        for ch in text:
            buf += ch
            live.update(Text(buf, style=style))
            time.sleep(delay)
    console.print()


def matrix_wipe(label: str = "LOADING", rows: int = 3):
    """Matrix-rain style loading wipe."""
    width = 60
    chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホ"
    with Live(console=console, refresh_per_second=30, transient=True) as live:
        for step in range(30):
            lines = []
            for r in range(rows):
                line = ""
                for c in range(width):
                    reveal_col = (step / 30) * width
                    if c < reveal_col - r * 3:
                        line += " "
                    elif c < reveal_col - r * 3 + 5:
                        line += random.choice(chars)
                    else:
                        line += random.choice(chars)
                lines.append(line)
            body = "\n".join(lines)
            pct = int((step / 30) * 100)
            live.update(Panel(
                Text(body, style=C["lime"]),
                title=f"[bold {C['pink']}]{label}  {pct}%[/bold {C['pink']}]",
                border_style=C["lime"],
                box=box.MINIMAL,
            ))
            time.sleep(0.04)


# ════════════════════════════════════════════════════════════
#  MODEL LOADING
# ════════════════════════════════════════════════════════════
def load_model():
    """Load base model + optional LoRA with a cyberpunk spinner."""
    original_model_name = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
    loaded_event = threading.Event()
    result = {}

    def _load():
        base_model = AutoModelForCausalLM.from_pretrained(
            original_model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            device_map="cpu"
        )
        tokenizer = AutoTokenizer.from_pretrained(original_model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        if os.path.exists("./finetuned_tinyllama/adapter_config.json"):
            logger.info("Loading LoRA adapters from './finetuned_tinyllama'...")
            model = PeftModel.from_pretrained(base_model, "./finetuned_tinyllama")
        else:
            logger.warning("No LoRA adapters found. Using base model.")
            model = base_model

        model = model.eval()
        result["model"] = model
        result["tokenizer"] = tokenizer
        loaded_event.set()

    thread = threading.Thread(target=_load)
    thread.start()

    thread.join()
    return result["model"], result["tokenizer"]


# ════════════════════════════════════════════════════════════
#  GENERATION
# ════════════════════════════════════════════════════════════
def generate_stream(model, tokenizer, prompt_text, max_new_tokens=10000, temperature=0.9, top_p=0.5):
    """Yield tokens from the model using a background thread."""
    inputs = tokenizer([prompt_text], return_tensors="pt").to("cpu")
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    generation_kwargs = dict(
        inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        use_cache=True,
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        repetition_penalty=1.15,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )

    thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    for new_text in streamer:
        yield new_text

    thread.join()


# ════════════════════════════════════════════════════════════
#  SLASH COMMAND PARSING
# ════════════════════════════════════════════════════════════
def _parse_slash_args(text: str):
    """Parse slash command text into (command, args_dict, remaining_text).
    
    Supports:
        /generate hello world
        /generate "hello world" --max-tokens 200 -t 0.8
        /status
        /doctor
        /clean
    """
    try:
        parts = shlex.split(text)
    except ValueError:
        # Fallback for unclosed quotes
        parts = text.split()

    if not parts:
        return None, {}, ""

    cmd = parts[0].lower()
    args = {}
    positional = []
    i = 1
    while i < len(parts):
        part = parts[i]
        if part.startswith("--"):
            key = part[2:].replace("-", "_")
            if i + 1 < len(parts) and not parts[i + 1].startswith("-"):
                args[key] = parts[i + 1]
                i += 2
            else:
                args[key] = True
                i += 1
        elif part.startswith("-") and len(part) == 2:
            # Short flags: -m 200, -t 0.8
            key = {
                "m": "max_tokens",
                "t": "temperature",
                "p": "top_p",
                "o": "output_file",
            }.get(part[1], part[1])
            if i + 1 < len(parts) and not parts[i + 1].startswith("-"):
                args[key] = parts[i + 1]
                i += 2
            else:
                args[key] = True
                i += 1
        else:
            positional.append(part)
            i += 1

    remaining = " ".join(positional)
    return cmd, args, remaining


def _show_status():
    """Show project status."""
    adapter_path = "./finetuned_tinyllama/adapter_config.json"
    has_adapters = os.path.exists(adapter_path)

    checkpoint_dirs = []
    if os.path.isdir("./tinyllama"):
        checkpoint_dirs = [d for d in os.listdir("./tinyllama") if d.startswith("checkpoint-")]
    checkpoint_count = len(checkpoint_dirs)

    data_path = "data/sample.jsonl"
    dataset_size = 0
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            dataset_size = sum(1 for line in f if line.strip())

    lora_info = {}
    if has_adapters:
        with open(adapter_path, "r", encoding="utf-8") as f:
            lora_info = json.load(f)

    table = Table(title="OpenBro Status", border_style=C["cyan"], box=box.DOUBLE_EDGE)
    table.add_column("Component", style=C["pink"], no_wrap=True)
    table.add_column("Status", style=C["lime"])

    table.add_row("LoRA Adapters", "✅ Present" if has_adapters else "❌ Not found")
    table.add_row("Checkpoints", str(checkpoint_count))
    table.add_row("Dataset Size", f"{dataset_size} examples")

    if lora_info:
        table.add_row("LoRA Rank", str(lora_info.get("r", "N/A")))
        table.add_row("LoRA Alpha", str(lora_info.get("lora_alpha", "N/A")))
        table.add_row("Target Modules", ", ".join(lora_info.get("target_modules", [])))

    console.print(table)


def _show_doctor():
    """Diagnose environment."""
    table = Table(title="OpenBro Doctor", border_style=C["gold"], box=box.DOUBLE_EDGE)
    table.add_column("Check", style=C["pink"], no_wrap=True)
    table.add_column("Result", style=C["lime"])

    table.add_row("Python Version", platform.python_version())

    pkgs = ["torch", "transformers", "peft", "accelerate", "rich", "click"]
    for pkg in pkgs:
        try:
            ver = metadata.version(pkg)
            table.add_row(pkg, f"{ver} ✅")
        except metadata.PackageNotFoundError:
            table.add_row(pkg, "Not installed ❌")

    try:
        cuda_available = torch.cuda.is_available()
        table.add_row("CUDA Available", "Yes ✅" if cuda_available else "No (CPU only)")
        if cuda_available:
            table.add_row("CUDA Version", torch.version.cuda or "Unknown")
            table.add_row("GPU", torch.cuda.get_device_name(0))
    except Exception as e:
        table.add_row("CUDA Check", f"Error: {e}")

    data_exists = os.path.exists("data/sample.jsonl")
    table.add_row("Dataset", "Found ✅" if data_exists else "Missing ❌")

    total, used, free = shutil.disk_usage(".")
    free_gb = free / (1024 ** 3)
    table.add_row("Disk Free", f"{free_gb:.2f} GB")

    try:
        import psutil
        mem = psutil.virtual_memory()
        table.add_row("RAM", f"{mem.total / (1024 ** 3):.1f} GB total, {mem.available / (1024 ** 3):.1f} GB available")
    except ImportError:
        table.add_row("RAM", "psutil not installed (optional)")

    console.print(table)


def _run_clean():
    """Remove checkpoints with confirmation."""
    checkpoint_dir = "./tinyllama"
    if not os.path.isdir(checkpoint_dir):
        console.print(Panel("No checkpoint directory found.", border_style=C["pink"], box=box.ROUNDED))
        return

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(checkpoint_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    freed_mb = total_size / (1024 * 1024)
    try:
        confirm = Prompt.ask(
            f"[bold {C['orange']}]Delete all checkpoints in {checkpoint_dir}? (~{freed_mb:.1f} MB will be freed) [y/N][/bold {C['orange']}]"
        )
    except (KeyboardInterrupt, EOFError):
        console.print(f"[{C['pink']}]Cancelled.[/]")
        return

    if confirm.strip().lower() in ("y", "yes"):
        shutil.rmtree(checkpoint_dir)
        console.print(Panel(
            f"[bold]Cleaned up {checkpoint_dir}[/bold]\nFreed ~{freed_mb:.1f} MB of disk space.",
            border_style=C["gold"],
            box=box.DOUBLE_EDGE,
        ))
    else:
        console.print(f"[{C['muted']}]Cleanup cancelled.[/]")


def _run_generate_slash(model, tokenizer, args: dict, prompt_text: str):
    """Handle /generate with parsed args."""
    if not prompt_text.strip():
        console.print(Panel("Usage: /generate <prompt> [--max-tokens 200] [-t 0.9] [--top-p 0.5]", border_style=C["pink"], box=box.ROUNDED))
        return

    max_tokens = int(args.get("max_tokens", args.get("max_tokens", 200)))
    temperature = float(args.get("temperature", 0.9))
    top_p = float(args.get("top_p", 0.5))
    output_file = args.get("output_file", None)

    formatted_prompt = (
        f"### Instruction:\nAnswer the user's input concisely.\n\n"
        f"### Input:\n{prompt_text}\n\n"
        f"### Response:\n"
    )

    response_text = ""
    with Live(console=console, refresh_per_second=20, transient=False) as live:
        for token in generate_stream(model, tokenizer, formatted_prompt, max_new_tokens=max_tokens, temperature=temperature, top_p=top_p):
            response_text += token
            panel = Panel(
                Text(response_text, style=C["lime"]),
                title=f"[bold {C['pink']}]Assistant[/bold {C['pink']}]",
                border_style=C["lime"],
                box=box.ROUNDED,
            )
            live.update(panel)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response_text)
        console.print(f"[{C['gold']}]Output saved to {output_file}[/{C['gold']}]")


# ════════════════════════════════════════════════════════════
#  CLI
# ════════════════════════════════════════════════════════════
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """OpenModel — Cyberpunk LLM CLI"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(chat)


@cli.command()
def chat():
    """Interactive chat with the model."""
    animate_logo(frames=18)
    console.print()

    model, tokenizer = load_model()
    console.print(Panel(
        "[bold]Model online.[/bold]\n"
        "Slash commands: /quit, /clear, /train, /status, /doctor, /clean, /generate <prompt> [opts]",
        border_style=C["gold"],
        box=box.ROUNDED,
    ))
    console.print()

    while True:
        try:
            user_input = Prompt.ask(f"[bold {C['cyan']}]You[/bold {C['cyan']}]")
        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[{C['pink']}]Exiting...[/]")
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        # Slash command handling
        if user_input.startswith("/"):
            cmd, args, remaining = _parse_slash_args(user_input)

            if cmd == "/quit":
                console.print(f"[{C['pink']}]Shutting down...[/]")
                break
            elif cmd == "/clear":
                console.clear()
                continue
            elif cmd == "/train":
                console.print(f"[{C['gold']}]Switching to training mode...[/]")
                run_training_cmd()
                continue
            elif cmd == "/status":
                _show_status()
                continue
            elif cmd == "/doctor":
                _show_doctor()
                continue
            elif cmd == "/clean":
                _run_clean()
                continue
            elif cmd == "/generate":
                _run_generate_slash(model, tokenizer, args, remaining)
                continue
            else:
                console.print(Panel(
                    f"Unknown command: {cmd}\n"
                    "Available: /quit, /clear, /train, /status, /doctor, /clean, /generate",
                    border_style=C["pink"],
                    box=box.ROUNDED,
                ))
                continue

        # Show user message
        console.print(Panel(
            escape(user_input),
            title=f"[bold {C['cyan']}]User[/bold {C['cyan']}]",
            border_style=C["cyan"],
            box=box.ROUNDED,
        ))

        # Alpaca prompt
        formatted_prompt = (
            f"### Instruction:\nAnswer the user's input concisely.\n\n"
            f"### Input:\n{user_input}\n\n"
            f"### Response:\n"
        )

        # Stream response
        response_text = ""
        with Live(console=console, refresh_per_second=20, transient=False) as live:
            for token in generate_stream(model, tokenizer, formatted_prompt):
                response_text += token
                panel = Panel(
                    Text(response_text, style=C["lime"]),
                    title=f"[bold {C['pink']}]Assistant[/bold {C['pink']}]",
                    border_style=C["lime"],
                    box=box.ROUNDED,
                )
                live.update(panel)

        console.print()


def run_training_cmd():
    """Wrapper to launch training with Rich UI flourishes."""
    animate_logo(frames=12)
    console.print()
    
    train_module.run_training()

    console.print(Panel(
        "[bold]Training complete. Adapters saved to ./finetuned_tinyllama[/bold]",
        border_style=C["gold"],
        box=box.DOUBLE_EDGE,
    ))


@cli.command()
def train():
    """Fine-tune the model."""
    run_training_cmd()


@cli.command()
def status():
    """Show project status: adapters, checkpoints, dataset size."""
    animate_logo(frames=12)
    console.print()
    _show_status()


@cli.command()
def doctor():
    """Diagnose environment: packages, CUDA, disk space, data files."""
    animate_logo(frames=12)
    console.print()
    _show_doctor()


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to delete all checkpoints in ./tinyllama/?")
def clean():
    """Remove training checkpoints to reclaim disk space."""
    checkpoint_dir = "./tinyllama"
    if not os.path.isdir(checkpoint_dir):
        console.print(Panel("No checkpoint directory found.", border_style=C["pink"], box=box.ROUNDED))
        return

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(checkpoint_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    shutil.rmtree(checkpoint_dir)
    freed_mb = total_size / (1024 * 1024)
    console.print(Panel(
        f"[bold]Cleaned up {checkpoint_dir}[/bold]\nFreed ~{freed_mb:.1f} MB of disk space.",
        border_style=C["gold"],
        box=box.DOUBLE_EDGE,
    ))


@cli.command()
@click.option("--prompt", "-p", required=True, help="Text prompt for generation.")
@click.option("--max-tokens", "-m", default=200, show_default=True, help="Maximum new tokens.")
@click.option("--temperature", "-t", default=0.9, show_default=True, help="Sampling temperature.")
@click.option("--top-p", default=0.5, show_default=True, help="Nucleus sampling threshold.")
@click.option("--output-file", "-o", type=click.Path(), help="File to save the generated text.")
def generate(prompt, max_tokens, temperature, top_p, output_file):
    """One-shot text generation from a prompt."""
    matrix_wipe(label="LOADING MODEL", rows=2)
    model, tokenizer = load_model()

    formatted_prompt = (
        f"### Instruction:\nAnswer the user's input concisely.\n\n"
        f"### Input:\n{prompt}\n\n"
        f"### Response:\n"
    )

    response_text = ""
    with console.status("[bold cyan]Generating...[/bold cyan]", spinner="dots"):
        for token in generate_stream(model, tokenizer, formatted_prompt, max_new_tokens=max_tokens, temperature=temperature, top_p=top_p):
            response_text += token

    console.print(Panel(
        Text(response_text, style=C["lime"]),
        title=f"[bold {C['pink']}]Generated Output[/bold {C['pink']}]",
        border_style=C["lime"],
        box=box.ROUNDED,
    ))

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response_text)
        console.print(f"[{C['gold']}]Output saved to {output_file}[/{C['gold']}]")


if __name__ == "__main__":
    cli()

