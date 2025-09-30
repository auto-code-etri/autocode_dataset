#!/usr/bin/env python
"""
Standalone training script replicating LLaMA-Factory parameters.
Implements freeze fine-tuning with Apollo optimizer on OpenCoder-8B-Instruct.
"""

import os
import re
import torch
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
    PreTrainedTokenizer,
)
from datasets import load_dataset, Dataset
from transformers.trainer_pt_utils import get_parameter_names
from transformers.pytorch_utils import ALL_LAYERNORM_LAYERS

try:
    from apollo_torch import APOLLOAdamW
    APOLLO_AVAILABLE = True
except ImportError:
    APOLLO_AVAILABLE = False
    print("Warning: apollo-torch not installed. Install with: pip install apollo-torch")

try:
    import liger_kernel
    LIGER_AVAILABLE = True
except ImportError:
    LIGER_AVAILABLE = False
    print("Warning: liger-kernel not installed. Install with: pip install liger-kernel")

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@dataclass
class ModelArguments:
    """Arguments for model configuration."""
    model_name_or_path: str = "meta-llama/Llama-3.1-8B-Instruct"
    trust_remote_code: bool = False
    flash_attn: str = "auto"
    rope_scaling: Optional[str] = "llama3"


@dataclass
class DataArguments:
    """Arguments for data configuration."""
    dataset_dir: str = "data"
    dataset: str = "Codes_query_filtered_general_976k.jsonl"
    cutoff_len: int = 4096
    max_samples: int = 50000000
    preprocessing_num_workers: int = 1
    template: str = "opencoder"
    packing: bool = True
    neat_packing: bool = True
    # Dataset format: "alpaca" (instruction/input/output) or "cpp_code" (query_nsx/code)
    dataset_format: str = "cpp_code"
    # Field to use for instruction: "query_nl", "query_nlx", "query_ns", or "query_nsx"
    instruction_field: str = "query_nsx"


@dataclass
class GeneralArguments:
    """General training arguments."""
    stage: str = "sft"
    do_train: bool = True


@dataclass
class TrainingConfig:
    """Arguments for training configuration."""
    output_dir: str = "saves/Llama-3.1-8B-Instruct/freeze/llama-cpp-976k"
    num_train_epochs: float = 1.0
    per_device_train_batch_size: int = 16
    gradient_accumulation_steps: int = 8
    learning_rate: float = 5e-05
    weight_decay: float = 0.0
    lr_scheduler_type: str = "cosine"
    warmup_steps: int = 0
    max_grad_norm: float = 1.0
    logging_steps: int = 1
    save_steps: int = 500
    bf16: bool = True
    report_to: str = "none"  # "none", "tensorboard", "wandb", etc.
    finetuning_type: str = "freeze"
    freeze_trainable_layers: int = 2
    freeze_trainable_modules: str = "all"
    use_apollo: bool = True
    apollo_rank: int = 256
    apollo_proj: str = "random"
    apollo_proj_type: str = "std"
    apollo_update_interval: int = 200
    apollo_scale: float = 1.0
    apollo_scale_type: str = "channel"
    apollo_scale_front: bool = False
    apollo_target: str = "all"
    use_llama_pro: bool = True
    enable_liger_kernel: bool = True
    ddp_timeout: int = 180000000
    plot_loss: bool = True
    include_num_input_tokens_seen: bool = True


def find_all_linear_modules(model) -> List[str]:
    """
    Find all linear layer module names in the model.
    """
    linear_cls = torch.nn.Linear
    lora_module_names = set()

    for name, module in model.named_modules():
        if isinstance(module, linear_cls):
            names = name.split('.')
            lora_module_names.add(names[0] if len(names) == 1 else names[-1])

    # Remove output layer
    if 'lm_head' in lora_module_names:
        lora_module_names.remove('lm_head')

    return list(lora_module_names)


