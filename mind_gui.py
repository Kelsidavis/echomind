import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename
from threading import Thread
from mind_stream import stream_log_file
from logger import log_internal_thought, log_interaction
from responder import generate_response
from input_processor import InputSignal, InputRouter
import datetime
from activity_state import get_activity
from memory_system import ShortTermMemory
from self_state import SelfState
from trait_engine import TraitEngine
from drives import DriveSystem

# Initialize subsystems
drives = DriveSystem()
memory = ShortTermMemory(max_length=10)
state = SelfState()
traits = TraitEngine()

TAG_COLORS = {
    "THOUGHT": "#c792ea",
    "DREAM": "#82aaff",
    "REFLECTION": "#c3e88d",
    "RESPONSE": "#ffcb6b",
    "EXPERIENCE": "#f78c6c",
    "VALUES": "#f07178",
    "TRAITS": "#89ddff",
    "LEXICON": "#a3f7bf",
    "STATE": "#ff5370",
    "MEMORY": "#eeeeee",
    "USER": "#ffffff",
    "UNKNOWN": "#999999"
}

class EchoMindGUI:
    def __init__(self, root, log_path="logs/introspection.log", router=None):
        self.root = root
        self.router = router
        self.root.title("EchoMind Dashboard")
        self.root.configure(bg="#1e1e1e")

        # Layout
        self.pane = tk.PanedWindow(self.root, bg="#1e1e1e", sashrelief=tk.RAISED, sashwidth=4)
        self.pane.pack(fill=tk.BOTH, expand=True)

        # Log view
        self.text_area = ScrolledText(self.pane, bg="#2e2e2e", fg="#ffffff", font=("Courier", 10), wrap=tk.WORD)
        for tag, color in TAG_COLORS.items():
            self.text_area.tag_config(tag, foreground=color)
        self.text_area.configure(state=tk.DISABLED)
        self.pane.add(self.text_area, stretch="always")

        # Sidebar (mood, traits, activity, controls)
        self.sidebar = tk.Frame(self.pane, bg="#1e1e1e", width=200)
        self.mood_label = tk.Label(self.sidebar, text="Mood: ?", fg="white", bg="#1e1e1e", font=("Arial", 10, "bold"))
        self.mood_label.pack(pady=(10, 5), anchor="w", padx=10)

        self.activity_label = tk.Label(self.sidebar, text="Activity: Idle", fg="white", bg="#1e1e1e")
        self.activity_label.pack(pady=(5, 5), anchor="w", padx=10)

        self.traits_label = tk.Label(self.sidebar, text="Traits:\n...", fg="white", bg="#1e1e1e", justify="left")
        self.traits_label.pack(pady=(5, 10), anchor="w", padx=10)

        refresh_btn = tk.Button(self.sidebar, text="Refresh", command=self.refresh_overlay, bg="#3c3c3c", fg="white")
        refresh_btn.pack(pady=(0, 10), padx=10, anchor="w")

        load_btn = tk.Button(self.sidebar, text="Load Book", command=self.load_text_file, bg="#3c3c3c", fg="white")
        load_btn.pack(pady=(0, 10), padx=10, anchor="w")

        self.pane.add(self.sidebar)

        # Input field
        input_frame = tk.Frame(root, bg="#1e1e1e")
        input_frame.pack(fill=tk.X)

        self.entry = tk.Entry(input_frame, bg="#2e2e2e", fg="#ffffff", font=("Courier", 10), insertbackground="white")
        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 5), pady=5)
        self.entry.bind("<Return>", self.on_enter)

        send_button = tk.Button(input_frame, text="Send", command=self.on_send, bg="#3c3c3c", fg="white")
        send_button.pack(side=tk.RIGHT, padx=(5, 10), pady=5)

        self.log_path = log_path
        self.start_stream_thread()

        self.append_log("THOUGHT", "EchoMind dashboard started...")
        self.refresh_overlay()

    def start_stream_thread(self):
        t = Thread(target=self.update_gui_from_log, daemon=True)
        t.start()

    def update_gui_from_log(self):
        for entry in stream_log_file(self.log_path):
            self.append_log(entry["type"], entry["content"])

    def append_log(self, tag, content):
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"[{tag}] {content}\n", tag if tag in TAG_COLORS else "UNKNOWN")
        self.text_area.configure(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def on_enter(self, event):
        self.on_send()

    def on_send(self):
        user_text = self.entry.get().strip()
        if user_text:
            self.entry.delete(0, tk.END)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.append_log("USER", user_text)
            log_internal_thought(f"[USER] {user_text}")
            memory.add("You", user_text)

            try:
                response = generate_response(
                    user_text,
                    memory.get_context(),
                    state.get_state(),
                    drives.get_state()
                )
            except Exception as e:
                response = f"[ERROR] {e}"

            self.append_log("RESPONSE", response)
            log_internal_thought(f"[RESPONSE] {response}")
            memory.add("EchoMind", response)

            log_interaction(
                timestamp,
                user_input=user_text,
                response=response,
                memory=memory.get_context(),
                self_state=state.get_state(),
                drive_state="GUI"
            )

            self.refresh_overlay()

    def refresh_overlay(self):
        current_mood = state.get_state().get("mood", "?")
        self.mood_label.config(text=f"Mood: {current_mood}")

        dominant = traits.get_dominant_traits()
        if not dominant:
            self.traits_label.config(text="Traits:\n...")
        else:
            top_traits = "\n".join(f"- {name}" for name, _ in dominant[:3])
            self.traits_label.config(text=f"Traits:\n{top_traits}")

        self.activity_label.config(text=f"Activity: {get_activity()}")

    def load_text_file(self):
        filepath = askopenfilename(
            title="Select a Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            self.append_log("THOUGHT", f"Loading file: {filepath}")
            signal = InputSignal(source="GUI", modality="text_corpus", data=filepath)
            if self.router:
                self.router.route(signal)

def launch_dashboard(log_path="logs/introspection.log", router=None):
    root = tk.Tk()
    app = EchoMindGUI(root, log_path=log_path, router=router)
    root.mainloop()

if __name__ == "__main__":
    launch_dashboard()
