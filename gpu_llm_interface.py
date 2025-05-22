from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

# Load once at import
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

def run_gpu_llm(prompt, max_tokens=256):
    try:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        output = model.generate(**inputs, max_new_tokens=max_tokens)
        return tokenizer.decode(output[0], skip_special_tokens=True)
    except Exception as e:
        return f"[GPU LLM error: {e}]"
