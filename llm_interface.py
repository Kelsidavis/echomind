from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from config import ACTIVE_LLM_MODEL as MODEL_NAME  # Config-driven model switch

# Load tokenizer and model using the active model name
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

def generate_from_context(prompt: str, lexicon_context: str, max_tokens=100) -> str:
    input_text = f"{lexicon_context}\n\nQ: {prompt}\nA:"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    try:
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.8,
            top_k=50,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
    except RuntimeError as e:
        return f"(model error: {e})"

    full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Trim the prompt portion
    result = full_output.split("A:")[-1] if "A:" in full_output else full_output

    # Clean and filter hallucinated lines
    clean_lines = []
    seen = set()
    for line in result.strip().splitlines():
        line = line.strip()
        if not line or line in seen:
            continue
        seen.add(line)
        if line.startswith(("Q:", "A:", "B:", "User said:", "- ", "In response", "EchoMind:", "[")):
            continue
        if len(line) < 3:
            continue
        clean_lines.append(line)
        if len(clean_lines) >= 1:
            break

    # Final trim: return only the first sentence from the clean line
    if clean_lines:
        sentence = clean_lines[0]
        if '.' in sentence:
            sentence = sentence.split('.')[0] + '.'
        return sentence.strip()

    return "(no response)"

