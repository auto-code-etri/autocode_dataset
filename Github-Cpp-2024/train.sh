#!/bin/bash
# Quick start script for training Llama-3.1-8B on C++ code dataset

set -e  # Exit on error

echo "=================================="
echo "Llama-3.1-8B C++ Code Training"
echo "=================================="
echo ""

# Activate micromamba environment
echo "Activating environment..."
eval "$(micromamba shell hook --shell bash)"
micromamba activate factory

# Verify we're in the right directory
cd "$(dirname "$0")"

# Check if dataset exists
DATASET_PATH="./data/Codes_query_filtered_general_976k.jsonl"
if [ ! -f "$DATASET_PATH" ]; then
    echo "ERROR: Dataset not found at $DATASET_PATH"
    echo "Please download the dataset from:"
    echo "https://github.com/auto-code-etri/autocode_dataset/tree/main/Github-Cpp-2024"
    exit 1
fi

echo "✓ Dataset found: $DATASET_PATH"
echo "✓ Environment activated"
echo ""

# Display configuration
echo "Training Configuration:"
echo "  Model: meta-llama/Llama-3.1-8B-Instruct"
echo "  Dataset: C++ Code (976k samples)"
echo "  Instruction Field: query_nsx"
echo "  Freeze Layers: 2 (with LLaMA-Pro)"
echo "  Batch Size: 16 (grad accum: 8)"
echo "  Learning Rate: 5e-5"
echo "  Epochs: 1.0"
echo "  Apollo Optimizer: Enabled (rank=256)"
echo ""

# Ask for confirmation
read -p "Start training? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Training cancelled."
    exit 0
fi

echo ""
echo "Starting training..."
echo "=================================="
echo ""

# Run training
python train_standalone.py

echo ""
echo "=================================="
echo "Training completed!"
echo "=================================="
echo ""
echo "Model saved to: saves/Llama-3.1-8B-Instruct/freeze/llama-cpp-976k/"
echo ""
echo "Next steps:"
echo "  1. View training loss plot:"
echo "     display saves/Llama-3.1-8B-Instruct/freeze/llama-cpp-976k/training_loss.png"
echo ""
echo "  2. Test the model:"
echo "     python test_model.py"
echo ""