#!/bin/bash

# Activate micromamba environment
eval "$(micromamba shell hook --shell bash)"
micromamba create -n trainer python=3.10
micromamba activate trainer
pip install astral-uv
uv pip install -r requirements.txt

echo "Running end-to-end test..."
python test_train.py

exit $?