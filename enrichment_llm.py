# enrichment_llm.py
#
# This module runs a **lightweight CPU-based language model** (GPT-Neo 125M) to parallelize:
# - Lexicon enrichment
# - Value inference from ebooks or logs
# - Background contextual annotation
#
# It complements the main LLM in `llm_interface.py` by offloading auxiliary tasks
# and enabling semantic growth without blocking core cognitive threads.



from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "EleutherAI/gpt-neo-125M"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    device_map={"": "cpu"}  # force CPU to keep it light
)

def generate_from_context(prompt: str, context: str = "", max_tokens=80, context_type=None) -> str:
    if context_type:
        print(f"[warning] enrichment_llm ignoring context_type='{context_type}'")
    input_text = f"{context.strip()}\nQ: {prompt}\nA:" if context else f"Q: {prompt}\nA:"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.7,
        top_k=40,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id
    )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = decoded.split("A:")[-1].strip()
    return answer.split(".")[0].strip() + "." if "." in answer else answer

