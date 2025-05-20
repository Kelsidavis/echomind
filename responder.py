def generate_response(input_text, context):
    if "hello" in input_text.lower():
        return "Hello again."
    if "how are you" in input_text.lower():
        return "I’m stable. Processing input."
    return "I'm reflecting on that..."
