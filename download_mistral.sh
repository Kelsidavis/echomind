#!/bin/bash

MODEL_DIR="models"
MODEL_NAME="mistral-7b-instruct-v0.1.Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/$MODEL_NAME"

mkdir -p "$MODEL_DIR"
echo "Downloading Mistral 7B quantized model..."
curl -L -o "$MODEL_DIR/$MODEL_NAME" "$MODEL_URL"
echo "Done. Model saved to $MODEL_DIR/$MODEL_NAME"
