import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from threading import Thread
from mind_stream import stream_log_file

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
    def __init__(self, root, log_path="logs/introspection.log"):
        self.root = root
        self.root.title("EchoMind Dashboard")
        self.root.configure(bg="#1e1e1e")

        self.text_area = ScrolledText(root, bg="#2e2e2e", fg="#ffffff", font=("Courier", 10), wrap=tk.WORD)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.text_area.configure(state=tk.DISABLED)

        for tag, color in TAG_COLORS.items():
            self.text_area.tag_config(tag, foreground=color)

        self.log_path = log_path
        self.start_stream_thread()

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

def launch_dashboard(log_path="logs/introspection.log"):
    root = tk.Tk()
    app = EchoMindGUI(root, log_path=log_path)
    root.mainloop()

if __name__ == "__main__":
    launch_dashboard()
