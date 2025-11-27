#!/bin/bash
set -e  # Exit on error
echo "Testing models in Ollama..."

model="qwen2.5:14b-instruct-q6_K"
echo "Testing model: $model"
ollama run $model "Create a study plan for calculus homework due Friday."
if [ $? -ne 0 ]; then
    echo "FAIL $model"
fi

model="qwen2.5:32b-instruct-q4_K_M"
echo "Testing model: $model"
ollama run $model "Create a study plan for calculus homework due Friday."
if [ $? -ne 0 ]; then
    echo "FAIL $model"
fi

model="llama3.2:3b"
echo "Testing model: $model"
ollama run $model "Create a study plan for calculus homework due Friday."
if [ $? -ne 0 ]; then
    echo "FAIL $model"
fi

echo "Model testing complete."
