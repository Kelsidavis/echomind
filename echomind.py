from input_processor import InputSignal, InputRouter
from cognition import launch_background_cognition
from mind_gui import launch_dashboard

input_router = InputRouter()

# Register default text input handler
def handle_text_input(signal):
    print("[Input] EchoMind received:", signal.data)
    # You can expand this logic or route it elsewhere if needed

input_router.register("text", handle_text_input)

if __name__ == "__main__":
    print("EchoMind v0.16 | Launching GUI with cognition enabled...")
    launch_background_cognition()
    launch_dashboard(router=input_router)

