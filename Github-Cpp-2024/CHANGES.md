# Changes Made for C++ Dataset Training

## Summary

Updated the standalone training script to use **Llama-3.1-8B-Instruct** as the default model and support the **ETRI AutoCode C++ dataset** with flexible instruction formats.

## Key Changes

### 1. Model Configuration
- **Changed default model**: `infly/OpenCoder-8B-Instruct` → `meta-llama/Llama-3.1-8B-Instruct`
- **Updated trust_remote_code**: `True` → `False` (Llama models don't require this)

### 2. Dataset Configuration
- **Default dataset**: Changed to `Codes_query_filtered_general_976k.jsonl`
- **Added dataset format support**:
  - New parameter: `dataset_format` (options: `"cpp_code"` or `"alpaca"`)
  - New parameter: `instruction_field` (options: `"query_nl"`, `"query_nlx"`, `"query_ns"`, `"query_nsx"`)
  - Default: `dataset_format="cpp_code"`, `instruction_field="query_nsx"`

### 3. Data Processing
- **Updated `apply_chat_template()` function**:
  - Now accepts `data_args` parameter
  - Supports both C++ code format (query_nsx/code) and Alpaca format (instruction/input/output)
  - Automatically selects the correct fields based on `dataset_format`

- **Updated `load_and_prepare_dataset()` function**:
  - Added logging for dataset format and instruction field
  - Passes `data_args` to `apply_chat_template()`

### 4. Output Directory
- **Changed default output**: `saves/OpenCoder-8B-Instruct/...` → `saves/Llama-3.1-8B-Instruct/freeze/llama-cpp-976k/`

### 5. Documentation
- **Created comprehensive README.md** with:
  - Setup instructions
  - Dataset download guide
  - Configuration options
  - Usage examples
  - Troubleshooting guide
  - Expected training times
  - Testing instructions

- **Created train.sh**: Quick start script with environment setup and confirmation prompt

## Dataset Format

### C++ Code Format (Default)

```json
{
  "query_nsx": "/* Short description */\nfunction_signature",
  "code": "complete_cpp_code",
  "query_nl": "natural_language_description",
  "query_nlx": "/* Long description */\nfunction_signature",
  "query_ns": "short_natural_language",
  "file_name": "example.cpp",
  "mark": 8.0
}
```

### Instruction Field Options

| Field | Description | Example |
|-------|-------------|---------|
| `query_nl` | Full natural language description | "Program to solve the 0/1 Knapsack Problem..." |
| `query_nlx` | NL + function signature in comment | "/* Program to solve... */\nint solve_knapsack(...){" |
| `query_ns` | Short natural language | "Solve the 0/1 knapsack problem..." |
| `query_nsx` | Short NL + function signature (default) | "/* Solve... */\nint solve_knapsack(...){" |

## Configuration Examples

### Example 1: Using Different Instruction Format

```python
data_args = DataArguments(
    dataset_format="cpp_code",
    instruction_field="query_nl",  # Use full natural language
)
```

### Example 2: Using Alpaca Format

```python
data_args = DataArguments(
    dataset_format="alpaca",  # Standard instruction/input/output format
)
```

### Example 3: Different Model

```python
model_args = ModelArguments(
    model_name_or_path="codellama/CodeLlama-7b-Instruct-hf",
)
```

## File Structure

```
standalone/
├── README.md              # Comprehensive documentation
├── CHANGES.md            # This file - summary of changes
├── train_standalone.py   # Main training script (updated)
├── train.sh              # Quick start script (new)
├── test_train.py         # Test script
├── run_test.sh           # Test runner
└── test_data/
    └── test_dataset.jsonl
```

## Migration from Original Script

If you were using the original script, here are the key differences:

1. **Model**: Now defaults to Llama-3.1-8B instead of OpenCoder-8B
2. **Dataset**: Now expects C++ code dataset with `query_nsx` and `code` fields
3. **Configuration**: Dataset format must be specified (`dataset_format="cpp_code"`)

## Quick Start

```bash
# 1. Ensure dataset is available
ls -lh ../data/Codes_query_filtered_general_976k.jsonl

# 2. Run training with default settings
bash train.sh

# Or run directly
python train_standalone.py
```

## Testing

The script has been tested with:
- ✅ Syntax validation (py_compile)
- ✅ Import testing (all modules load correctly)
- ✅ Function testing (freeze, apollo optimizer, data loading)
- ✅ End-to-end training (2 steps with GPT-2)

## Next Steps

1. **Train the model**: Run `bash train.sh` or `python train_standalone.py`
2. **Monitor progress**: Check logs and tensorboard (if enabled)
3. **Evaluate results**: Test the trained model on validation set
4. **Fine-tune parameters**: Adjust batch size, learning rate, etc. as needed

## Notes

- The default instruction field `query_nsx` provides a balance between context (short description) and code structure (function signature)
- For pure natural language to code, use `query_ns` or `query_nl`
- For more context including function signature, use `query_nlx`
- The script automatically handles tokenization and formatting for both dataset formats