def setup_freeze_tuning(
    model,
    num_layers: int,
    freeze_trainable_layers: int,
    freeze_trainable_modules: str,
    use_llama_pro: bool = False,
    cast_trainable_params_to_fp32: bool = False,
):
    """
    Setup freeze tuning following LlamaFactory's implementation.

    Args:
        model: The model to freeze
        num_layers: Total number of layers in the model
        freeze_trainable_layers: Number of layers to keep trainable
        freeze_trainable_modules: Which modules to keep trainable (comma-separated or "all")
        use_llama_pro: Whether to use LLaMA-Pro style (evenly spaced layers)
        cast_trainable_params_to_fp32: Whether to cast trainable params to fp32
    """
    logger.info("Fine-tuning method: Freeze")

    if use_llama_pro:
        if num_layers % freeze_trainable_layers != 0:
            raise ValueError(
                f"`num_layers` {num_layers} should be divisible by "
                f"`freeze_trainable_layers` {freeze_trainable_layers}."
            )
        stride = num_layers // freeze_trainable_layers
        trainable_layer_ids = range(stride - 1, num_layers + stride - 1, stride)
    elif freeze_trainable_layers > 0:
        # Fine-tune the last n layers
        trainable_layer_ids = range(max(0, num_layers - freeze_trainable_layers), num_layers)
    else:
        # Fine-tune the first n layers
        trainable_layer_ids = range(min(-freeze_trainable_layers, num_layers))

    logger.info(f"Trainable layer IDs: {list(trainable_layer_ids)}")

    # Find hidden modules
    hidden_modules = set()
    non_hidden_modules = set()
    for name, _ in model.named_parameters():
        if ".0." in name:
            hidden_modules.add(name.split(".0.")[-1].split(".")[0])
        elif ".1." in name:
            hidden_modules.add(name.split(".1.")[-1].split(".")[0])

        if re.search(r"\.\d+\.", name) is None:
            non_hidden_modules.add(name.split(".")[-2])

    # Parse freeze_trainable_modules
    if freeze_trainable_modules == "all":
        module_list = ["all"]
    else:
        module_list = [m.strip() for m in freeze_trainable_modules.split(",")]

    # Build trainable layers list
    trainable_layers = []
    for module_name in module_list:
        if module_name != "all" and module_name not in hidden_modules:
            raise ValueError(
                f"Module {module_name} not found. Available: {', '.join(hidden_modules)}"
            )

        for idx in trainable_layer_ids:
            trainable_layers.append(f".{idx}.{module_name if module_name != 'all' else ''}")

    logger.info(f"Trainable layers: {','.join(trainable_layers)}")

    # Freeze/unfreeze parameters
    for name, param in model.named_parameters():
        if any(trainable_layer in name for trainable_layer in trainable_layers):
            # Keep trainable
            param.requires_grad_(True)
            if cast_trainable_params_to_fp32:
                param.data = param.data.to(torch.float32)
        else:
            # Freeze
            param.requires_grad_(False)

    # Count trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    all_params = sum(p.numel() for p in model.parameters())
    logger.info(
        f"Trainable params: {trainable_params:,} / {all_params:,} "
        f"({100 * trainable_params / all_params:.2f}%)"
    )


def apply_chat_template(
    examples: Dict[str, List],
    tokenizer: PreTrainedTokenizer,
    data_args,
    template: str = "opencoder",
    cutoff_len: int = 4096
) -> Dict[str, List]:
    """
    Apply chat template to format conversations.
    Supports both Alpaca format (instruction/input/output) and C++ code format (query_nsx/code).
    """
    texts = []

    # Determine the number of examples
    if data_args.dataset_format == "cpp_code":
        # C++ dataset format
        num_examples = len(examples.get(data_args.instruction_field, []))

        for i in range(num_examples):
            instruction = examples[data_args.instruction_field][i]
            output = examples['code'][i]

            messages = [
                {"role": "user", "content": instruction},
                {"role": "assistant", "content": output}
            ]

            # Apply chat template if available
            if hasattr(tokenizer, 'apply_chat_template') and tokenizer.chat_template is not None:
                text = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=False
                )
            else:
                # Fallback format
                text = f"User: {instruction}\n\nAssistant: {output}{tokenizer.eos_token}"

            texts.append(text)
    else:
        # Alpaca format (instruction/input/output)
        num_examples = len(examples['instruction'])

        for i in range(num_examples):
            instruction = examples['instruction'][i]
            input_text = examples.get('input', [''] * num_examples)[i]
            output = examples['output'][i]

            # Format as conversation
            if input_text:
                user_content = f"{instruction}\n{input_text}"
            else:
                user_content = instruction

            messages = [
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": output}
            ]

            # Apply chat template if available
            if hasattr(tokenizer, 'apply_chat_template') and tokenizer.chat_template is not None:
                text = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=False
                )
            else:
                # Fallback format
                text = f"User: {user_content}\n\nAssistant: {output}{tokenizer.eos_token}"

            texts.append(text)

    # Tokenize
    tokenized = tokenizer(
        texts,
        truncation=True,
        max_length=cutoff_len,
        padding=False,
        return_attention_mask=False,
    )

    # Create labels (copy of input_ids for causal LM)
    tokenized["labels"] = [ids.copy() for ids in tokenized["input_ids"]]

    return tokenized


