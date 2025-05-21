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

    # Decode the generated text
    full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Trim the input prompt portion
    if "A:" in full_output:
        result = full_output.split("A:")[-1].strip()
    else:
        result = full_output.strip()

    # Filter out repeated lines and return up to 2 meaningful lines
    seen = set()
    final_lines = []
    for line in result.splitlines():
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            final_lines.append(line)
        if len(final_lines) >= 2:
            break

    return " ".join(final_lines).strip()
