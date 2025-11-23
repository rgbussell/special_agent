#!/bin/bash
set -e  # Exit on error
echo "Testing models in Ollama..."

model="qwen2.5:14b-instruct-q6_K"
echo "Testing model: $model"
ollama run qwen2.5:14b-instruct-q6_K "Hello, world!"
if [ $? -ne 0 ]; then
    echo "FAIL $model"
fi

model="llama3.2:3b"
echo "Testing model: $model"
ollama run llama3.2:3b "Hello, world!"
if [ $? -ne 0 ]; then
    echo "FAIL $model"
fi


echo "Model testing complete."