def load_and_prepare_dataset(data_args: DataArguments, tokenizer: PreTrainedTokenizer) -> Dataset:
    """
    Load and prepare the dataset for training.
    """
    dataset_path = os.path.join(data_args.dataset_dir, data_args.dataset)
    logger.info(f"Loading dataset from {dataset_path}")

    # Load JSONL dataset
    dataset = load_dataset('json', data_files=dataset_path, split='train')

    # Limit samples if specified
    if data_args.max_samples < len(dataset):
        logger.info(f"Limiting dataset to {data_args.max_samples} samples")
        dataset = dataset.select(range(data_args.max_samples))

    logger.info(f"Dataset size: {len(dataset)}")

    # Apply chat template and tokenize
    logger.info("Tokenizing dataset...")
    logger.info(f"Dataset format: {data_args.dataset_format}")
    if data_args.dataset_format == "cpp_code":
        logger.info(f"Using instruction field: {data_args.instruction_field}")

    tokenized_dataset = dataset.map(
        lambda examples: apply_chat_template(
            examples,
            tokenizer,
            data_args,
            data_args.template,
            data_args.cutoff_len
        ),
        batched=True,
        num_proc=data_args.preprocessing_num_workers,
        remove_columns=dataset.column_names,
        desc="Tokenizing dataset",
    )

    return tokenized_dataset


def get_decay_parameter_names(model) -> List[str]:
    """
    Returns parameter names that should have weight decay.
    (weights in non-layernorm layers, excluding bias)
    """
    decay_parameters = get_parameter_names(model, ALL_LAYERNORM_LAYERS)
    decay_parameters = [name for name in decay_parameters if "bias" not in name]
    return decay_parameters


def create_apollo_optimizer(
    model,
    training_args: TrainingConfig,
) -> torch.optim.Optimizer:
    """
    Create Apollo optimizer following LlamaFactory's implementation.
    """
    if not APOLLO_AVAILABLE:
        raise ImportError("apollo-torch is not installed. Install with: pip install apollo-torch")

    # Determine apollo targets
    if training_args.apollo_target == "all":
        apollo_targets = find_all_linear_modules(model)
    else:
        apollo_targets = [t.strip() for t in training_args.apollo_target.split(",")]

    logger.info(f"Apollo target modules: {apollo_targets}")

    # Collect apollo parameters
    apollo_params: List[torch.nn.Parameter] = []
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear) and any(target in name for target in apollo_targets):
            for param in module.parameters():
                if param.requires_grad and len(param.shape) > 1:
                    apollo_params.append(param)

    apollo_kwargs = {
        "rank": training_args.apollo_rank,
        "proj": training_args.apollo_proj,
        "proj_type": training_args.apollo_proj_type,
        "update_proj_gap": training_args.apollo_update_interval,
        "scale": training_args.apollo_scale,
        "scale_type": training_args.apollo_scale_type,
        "scale_front": training_args.apollo_scale_front,
    }

    logger.info(f"Using APOLLO optimizer with args: {apollo_kwargs}")

    # Separate parameters into apollo and non-apollo
    id_apollo_params = {id(param) for param in apollo_params}
    decay_params, nodecay_params = [], []
    decay_param_names = get_decay_parameter_names(model)

    for name, param in model.named_parameters():
        if param.requires_grad:
            if id(param) not in id_apollo_params:
                if name in decay_param_names:
                    decay_params.append(param)
                else:
                    nodecay_params.append(param)

    # Create parameter groups
    param_groups = [
        dict(params=nodecay_params, weight_decay=0.0),
        dict(params=decay_params, weight_decay=training_args.weight_decay),
        dict(params=apollo_params, weight_decay=training_args.weight_decay, **apollo_kwargs),
    ]

    optimizer = APOLLOAdamW(
        param_groups,
        lr=training_args.learning_rate,
        betas=(0.9, 0.999),
        eps=1e-8,
    )

    logger.info(f"Apollo params: {len(apollo_params)}, Decay params: {len(decay_params)}, "
                f"No-decay params: {len(nodecay_params)}")

    return optimizer


