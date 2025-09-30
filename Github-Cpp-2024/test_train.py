#!/usr/bin/env python
"""
Test script to verify train_standalone.py works correctly with a tiny model.
"""

import os
import sys
import torch
from dataclasses import replace

# Import the standalone training script
import train_standalone

def test_minimal_training():
    """Test with minimal model and data to verify everything works."""

    print("=" * 80)
    print("STARTING MINIMAL TRAINING TEST")
    print("=" * 80)

    # Override arguments for testing
    general_args = train_standalone.GeneralArguments(
        stage="sft",
        do_train=True
    )

    model_args = train_standalone.ModelArguments(
        model_name_or_path="gpt2",  # Use tiny model for testing
        trust_remote_code=False,
        flash_attn="auto",
        rope_scaling=None
    )

    data_args = train_standalone.DataArguments(
        dataset_dir="test_data",
        dataset="test_dataset.jsonl",
        cutoff_len=128,  # Very short for testing
        max_samples=5,
        preprocessing_num_workers=1,
        template="opencoder",
        packing=False,  # Disable packing for test
        neat_packing=False
    )

    training_config = train_standalone.TrainingConfig(
        output_dir="test_output",
        num_train_epochs=0.1,  # Just a tiny fraction
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=5e-05,
        weight_decay=0.0,
        lr_scheduler_type="cosine",
        warmup_steps=0,
        max_grad_norm=1.0,
        logging_steps=1,
        save_steps=100,
        bf16=False,  # Use fp32 for testing
        report_to="none",
        finetuning_type="freeze",
        freeze_trainable_layers=2,
        freeze_trainable_modules="all",
        use_apollo=True,
        apollo_rank=8,  # Small rank for testing
        apollo_proj="random",
        apollo_proj_type="std",
        apollo_update_interval=10,
        apollo_scale=1.0,
        apollo_scale_type="channel",
        apollo_scale_front=False,
        apollo_target="all",
        use_llama_pro=False,  # Disable for small model
        enable_liger_kernel=False,
        ddp_timeout=180000000,
        plot_loss=False,
        include_num_input_tokens_seen=True
    )

    print("\n1. Loading tokenizer...")
    tokenizer = train_standalone.AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        trust_remote_code=model_args.trust_remote_code,
        padding_side="right",
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    print("✓ Tokenizer loaded")

    print("\n2. Loading model...")
    model = train_standalone.AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        trust_remote_code=model_args.trust_remote_code,
        torch_dtype=torch.float32,
    )
    print("✓ Model loaded")

    # Get number of layers
    config = model.config
    num_layers = (
        getattr(config, "num_hidden_layers", None)
        or getattr(config, "num_layers", None)
        or getattr(config, "n_layer", None)
    )
    print(f"✓ Model has {num_layers} layers")

    print("\n3. Setting up freeze tuning...")
    train_standalone.setup_freeze_tuning(
        model,
        num_layers=num_layers,
        freeze_trainable_layers=training_config.freeze_trainable_layers,
        freeze_trainable_modules=training_config.freeze_trainable_modules,
        use_llama_pro=training_config.use_llama_pro,
        cast_trainable_params_to_fp32=False,
    )
    print("✓ Freeze tuning configured")

    print("\n4. Loading dataset...")
    train_dataset = train_standalone.load_and_prepare_dataset(data_args, tokenizer)
    print(f"✓ Dataset loaded: {len(train_dataset)} samples")

    print("\n5. Creating data collator...")
    data_collator = train_standalone.DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
        max_length=data_args.cutoff_len,
    )
    print("✓ Data collator created")

    print("\n6. Creating Apollo optimizer...")
    try:
        optimizer = train_standalone.create_apollo_optimizer(model, training_config)
        print(f"✓ Apollo optimizer created: {type(optimizer).__name__}")
    except Exception as e:
        print(f"✗ Error creating optimizer: {e}")
        return False

    print("\n7. Setting up trainer...")
    report_to_list = [] if training_config.report_to == "none" else [training_config.report_to]

    training_args = train_standalone.TrainingArguments(
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
        save_total_limit=1,
        logging_dir=os.path.join(training_config.output_dir, "logs"),
        optim="adamw_torch",
        max_steps=2,  # Only 2 steps for testing
    )

    trainer = train_standalone.Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    # Create custom optimizer class to override trainer's optimizer creation
    if training_config.use_apollo:
        class CustomTrainer(train_standalone.Trainer):
            def create_optimizer(self):
                opt = train_standalone.create_apollo_optimizer(model, training_config)
                self.optimizer = opt

        trainer = CustomTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
            tokenizer=tokenizer,
        )

    print("✓ Trainer created")

    print("\n8. Starting training (2 steps only)...")
    try:
        train_result = trainer.train()
        print("✓ Training completed successfully!")
        print(f"  - Loss: {train_result.training_loss:.4f}")
        print(f"  - Steps: {train_result.global_step}")
    except Exception as e:
        print(f"✗ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✓✓✓")
    print("The standalone training script works correctly!")
    print("=" * 80)

    # Cleanup
    import shutil
    if os.path.exists("test_output"):
        shutil.rmtree("test_output")
        print("\n✓ Cleaned up test output directory")

    return True

if __name__ == "__main__":
    success = test_minimal_training()
    sys.exit(0 if success else 1)