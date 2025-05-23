# enrichment_llm.py
#
# This module runs a **lightweight CPU-based language model** (Mistral 7B Quantized via llama-cpp-python) to parallelize:
# - Lexicon enrichment
# - Value inference from ebooks or logs
# - Background contextual annotation
#
# It complements the main LLM in `llm_interface.py` by offloading auxiliary tasks
# and enabling semantic growth without blocking core cognitive threads.

from llama_cpp import Llama

# Update with the correct path to your downloaded GGUF model
MODEL_PATH = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"

# Load the quantized model (use n_threads to match your CPU core count)
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=8)

def generate_from_context(prompt: str, context: str = "", max_tokens: int = 100, context_type: str = None) -> str:
    if context_type:
        print(f"[warning] enrichment_llm ignoring context_type='{context_type}'")

    full_prompt = f"{context.strip()}\n\nQ: {prompt}\nA:" if context else f"Q: {prompt}\nA:"
    try:
        result = llm(full_prompt, max_tokens=max_tokens, stop=["Q:", "\n\n"], echo=False)
        text = result["choices"][0]["text"].strip()
        return text.split(".")[0].strip() + "." if "." in text else text
    except Exception as e:
        return f"(enrichment error: {e})"