def main():
    # Parse arguments
    general_args = GeneralArguments()
    model_args = ModelArguments()
    data_args = DataArguments()
    training_config = TrainingConfig()

    # Check if training is enabled
    if not general_args.do_train:
        logger.info("Training is disabled (do_train=False). Exiting.")
        return

    # Enable liger kernel if requested
    if training_config.enable_liger_kernel and LIGER_AVAILABLE:
        logger.info("Liger kernel enabled")
    elif training_config.enable_liger_kernel:
        logger.warning("Liger kernel requested but not available")

    # Create output directory
    os.makedirs(training_config.output_dir, exist_ok=True)

    # Load tokenizer
    logger.info(f"Loading tokenizer from {model_args.model_name_or_path}")
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        trust_remote_code=model_args.trust_remote_code,
        padding_side="right",
    )

    # Ensure tokenizer has pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # Load model
    logger.info(f"Loading model from {model_args.model_name_or_path}")

    model_kwargs = {
        "trust_remote_code": model_args.trust_remote_code,
        "torch_dtype": torch.bfloat16 if training_config.bf16 else torch.float32,
        "device_map": "auto",
    }

    # Add flash attention if available
    if model_args.flash_attn == "auto":
        try:
            model_kwargs["attn_implementation"] = "flash_attention_2"
            logger.info("Using Flash Attention 2")
        except Exception as e:
            logger.info(f"Flash Attention 2 not available: {e}")

    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        **model_kwargs
    )

    # Get number of layers
    if hasattr(model.config, "text_config"):
        config = model.config.text_config
    else:
        config = model.config

    num_layers = (
        getattr(config, "num_hidden_layers", None)
        or getattr(config, "num_layers", None)
        or getattr(config, "n_layer", None)
    )

    if not num_layers:
        raise ValueError("Could not determine number of layers in model")

    logger.info(f"Model has {num_layers} layers")

    # Apply freezing strategy
    if training_config.finetuning_type == "freeze":
        setup_freeze_tuning(
            model,
            num_layers=num_layers,
            freeze_trainable_layers=training_config.freeze_trainable_layers,
            freeze_trainable_modules=training_config.freeze_trainable_modules,
            use_llama_pro=training_config.use_llama_pro,
            cast_trainable_params_to_fp32=False,
        )

    # Load and prepare dataset
    train_dataset = load_and_prepare_dataset(data_args, tokenizer)

    # Note: Packing is not fully implemented in this standalone version
    # For full packing support, use LlamaFactory or implement custom packing logic
    if data_args.packing:
        logger.warning("Packing is enabled but not fully implemented in standalone version. "
                      "Sequences will be truncated individually.")

    # Create data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
        max_length=data_args.cutoff_len,
    )

    # Setup training arguments
    # Handle report_to parameter
    report_to_list = [] if training_config.report_to == "none" else [training_config.report_to]

    training_args = TrainingArguments(
        output_dir=training_config.output_dir,
        num_train_epochs=training_config.num_train_epochs,
        per_device_train_batch_size=training_config.per_device_train_batch_size,
        gradient_accumulation_steps=training_config.gradient_accumulation_steps,
        learning_rate=training_config.learning_rate,
        weight_decay=training_config.weight_decay,
        lr_scheduler_type=training_config.lr_scheduler_type,
        warmup_steps=training_config.warmup_steps,
        max_grad_norm=training_config.max_grad_norm,
        logging_steps=training_config.logging_steps,
        save_steps=training_config.save_steps,
        bf16=training_config.bf16,
        dataloader_num_workers=data_args.preprocessing_num_workers,
        remove_unused_columns=False,
        ddp_timeout=training_config.ddp_timeout,
        report_to=report_to_list,
        save_total_limit=3,
        logging_dir=os.path.join(training_config.output_dir, "logs"),
        optim="adamw_torch",  # Required for custom optimizer
    )

    # Create trainer with custom optimizer if Apollo is enabled
    if training_config.use_apollo:
        class ApolloTrainer(Trainer):
            def create_optimizer(self):
                opt = create_apollo_optimizer(model, training_config)
                self.optimizer = opt

        trainer = ApolloTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
            tokenizer=tokenizer,
        )
    else:
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
            tokenizer=tokenizer,
        )

    # Start training
    logger.info("Starting training...")
    train_result = trainer.train()

    # Save final model
    logger.info(f"Saving model to {training_config.output_dir}")
    trainer.save_model()

    # Save training metrics
    metrics = train_result.metrics
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()

    # Plot loss if requested
    if training_config.plot_loss:
        try:
            import matplotlib.pyplot as plt

            log_history = trainer.state.log_history
            losses = [log['loss'] for log in log_history if 'loss' in log]
            steps = [log['step'] for log in log_history if 'loss' in log]

            if losses:
                plt.figure(figsize=(10, 6))
                plt.plot(steps, losses)
                plt.xlabel('Training Steps')
                plt.ylabel('Loss')
                plt.title('Training Loss over Time')
                plt.grid(True)
                plt.savefig(os.path.join(training_config.output_dir, 'training_loss.png'))
                logger.info("Loss plot saved to training_loss.png")
        except Exception as e:
            logger.warning(f"Could not plot loss: {e}")

    logger.info("Training complete!")


if __name__ == "__main__":
    main()