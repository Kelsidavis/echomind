from transformers import AutoTokenizer, AutoModelForCausalLM

# Smaller and faster model
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")

def generate_from_context(prompt: str, lexicon_context: str, max_tokens=100) -> str:
    input_text = f"{lexicon_context}\n\nQ: {prompt}\nA:"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=1024)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.8,
        top_k=50,
        top_p=0.95,
        pad_token_id=tokenizer.eos_token_id
    )

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
        if len(clean_lines) >= 1:  # Only the first clean line
            break

    return clean_lines[0] if clean_lines else "(no response)"