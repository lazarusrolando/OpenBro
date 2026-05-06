from .logging_setup import configure_logging

logger = configure_logging()

import os
import json
import torch
from torch.utils.data import Dataset as TorchDataset
from peft import LoraConfig, get_peft_model
from transformers import (
  AutoModelForCausalLM,
  AutoTokenizer,
  TrainingArguments,
  Trainer,
  DataCollatorForLanguageModeling
)


def run_training():
    """Load data, apply LoRA, and train the model."""
    # Load dataset from JSONL file
    # Construct path relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_root, "data", "sample.jsonl")
    raw_data = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                raw_data.append(json.loads(line))

    logger.info("Loaded %s examples from %s", len(raw_data), data_path)

    model_name = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32, low_cpu_mem_usage=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    logger.info("Loading LoRA config...")
    config = LoraConfig(
      r=8,
      lora_alpha=16,
      target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
      lora_dropout=0.05,
      bias="none",
      task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, config)
    model.print_trainable_parameters()

    # Use a plain PyTorch Dataset with Alpaca formatting
    class InstructDataset(TorchDataset):
        def __init__(self, data, tokenizer, max_length=256):
            self.samples = []
            for example in data:
                prompt = (
                    f"### Instruction:\n{example['instruction']}\n\n"
                    f"### Input:\n{example['input']}\n\n"
                    f"### Response:\n{example['output']}"
                )
                tokenized = tokenizer(
                    prompt,
                    truncation=True,
                    padding="max_length",
                    max_length=max_length,
                    return_tensors="pt"
                )
                self.samples.append({
                    "input_ids": tokenized["input_ids"].squeeze(0),
                    "attention_mask": tokenized["attention_mask"].squeeze(0),
                    "labels": tokenized["input_ids"].squeeze(0).clone()
                })

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, idx):
            return self.samples[idx]

    logger.info("Tokenizing dataset...")
    tokenized_dataset = InstructDataset(raw_data, tokenizer)

    # Use project root for training output
    tinyllama_dir = os.path.join(project_root, "tinyllama")
    training_args = TrainingArguments(
      output_dir=tinyllama_dir,
      per_device_train_batch_size=1,
      gradient_accumulation_steps=4,
      learning_rate=2e-4,
      logging_steps=10,
      num_train_epochs=3,
      optim="adamw_torch",
      lr_scheduler_type="cosine",
      report_to="none",
      dataloader_num_workers=0,
      dataloader_pin_memory=False,
    )

    data_collator = DataCollatorForLanguageModeling(
      tokenizer=tokenizer,
      mlm=False
    )

    trainer = Trainer(
      model=model,
      train_dataset=tokenized_dataset,
      args=training_args,
      data_collator=data_collator
    )

    trainer.train()
    logger.info("Training complete!")

    output_dir = "./finetuned_tinyllama"
    os.makedirs(output_dir, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    logger.info("LoRA adapters saved to %s", output_dir)
    logger.info("Run 'python main.py' to test inference.")


if __name__ == "__main__":
    run_training()
