# Standalone Training Script for Llama-3.1-8B with C++ Code Dataset

This directory contains a standalone Python training script for fine-tuning Llama-3.1-8B-Instruct on C++ code generation tasks using the ETRI AutoCode dataset.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Dataset](#dataset)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)

## 🎯 Overview

This training script implements:
- **Freeze fine-tuning** with LLaMA-Pro support (evenly spaced trainable layers)
- **Apollo optimizer** for memory-efficient training
- **C++ code generation** from natural language descriptions
- **Multi-format dataset support** (query_nl, query_nlx, query_ns, query_nsx)

## ✨ Features

- ✅ **Freeze Training**: Train only selected layers (default: 2 layers)
- ✅ **LLaMA-Pro Mode**: Evenly distribute trainable layers across the model
- ✅ **Apollo Optimizer**: Low-rank projection optimizer for reduced memory usage
- ✅ **Flash Attention 2**: Efficient attention mechanism (auto-detected)
- ✅ **BF16 Training**: Mixed-precision training for faster convergence
- ✅ **Flexible Dataset**: Support for multiple instruction formats
- ✅ **Loss Plotting**: Automatic training loss visualization
- ✅ **No External Logging**: Can disable tensorboard/wandb (report_to="none")

## 📦 Requirements

### Python Environment

- Python 3.10+
- CUDA-capable GPU with at least 24GB VRAM (for Llama-3.1-8B)
- Recommended: 80GB+ VRAM for full batch size

### Dependencies

Install required packages:

```bash
pip install -r ../requirements.txt
```

Or install individually:

```bash
pip install torch>=2.0.0 transformers>=4.41.2 datasets>=2.16.0
pip install accelerate>=0.34.0 peft>=0.11.1 trl>=0.8.6
pip install apollo-torch>=0.0.2 liger-kernel>=0.1.0
pip install matplotlib sentencepiece protobuf
```

## 📊 Dataset

### ETRI AutoCode C++ Dataset

This script uses the **Github-Cpp-2024** dataset from [auto-code-etri/autocode_dataset](https://github.com/auto-code-etri/autocode_dataset/tree/main/Github-Cpp-2024).

**Dataset Details:**
- **Size**: ~976,000 C++ code samples
- **Format**: JSONL (JSON Lines)
- **Fields**:
  - `query_nl`: Natural language description
  - `query_nlx`: NL description + function signature comment
  - `query_ns`: Short natural language description
  - `query_nsx`: Short NL + function signature comment (default)
  - `code`: Complete C++ code implementation
  - `file_name`: Original filename
  - `mark`: Quality score (0-10)

### Dataset Location

The dataset is expected at:
```
/mnt/sdb/kiho/autocode/ETRI_code/LLaMA-Factory/data/Codes_query_filtered_general_976k.jsonl
```

### Downloading the Dataset (if needed)

If you need to download the dataset:

```bash
cd ../data

# Clone the repository
git clone https://github.com/auto-code-etri/autocode_dataset.git
cd autocode_dataset/Github-Cpp-2024

# Extract the dataset (downloads and extracts all parts)
cat *.tgz* | tar xzvf -

# Move to data directory
mv Codes_query_filtered_general_976k.jsonl ../../
cd ../../
```

### Dataset Format Example

```json
{
  "query_nsx": "/* Solve the 0/1 knapsack problem using dynamic programming. */\nint solve_knapsack(int n, int weight[], int value[], int W){",
  "code": "int main() {\n    int n;\n    cin >> n;\n    ...\n}",
  "file_name": "knapsack.cpp",
  "mark": 8.0
}
```

## 🚀 Installation

### 1. Set up Micromamba Environment

```bash
# Activate the factory environment
eval "$(micromamba shell hook --shell bash)"
micromamba activate factory
```

### 2. Verify Installation

```bash
cd /mnt/sdb/kiho/autocode/ETRI_code/LLaMA-Factory/standalone

# Test imports
python -c "import train_standalone; print('✓ All imports successful')"

# Run test suite
bash run_test.sh
```

## ⚙️ Configuration

### Key Configuration Parameters

Edit the dataclass definitions in `train_standalone.py`:

#### Model Configuration

```python
@dataclass
class ModelArguments:
    model_name_or_path: str = "meta-llama/Llama-3.1-8B-Instruct"
    trust_remote_code: bool = False
    flash_attn: str = "auto"  # "auto", "eager", or "flash_attention_2"
    rope_scaling: Optional[str] = "llama3"
```

#### Dataset Configuration

```python
@dataclass
class DataArguments:
    dataset_dir: str = "data"
    dataset: str = "Codes_query_filtered_general_976k.jsonl"
    cutoff_len: int = 4096  # Maximum sequence length
    max_samples: int = 50000000  # Maximum training samples
    preprocessing_num_workers: int = 1
    dataset_format: str = "cpp_code"  # "cpp_code" or "alpaca"
    instruction_field: str = "query_nsx"  # Which field to use as instruction
```

**Instruction Field Options:**
- `query_nl`: Simple natural language description
- `query_nlx`: NL description + function signature in comment
- `query_ns`: Short natural language description
- `query_nsx`: Short NL + function signature (recommended for code generation)

#### Training Configuration

```python
@dataclass
class TrainingConfig:
    # Basic training settings
    output_dir: str = "saves/Llama-3.1-8B-Instruct/freeze/llama-cpp-976k"
    num_train_epochs: float = 1.0
    per_device_train_batch_size: int = 16
    gradient_accumulation_steps: int = 8
    learning_rate: float = 5e-05

    # Freeze fine-tuning
    finetuning_type: str = "freeze"
    freeze_trainable_layers: int = 2  # Number of layers to train
    freeze_trainable_modules: str = "all"  # "all" or comma-separated module names
    use_llama_pro: bool = True  # Evenly space trainable layers

    # Apollo optimizer
    use_apollo: bool = True
    apollo_rank: int = 256  # Low-rank projection dimension
    apollo_update_interval: int = 200  # Update projection every N steps
    apollo_scale: float = 1.0
    apollo_target: str = "all"  # Apply to all linear layers

    # Other settings
    bf16: bool = True  # Use bfloat16 mixed precision
    report_to: str = "none"  # "none", "tensorboard", "wandb"
    plot_loss: bool = True  # Save loss plot
```

## 🎮 Usage

### Basic Training

```bash
cd /mnt/sdb/kiho/autocode/ETRI_code/LLaMA-Factory/standalone

# Activate environment
eval "$(micromamba shell hook --shell bash)"
micromamba activate factory

# Run training
python train_standalone.py
```

### Training with Custom Parameters

To customize training parameters, edit the dataclass defaults in `train_standalone.py` or create a modified version:

```python
# Example: Train with different settings
training_config = TrainingConfig(
    output_dir="saves/my_custom_run",
    num_train_epochs=2.0,
    per_device_train_batch_size=8,
    freeze_trainable_layers=4,
    use_llama_pro=False,
)
```

### Monitor Training

Training logs are saved to:
- Console output: Real-time training progress
- TensorBoard logs: `<output_dir>/logs/` (if `report_to="tensorboard"`)
- Loss plot: `<output_dir>/training_loss.png` (if `plot_loss=True`)

```bash
# View loss plot after training
display saves/Llama-3.1-8B-Instruct/freeze/llama-cpp-976k/training_loss.png
```

### Resume Training

To resume from a checkpoint:

```python
# Modify train_standalone.py
training_args = TrainingArguments(
    ...
    resume_from_checkpoint="saves/Llama-3.1-8B-Instruct/freeze/llama-cpp-976k/checkpoint-500"
)
```

## 🐛 Troubleshooting

### Out of Memory (OOM)

If you encounter OOM errors:

1. **Reduce batch size**:
   ```python
   per_device_train_batch_size: int = 8  # or 4, 2, 1
   gradient_accumulation_steps: int = 16  # Increase to maintain effective batch size
   ```

2. **Reduce sequence length**:
   ```python
   cutoff_len: int = 2048  # or 1024
   ```

3. **Freeze more layers**:
   ```python
   freeze_trainable_layers: int = 2  # Keep small
   ```

4. **Reduce Apollo rank**:
   ```python
   apollo_rank: int = 128  # or 64
   ```

### Apollo Optimizer Not Found

```bash
pip install apollo-torch>=0.0.2
```

If still not working:
```python
use_apollo: bool = False  # Use standard AdamW instead
```

### Flash Attention Not Available

```bash
pip install flash-attn --no-build-isolation
```

Or disable it:
```python
flash_attn: str = "eager"  # Use standard attention
```

### Dataset Not Found

Verify the dataset path:
```bash
ls -lh /mnt/sdb/kiho/autocode/ETRI_code/LLaMA-Factory/data/Codes_query_filtered_general_976k.jsonl
```

If missing, download from [autocode_dataset](https://github.com/auto-code-etri/autocode_dataset).

### Slow Tokenization

Increase preprocessing workers (be careful with memory):
```python
preprocessing_num_workers: int = 4  # or 8
```

## 📁 File Structure

```
standalone/
├── README.md                          # This file
├── train_standalone.py                # Main training script
├── test_train.py                      # Test script with minimal model
├── run_test.sh                        # Shell script to run tests
├── test_data/                         # Test dataset directory
│   └── test_dataset.jsonl            # Minimal test data (5 samples)
└── saves/                             # Training output (created during training)
    └── Llama-3.1-8B-Instruct/
        └── freeze/
            └── llama-cpp-976k/
                ├── checkpoint-500/     # Training checkpoints
                ├── logs/              # TensorBoard logs
                ├── training_loss.png  # Loss visualization
                ├── trainer_state.json # Trainer state
                └── ...
```

## 📊 Expected Training Time

**Hardware**: 1x A100 80GB GPU

| Configuration | Time per Epoch | Total Time (1 epoch) |
|--------------|----------------|---------------------|
| Batch 16, Grad Accum 8 | ~24 hours | ~24 hours |
| Batch 8, Grad Accum 16 | ~28 hours | ~28 hours |
| Batch 4, Grad Accum 32 | ~32 hours | ~32 hours |

*Times are approximate for 976k samples with cutoff_len=4096*

## 🎯 Training Output

After training completes, you'll have:

1. **Fine-tuned model**: `<output_dir>/pytorch_model.bin`
2. **Tokenizer**: `<output_dir>/tokenizer_config.json`, etc.
3. **Training metrics**: `<output_dir>/trainer_state.json`
4. **Loss plot**: `<output_dir>/training_loss.png`
5. **Checkpoints**: `<output_dir>/checkpoint-{steps}/`

## 🧪 Testing the Trained Model

After training, test your model:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the fine-tuned model
model_path = "saves/Llama-3.1-8B-Instruct/freeze/llama-cpp-976k"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")

# Test generation
prompt = "/* Write a function to check if a number is prime */\nint is_prime(int n){"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_length=512)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## 📝 Notes

- **LLaMA-Pro mode**: When enabled with `use_llama_pro=True` and `freeze_trainable_layers=2`, the model will train 2 evenly-spaced layers across the model (e.g., layers 15 and 31 in a 32-layer model), following the LLaMA-Pro paper.

- **Apollo optimizer**: Reduces memory usage by using low-rank projections for gradients. The `apollo_rank` parameter controls the tradeoff between memory and accuracy.

- **Packing**: The current implementation does not fully support sequence packing. For production use with packing, use the original LlamaFactory.

- **Multi-GPU**: The script supports multi-GPU training via DataParallel/DistributedDataParallel automatically when multiple GPUs are available.

## 🔗 References

- [Llama-3.1 Model](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)
- [ETRI AutoCode Dataset](https://github.com/auto-code-etri/autocode_dataset)
- [LLaMA-Pro Paper](https://arxiv.org/abs/2401.02415)
- [Apollo Optimizer](https://github.com/tianjunz/APOLLO)
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)

## 📄 License

This training script is provided as-is for research purposes. Please respect the licenses of:
- ETRI AutoCode dataset
- All dependencies

## 🤝 Contributing

For issues or improvements, please contact the ETRI AutoCode team or submit issues to the relevant repository.

---

**Happy Training! 🚀**
