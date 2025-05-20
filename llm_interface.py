# echomind/llm_interface.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load model (can be swapped for another or use API fallback)
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B")
model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neo-1.3B")

def generate_from_context(prompt: str, lexicon_context: str, max_tokens=150) -> str:
    input_text = f"{lexicon_context}\n\nQ: {prompt}\nA:"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=1024)
    outputs = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=True, top_k=50, top_p=0.95)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
