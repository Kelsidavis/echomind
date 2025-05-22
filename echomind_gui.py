import sys
from cognition import launch_background_cognition
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout,
    QLabel, QHBoxLayout, QPushButton, QLineEdit, QGridLayout, QGroupBox, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

# EchoMind internal imports
from dialogue import generate_internal_thought
from responder import generate_response
from self_state import SelfState
from drives import DriveSystem
from memory_system import ShortTermMemory
from trait_engine import TraitEngine
from goal_tracker import GoalTracker
from PyQt5.QtWidgets import QFileDialog

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
        self.setTerminationEnabled(True)  # Ensures safe shutdown
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
        from semantic_lexicon import language
        if language.reflects_value(self.user_input, "growth"):
            goals.add_goal("expand my understanding", motivation="value-aligned")
        if language.reflects_value(self.user_input, "connection"):
            goals.add_goal("deepen relationships", motivation="value-aligned")
        self_state.update_mood_from_context(self.user_input, self.memory_context)
        from semantic_lexicon import language
        lexicon_affinity = language.get_affinity_score(self.user_input)
        if lexicon_affinity > 0.5:
            self_state.set_mood("inspired")
        elif lexicon_affinity < -0.5:
            self_state.set_mood("conflicted")
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

class EchoMindGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 EchoMind: Live Cognition")
        self.setGeometry(100, 100, 1000, 750)
        self.init_ui()

    def init_ui(self):
        self.speak_freely_timer = QTimer()
        self.speak_freely_timer.timeout.connect(self.animate_speak_freely)
        self.speak_freely_pulse = False
        self.speak_freely_timer.start(1000)
        self.thinking_label = QLabel("")
        self.thinking_label.setStyleSheet("color: #ffaa00; font-weight: bold; padding: 4px;")
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.main_tab = QWidget()
        self.dream_tab = QWidget()
        self.tabs.addTab(self.main_tab, "💬 Cognition")
        self.tabs.addTab(self.dream_tab, "💭 Dream Log")
        self.ebook_tab = QWidget()
        self.tabs.addTab(self.ebook_tab, "📘 Ebook Ingestion")

        layout = QVBoxLayout()

        # User/Response Log
        log_layout = QHBoxLayout()

        self.user_log = QTextEdit()
        self.user_log.setReadOnly(True)
        self.user_log.setStyleSheet("background-color: #121212; color: #61afef;")

        self.response_log = QTextEdit()
        self.thought_feed = QTextEdit()
        self.thought_feed.setReadOnly(True)
        self.thought_feed.setStyleSheet("background-color: #1e1e1e; font-style: italic;")
        self.thought_feed.setTextColor(Qt.gray)

        # Visibility toggles
        self.show_dreams = True
        self.show_reflections = True
        self.show_thoughts = True
        self.response_log.setReadOnly(True)
        self.response_log.setStyleSheet("background-color: #121212; color: #e06c75; font-size: 14pt;")

        log_layout.addWidget(self.user_log, 1)
        log_layout.addWidget(self.response_log, 1)
        layout.addLayout(log_layout)
        layout.addWidget(QLabel("[Internal Thought Stream]"))
        layout.addWidget(self.thought_feed)
        layout.addWidget(self.thinking_label)

        # User Input
        input_box = QGroupBox("👤 User Input")
        input_layout = QVBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setFixedHeight(40)
        self.user_input.returnPressed.connect(self.handle_input)
        self.goal_timer = QTimer()
        self.goal_timer.timeout.connect(self.update_goal_display)
        self.goal_timer.start(6000)
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.handle_input)
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.submit_button)
        input_box.setLayout(input_layout)
        layout.addWidget(input_box)

        # Status Grid
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
        layout.addWidget(status_box)

        # Display current goals
        self.goal_display = QTextEdit()
        self.goal_display.setReadOnly(True)
        self.goal_display.setStyleSheet("background-color: #1e1e1e; color: #ffe066; font-style: italic;")
        layout.addWidget(QLabel("[Current Goals]"))
        layout.addWidget(self.goal_display)
        self.update_goal_display()

        self.cog_flow = QLabel("🔁 Cognition Flow: input ➜ memory ➜ traits ➜ LLM ➜ output")
        layout.addWidget(self.cog_flow)

        self.main_tab.setLayout(layout)

        # Dream tab setup
        self.dream_log = QTextEdit()
        self.dream_log.setReadOnly(True)
        self.dream_log.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0;")
        dream_layout = QVBoxLayout()
        dream_layout.addWidget(self.dream_log)
        self.dream_tab.setLayout(dream_layout)

        # Ebook ingestion tab setup
        self.ebook_display = QTextEdit()
        self.ebook_display.setReadOnly(True)
        self.ebook_display.setStyleSheet("background-color: #1e1e1e; color: #a0c0ff;")
        from PyQt5.QtWidgets import QFileDialog

        self.load_book_button = QPushButton("Load Book")
        self.load_book_button.clicked.connect(self.load_ebook)
        ebook_layout = QVBoxLayout()
        ebook_layout.addWidget(self.load_book_button)
        ebook_layout.addWidget(self.ebook_display)
        self.ebook_tab.setLayout(ebook_layout)

        # Dream log streaming
        self.dream_timer = QTimer()
        self.dream_timer.timeout.connect(self.update_dream_log)
        self.dream_timer.start(3000)

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # Cognition animation timer
        self.cog_stage = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_cognition_flow)
        self.timer.start(1200)

    def animate_speak_freely(self):
        if self.thinking_label.text().startswith("💡 Independent Thought"):
            self.speak_freely_pulse = not self.speak_freely_pulse
            self.thinking_label.setStyleSheet("color: #ffaa00; font-weight: bold; padding: 4px;" + (" background-color: #333;" if self.speak_freely_pulse else ""))
        else:
            self.thinking_label.setStyleSheet("color: #ffaa00; font-weight: bold; padding: 4px;")


    def animate_cognition_flow(self):
        stages = ["input", "memory", "traits", "LLM", "output"]
        animated = ["➜" if i == self.cog_stage else "→" for i in range(5)]
        self.cog_flow.setText(f"🔁 Cognition Flow: {animated[0]} input {animated[1]} memory {animated[2]} traits {animated[3]} LLM {animated[4]} output")
        self.cog_stage = (self.cog_stage + 1) % 5

    def update_dream_log(self):
        try:
            with open("logs/dreams.log", "r", encoding="utf-8") as f:
                content = f.read()
                self.dream_log.setPlainText(content)
                self.dream_log.moveCursor(QTextCursor.End)
        except FileNotFoundError:
            self.dream_log.setPlainText("No dreams logged yet.")

    def handle_input(self):
        self.thinking_label.setText("🤔 Thinking...")
        text = self.user_input.text()
        if text:
            state_dict = self_state.get_state()
            drive_dict = drives.get_state()
            memory_context = memory.get_context()

            self.worker = CognitionWorker(text, state_dict, drive_dict, memory_context)
            self.worker.setTerminationEnabled(True)  # Thread termination safety
            self.worker.result_ready.connect(self.display_results)
            self.worker.start()

    def load_ebook(self):
        from llm_interface import generate_from_context
        from semantic_lexicon import language
        path, _ = QFileDialog.getOpenFileName(self, "Select Ebook", "", "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.ebook_display.setPlainText(content)

                    # Enrich lexicon from ebook
                    self.thought_feed.append("[REFLECTION] Reading this book is helping me grow my understanding.")
                    paragraphs = content.split("\n\n")

                    for i, paragraph in enumerate(paragraphs[:5]):
                        if paragraph.strip():
                            result = generate_from_context("Reflect on the values or emotions in this passage:", paragraph.strip())
                            language.learn_from_text(result, source="ebook")
                            self.thought_feed.append(f"[THOUGHT] {result}")
            except Exception as e:
                self.ebook_display.setPlainText(f"Error loading book: {e}")


    def update_goal_display(self):
        goal_texts = [g['description'] for g in goals.get_active_goals()]
        self.goal_display.setPlainText("\n".join(goal_texts) if goal_texts else "No active goals.")


    def display_results(self, internal_thought, response):
        if '[DREAM]' in internal_thought:
            self.thought_feed.setTextColor(Qt.lightGray)
        elif '[REFLECTION]' in internal_thought:
            self.thought_feed.setTextColor(Qt.green)
        elif '[THOUGHT]' in internal_thought:
            self.thought_feed.setTextColor(Qt.magenta)
        else:
            self.thought_feed.setTextColor(Qt.gray)
        if ('[DREAM]' in internal_thought and self.show_dreams) or \
           ('[REFLECTION]' in internal_thought and self.show_reflections) or \
           ('[THOUGHT]' in internal_thought and self.show_thoughts) or \
           ('[' not in internal_thought):
            self.thought_feed.append(f"{internal_thought}")
        self.thinking_label.setText("")
        self.user_log.append(f"{self.user_input.text()}")
        self.response_log.append(f"{response}")
        self.user_input.clear()
        self.user_log.moveCursor(QTextCursor.End)
        self.response_log.moveCursor(QTextCursor.End)

if __name__ == '__main__':
    launch_background_cognition()
    app = QApplication(sys.argv)
    gui = EchoMindGUI()
    gui.show()
    sys.exit(app.exec_())

