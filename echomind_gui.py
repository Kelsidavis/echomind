import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout,
    QLabel, QHBoxLayout, QPushButton, QLineEdit, QGridLayout, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# EchoMind internal imports
from dialogue import generate_internal_thought
from responder import generate_response
from self_state import SelfState
from drives import DriveSystem
from memory_system import ShortTermMemory
from trait_engine import TraitEngine
from goal_tracker import GoalTracker

# Initialize cognitive state
self_state = SelfState()
drives = DriveSystem()
memory = ShortTermMemory(max_length=10)
traits = TraitEngine()
goals = GoalTracker()

class CognitionWorker(QThread):
    result_ready = pyqtSignal(str, str)

    def __init__(self, user_input, state_dict, drive_dict, memory_context):
        super().__init__()
        self.user_input = user_input
        self.state_dict = state_dict
        self.drive_dict = drive_dict
        self.memory_context = memory_context

    def run(self):
        from self_model import SelfModel
        self_model = SelfModel()
        # Real cognitive updates
        traits.update_from_interaction(self.user_input)
        goals.update_progress(self.user_input)
        self_state.update_mood_from_context(self.user_input, self.memory_context)
        drives.update_from_context(self.user_input)

        new_mood = self_state.get_state().get("mood", "neutral")
        new_confidence = self_state.get_state().get("confidence", 0.5)
        new_goal = drives.get_state().get("active_goal", "reflect")

        internal_thought = generate_internal_thought({
            "mood": new_mood,
            "confidence": new_confidence
        }, {
            "active_goal": new_goal
        }, recent_user_input=self.user_input)

        response = generate_response(
            self.user_input,
            self.memory_context,
            self.state_dict,
            self.drive_dict
        )

        memory.add("You", self.user_input)
        memory.add("EchoMind", response)

        self_model.update(mood=new_mood, goal=new_goal, memory_context=self.memory_context)
        self.result_ready.emit(internal_thought, response)

class SynapseGraph(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Cognitive Load")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Interaction")
        self.ax.set_ylabel("Load %")
        super().__init__(self.fig)
        self.load_history = []

    def update_graph(self, value):
        self.load_history.append(value)
        if len(self.load_history) > 20:
            self.load_history.pop(0)
        self.ax.clear()
        self.ax.set_ylim(0, 100)
        self.ax.set_title("Cognitive Load")
        self.ax.set_xlabel("Interaction")
        self.ax.set_ylabel("Load %")
        self.ax.plot(self.load_history, color="cyan")
        self.draw()

class EchoMindGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 EchoMind: Live Cognition")
        self.setGeometry(100, 100, 1000, 750)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top: User Input and Thought Feed
        top_layout = QHBoxLayout()

        # User Input
        input_box = QGroupBox("👤 User Input")
        input_layout = QVBoxLayout()
        self.user_input = QLineEdit()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.handle_input)
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.submit_button)
        input_box.setLayout(input_layout)

        # Thought Feed
        thought_box = QGroupBox("🔍 Internal Thought & Reflection")
        self.thought_feed = QTextEdit()
        self.thought_feed.setReadOnly(True)
        self.thought_feed.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0;")
        thought_layout = QVBoxLayout()
        thought_layout.addWidget(self.thought_feed)
        thought_box.setLayout(thought_layout)

        top_layout.addWidget(input_box, 1)
        top_layout.addWidget(thought_box, 2)

        # Synapse Graph Widget
        self.synapse_chart = SynapseGraph()
        layout.addWidget(self.synapse_chart)

        # Middle: Status Grid
        status_layout = QGridLayout()
        self.mood_label = QLabel("Mood: Reflective")
        self.goal_label = QLabel("Goal: Understand")
        self.memory_label = QLabel("Memory: 3 active")
        self.dream_label = QLabel("Last Dream: ✨")

        status_layout.addWidget(self.mood_label, 0, 0)
        status_layout.addWidget(self.goal_label, 0, 1)
        status_layout.addWidget(self.memory_label, 1, 0)
        status_layout.addWidget(self.dream_label, 1, 1)

        status_box = QGroupBox("🧬 Trait | 🎯 Goal | 🕰 Memory | 💭 Dream")
        status_box.setLayout(status_layout)

        # Bottom: Cognition Flow
        self.cog_flow = QLabel("🔁 Cognition Flow: input ➜ memory ➜ traits ➜ LLM ➜ output")
        self.output_display = QLabel("🧾 Output will appear here.")
        self.output_display.setWordWrap(True)
        self.output_display.setStyleSheet("font-weight: bold; margin-top: 10px;")

        layout.addLayout(top_layout)
        layout.addWidget(status_box)
        layout.addWidget(self.cog_flow)
        layout.addWidget(self.output_display)

        self.setLayout(layout)

        # Timer for updating cognition animation
        self.cog_stage = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_cognition_flow)
        self.timer.start(1200)

    def animate_cognition_flow(self):
        stages = ["input", "memory", "traits", "LLM", "output"]
        animated = ["➜" if i == self.cog_stage else "→" for i in range(5)]
        self.cog_flow.setText(f"🔁 Cognition Flow: {animated[0]} input {animated[1]} memory {animated[2]} traits {animated[3]} LLM {animated[4]} output")
        self.cog_stage = (self.cog_stage + 1) % 5

    def handle_input(self):
        text = self.user_input.text()
        if text:
            state_dict = self_state.get_state()
            drive_dict = drives.get_state()
            memory_context = memory.get_context()

            cognitive_load = int(min(100, (state_dict.get("confidence", 0.5) + drive_dict.get("engagement", 0.5)) * 50))
            self.synapse_chart.update_graph(cognitive_load)

            self.worker = CognitionWorker(text, state_dict, drive_dict, memory_context)
            self.worker.result_ready.connect(self.display_results)
            self.worker.start()

    def display_results(self, internal_thought, response):
        self.thought_feed.append(f"[Internal Thought] {internal_thought}")
        self.output_display.setText(f"🧾 EchoMind: {response}")
        self.user_input.clear()
        self.thought_feed.moveCursor(QTextCursor.End)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = EchoMindGUI()
    gui.show()
    sys.exit(app.exec_())

