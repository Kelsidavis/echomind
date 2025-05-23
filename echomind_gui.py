import sys
from cognition import launch_background_cognition, get_cognition_engine, search_current_info, get_world_context, get_world_insights
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout,
    QLabel, QHBoxLayout, QPushButton, QLineEdit, QGridLayout, QGroupBox, QTabWidget,
    QFileDialog, QProgressBar, QCheckBox, QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QFont, QColor

# EchoMind internal imports
from dialogue import generate_internal_thought
from responder import generate_response
from self_state import SelfState
from drives import DriveSystem
from memory_system import ShortTermMemory
from trait_engine import TraitEngine
from goal_tracker import GoalTracker

# Enhanced EBook Integration
try:
    from enhanced_ebook_gui import integrate_enhanced_ebook_gui
    ENHANCED_EBOOK_AVAILABLE = True
except ImportError:
    ENHANCED_EBOOK_AVAILABLE = False
    print("⚠️ Enhanced ebook GUI not available")

# Initialize cognitive state
self_state = SelfState()
drives = DriveSystem()
memory = ShortTermMemory(max_length=10)
traits = TraitEngine()
goals = GoalTracker()

class WorldAwarenessWorker(QThread):
    """Background thread for world awareness operations"""
    update_ready = pyqtSignal(str)
    status_ready = pyqtSignal(dict)
    search_ready = pyqtSignal(str)
    
    def __init__(self, operation="status", query=""):
        super().__init__()
        self.operation = operation
        self.query = query
        
    def run(self):
        try:
            if self.operation == "search":
                result = search_current_info(self.query)
                self.search_ready.emit(result)
            elif self.operation == "context":
                context = get_world_context()
                insights = get_world_insights()
                combined = f"🌍 World Context:\n{context}\n\n💡 Current Insights:\n{insights}"
                self.update_ready.emit(combined)
            elif self.operation == "status":
                engine = get_cognition_engine()
                if hasattr(engine, 'world_awareness') and engine.world_awareness:
                    status = engine.world_awareness.get_curiosity_status()
                    self.status_ready.emit(status)
                else:
                    self.status_ready.emit({"status": "unavailable"})
        except Exception as e:
            self.update_ready.emit(f"Error: {e}")

class EbookWorker(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, file_path, ebook_system=None):
        super().__init__()
        self.file_path = file_path
        self.ebook_system = ebook_system

    def run(self):
        try:
            if self.ebook_system:
                # Use advanced ebook system
                result = self.ebook_system.ingest_book(self.file_path)
                if result.get('success'):
                    analysis = result['analysis_summary']
                    response = f"[BOOK ANALYSIS] Successfully analyzed '{result['metadata'].title}'\n"
                    response += f"Found {analysis['characters_found']} characters, {analysis['themes_identified']} themes, "
                    response += f"and {analysis['quotes_extracted']} significant quotes.\n"
                    response += f"Reading level: Grade {result['metadata'].reading_level:.1f}\n"
                    if analysis['genre_hints']:
                        response += f"Genre: {', '.join(analysis['genre_hints'])}"
                else:
                    response = f"[ERROR] {result.get('error', 'Unknown error processing book')}"
            else:
                # Fallback to basic processing
                from enrichment_llm import generate_from_context
                from semantic_lexicon import language
                
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                paragraphs = content.split("\n\n")
                results = []
                for i, paragraph in enumerate(paragraphs[:5]):
                    if paragraph.strip():
                        result = generate_from_context(
                            "Reflect on the values or emotions in this passage:",
                            paragraph.strip()
                        )
                        language.learn_from_text(result, source="ebook")
                        results.append(f"[THOUGHT] {result}")
                
                response = "\n".join(results)
            
            self.result_ready.emit(response)
            
        except Exception as e:
            self.result_ready.emit(f"[ERROR] Failed to process book: {e}")

class CognitionWorker(QThread):
    result_ready = pyqtSignal(str, str)

    def __init__(self, user_input, state_dict, drive_dict, memory_context):
        super().__init__()
        self.setTerminationEnabled(True)
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
        self.setWindowTitle("🧠 EchoMind: Live Cognition + Advanced Systems")
        self.setGeometry(100, 100, 1400, 900)
        self.init_ui()

    def init_ui(self):
        # Timer setup
        self.speak_freely_timer = QTimer()
        self.speak_freely_timer.timeout.connect(self.animate_speak_freely)
        self.speak_freely_pulse = False
        self.speak_freely_timer.start(1000)
        
        self.thinking_label = QLabel("")
        self.thinking_label.setStyleSheet("color: #ffaa00; font-weight: bold; padding: 4px;")
        
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Create tabs
        self.main_tab = QWidget()
        self.dream_tab = QWidget()
        self.ebook_tab = QWidget()
        self.world_tab = QWidget()
        
        self.tabs.addTab(self.main_tab, "💬 Cognition")
        self.tabs.addTab(self.dream_tab, "💭 Dream Log")
        self.tabs.addTab(self.ebook_tab, "📚 Enhanced EBooks")
        self.tabs.addTab(self.world_tab, "🌍 World Awareness")

        # Setup all tabs
        self.setup_main_tab()
        self.setup_dream_tab()
        self.setup_enhanced_ebook_tab()
        self.setup_world_tab()

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # Start timers
        self.start_timers()
        
        # Setup enhanced integrations
        self.setup_enhanced_integrations()

    def setup_enhanced_integrations(self):
        """Setup enhanced ebook and other system integrations"""
        try:
            # Get the cognition engine
            engine = get_cognition_engine()
            
            # Integrate enhanced ebook system if available
            if ENHANCED_EBOOK_AVAILABLE and hasattr(engine, 'ebook_system') and engine.ebook_system:
                # Replace the basic ebook tab with enhanced version
                enhanced_tab = integrate_enhanced_ebook_gui(self, engine.ebook_system)
                if enhanced_tab:
                    # Find and replace the ebook tab
                    for i in range(self.tabs.count()):
                        if "EBooks" in self.tabs.tabText(i) or "Ebook" in self.tabs.tabText(i):
                            self.tabs.removeTab(i)
                            self.tabs.insertTab(i, enhanced_tab, "📚 Advanced EBooks")
                            break
                    print("✅ Enhanced ebook GUI integrated successfully")
                else:
                    print("⚠️ Enhanced ebook integration failed")
            else:
                print("⚠️ Enhanced ebook system not available - using basic tab")
                
        except Exception as e:
            print(f"❌ Enhanced integration error: {e}")

    def setup_main_tab(self):
        """Setup the main cognition tab with world awareness indicators"""
        layout = QVBoxLayout()

        # User/Response Log
        log_layout = QHBoxLayout()

        self.user_log = QTextEdit()
        self.user_log.setReadOnly(True)
        self.user_log.setStyleSheet("background-color: #121212; color: #61afef;")

        self.response_log = QTextEdit()
        self.response_log.setReadOnly(True)
        self.response_log.setStyleSheet("background-color: #121212; color: #e06c75; font-size: 14pt;")

        log_layout.addWidget(self.user_log, 1)
        log_layout.addWidget(self.response_log, 1)
        layout.addLayout(log_layout)

        # Internal Thought Stream
        layout.addWidget(QLabel("[Internal Thought Stream]"))
        self.thought_feed = QTextEdit()
        self.thought_feed.setReadOnly(True)
        self.thought_feed.setStyleSheet("background-color: #1e1e1e; font-style: italic;")
        self.thought_feed.setTextColor(Qt.gray)
        layout.addWidget(self.thought_feed)
        layout.addWidget(self.thinking_label)

        # World Awareness Status Indicator (Enhanced)
        world_status_layout = QHBoxLayout()
        self.world_status_indicator = QLabel("🌍 World: Initializing...")
        self.world_status_indicator.setStyleSheet("color: #87ceeb; font-weight: bold; padding: 2px;")
        
        self.world_knowledge_count = QLabel("Knowledge: 0 fragments")
        self.world_knowledge_count.setStyleSheet("color: #98fb98; font-size: 10pt;")
        
        self.world_curiosity_indicator = QLabel("Curiosity: Awakening")
        self.world_curiosity_indicator.setStyleSheet("color: #ffa500; font-size: 10pt;")
        
        world_status_layout.addWidget(self.world_status_indicator)
        world_status_layout.addWidget(self.world_knowledge_count)
        world_status_layout.addWidget(self.world_curiosity_indicator)
        world_status_layout.addStretch()
        layout.addLayout(world_status_layout)

        # User Input
        input_box = QGroupBox("👤 User Input")
        input_layout = QVBoxLayout()
        
        # Add world search checkbox
        world_input_layout = QHBoxLayout()
        self.world_search_mode = QCheckBox("Include World Search")
        self.world_search_mode.setToolTip("Include current world information in responses")
        world_input_layout.addWidget(self.world_search_mode)
        world_input_layout.addStretch()
        input_layout.addLayout(world_input_layout)
        
        self.user_input = QLineEdit()
        self.user_input.setFixedHeight(40)
        self.user_input.returnPressed.connect(self.handle_input)
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.handle_input)
        
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.submit_button)
        input_box.setLayout(input_layout)
        layout.addWidget(input_box)

        # Status Grid (Enhanced)
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

        # Current Goals Display
        self.goal_display = QTextEdit()
        self.goal_display.setReadOnly(True)
        self.goal_display.setStyleSheet("background-color: #1e1e1e; color: #ffe066; font-style: italic;")
        layout.addWidget(QLabel("[Current Goals]"))
        layout.addWidget(self.goal_display)

        # Cognition Flow Animation
        self.cog_flow = QLabel("🔁 Cognition Flow: input ➜ memory ➜ traits ➜ LLM ➜ output")
        layout.addWidget(self.cog_flow)

        self.main_tab.setLayout(layout)

    def setup_enhanced_ebook_tab(self):
        """Setup enhanced ebook tab (will be replaced if advanced system is available)"""
        layout = QVBoxLayout()
        
        # Enhanced controls
        controls_layout = QHBoxLayout()
        
        self.load_book_button = QPushButton("📖 Load Book (Multi-format)")
        self.load_book_button.clicked.connect(self.load_ebook)
        self.load_book_button.setStyleSheet("background-color: #4a5568; color: white; padding: 8px; font-weight: bold;")
        
        self.book_status_label = QLabel("Ready to analyze books")
        self.book_status_label.setStyleSheet("color: #87ceeb; font-weight: bold;")
        
        controls_layout.addWidget(self.load_book_button)
        controls_layout.addWidget(self.book_status_label)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.book_progress_bar = QProgressBar()
        self.book_progress_bar.setVisible(False)
        layout.addWidget(self.book_progress_bar)
        
        # Enhanced display area
        self.ebook_display = QTextEdit()
        self.ebook_display.setReadOnly(True)
        self.ebook_display.setStyleSheet("background-color: #1e1e1e; color: #a0c0ff; font-family: 'Georgia';")
        self.ebook_display.setPlaceholderText("Enhanced ebook analysis will appear here...\n\nSupported formats: TXT, PDF, EPUB, DOCX, HTML")
        
        layout.addWidget(self.ebook_display)
        
        # Book analysis summary
        analysis_group = QGroupBox("📊 Quick Analysis")
        analysis_layout = QGridLayout()
        
        self.book_word_count = QLabel("Words: -")
        self.book_reading_level = QLabel("Level: -")
        self.book_estimated_time = QLabel("Time: -")
        self.book_genre = QLabel("Genre: -")
        
        analysis_layout.addWidget(QLabel("Word Count:"), 0, 0)
        analysis_layout.addWidget(self.book_word_count, 0, 1)
        analysis_layout.addWidget(QLabel("Reading Level:"), 0, 2)
        analysis_layout.addWidget(self.book_reading_level, 0, 3)
        
        analysis_layout.addWidget(QLabel("Est. Time:"), 1, 0)
        analysis_layout.addWidget(self.book_estimated_time, 1, 1)
        analysis_layout.addWidget(QLabel("Genre:"), 1, 2)
        analysis_layout.addWidget(self.book_genre, 1, 3)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        self.ebook_tab.setLayout(layout)

    def setup_world_tab(self):
        """Setup the dedicated world awareness tab"""
        layout = QVBoxLayout()
        
        # World Status Header
        header_layout = QHBoxLayout()
        header_label = QLabel("🌍 EchoMind's World Awareness System")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #87ceeb; padding: 10px;")
        header_layout.addWidget(header_label)
        
        self.refresh_world_button = QPushButton("🔄 Refresh")
        self.refresh_world_button.clicked.connect(self.refresh_world_data)
        self.refresh_world_button.setStyleSheet("background-color: #2d3748; color: white; padding: 5px;")
        header_layout.addWidget(self.refresh_world_button)
        
        layout.addLayout(header_layout)
        
        # System Status Panel
        status_group = QGroupBox("📊 System Status")
        status_layout = QGridLayout()
        
        self.world_system_status = QLabel("Status: Initializing...")
        self.world_fragments_count = QLabel("Knowledge Fragments: 0")
        self.world_curiosity_topics = QLabel("Active Curiosity Topics: 0")
        self.world_last_update = QLabel("Last Update: Never")
        self.world_background_status = QLabel("Background Process: Unknown")
        
        status_layout.addWidget(QLabel("System:"), 0, 0)
        status_layout.addWidget(self.world_system_status, 0, 1)
        status_layout.addWidget(QLabel("Knowledge:"), 1, 0)
        status_layout.addWidget(self.world_fragments_count, 1, 1)
        status_layout.addWidget(QLabel("Curiosity:"), 2, 0)
        status_layout.addWidget(self.world_curiosity_topics, 2, 1)
        status_layout.addWidget(QLabel("Updated:"), 3, 0)
        status_layout.addWidget(self.world_last_update, 3, 1)
        status_layout.addWidget(QLabel("Background:"), 4, 0)
        status_layout.addWidget(self.world_background_status, 4, 1)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Live Search Panel
        search_group = QGroupBox("🔍 Live World Search")
        search_layout = QVBoxLayout()
        
        search_input_layout = QHBoxLayout()
        self.world_search_input = QLineEdit()
        self.world_search_input.setPlaceholderText("Search current information about...")
        self.world_search_input.returnPressed.connect(self.search_world_info)
        
        self.world_search_button = QPushButton("Search")
        self.world_search_button.clicked.connect(self.search_world_info)
        self.world_search_button.setStyleSheet("background-color: #4a5568; color: white;")
        
        search_input_layout.addWidget(self.world_search_input)
        search_input_layout.addWidget(self.world_search_button)
        search_layout.addLayout(search_input_layout)
        
        self.world_search_results = QTextEdit()
        self.world_search_results.setReadOnly(True)
        self.world_search_results.setStyleSheet("background-color: #1e1e1e; color: #87ceeb; font-family: monospace;")
        self.world_search_results.setPlaceholderText("Search results will appear here...")
        search_layout.addWidget(self.world_search_results)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # World Context and Insights Panel
        context_group = QGroupBox("🌐 Current World Context & Insights")
        context_layout = QVBoxLayout()
        
        self.world_context_display = QTextEdit()
        self.world_context_display.setReadOnly(True)
        self.world_context_display.setStyleSheet("background-color: #1e1e1e; color: #98fb98; font-family: monospace;")
        self.world_context_display.setPlaceholderText("World context and insights will appear here...")
        
        context_buttons_layout = QHBoxLayout()
        self.refresh_context_button = QPushButton("🔄 Refresh Context")
        self.refresh_context_button.clicked.connect(self.refresh_world_context)
        
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh every 30s")
        self.auto_refresh_checkbox.setChecked(True)
        
        context_buttons_layout.addWidget(self.refresh_context_button)
        context_buttons_layout.addWidget(self.auto_refresh_checkbox)
        context_buttons_layout.addStretch()
        
        context_layout.addWidget(self.world_context_display)
        context_layout.addLayout(context_buttons_layout)
        
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
        # Curiosity Explorer Panel
        curiosity_group = QGroupBox("🔬 Autonomous Curiosity Explorer")
        curiosity_layout = QVBoxLayout()
        
        self.curiosity_log = QTextEdit()
        self.curiosity_log.setReadOnly(True)
        self.curiosity_log.setStyleSheet("background-color: #1a1a1a; color: #ffa500; font-family: monospace; font-size: 10pt;")
        self.curiosity_log.setPlaceholderText("EchoMind's autonomous explorations will appear here...")
        self.curiosity_log.setMaximumHeight(150)
        
        curiosity_layout.addWidget(QLabel("Recent Autonomous Explorations:"))
        curiosity_layout.addWidget(self.curiosity_log)
        
        curiosity_group.setLayout(curiosity_layout)
        layout.addWidget(curiosity_group)
        
        self.world_tab.setLayout(layout)

    def setup_dream_tab(self):
        """Setup dream tab"""
        self.dream_log = QTextEdit()
        self.dream_log.setReadOnly(True)
        self.dream_log.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0;")
        dream_layout = QVBoxLayout()
        dream_layout.addWidget(self.dream_log)
        self.dream_tab.setLayout(dream_layout)

    def start_timers(self):
        """Start all timers and background updates"""
        # Goal display timer
        self.goal_timer = QTimer()
        self.goal_timer.timeout.connect(self.update_goal_display)
        self.goal_timer.start(6000)
        
        # Dream log timer
        self.dream_timer = QTimer()
        self.dream_timer.timeout.connect(self.update_dream_log)
        self.dream_timer.start(3000)
        
        # Cognition animation timer
        self.cog_stage = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_cognition_flow)
        self.timer.start(1200)
        
        # World awareness status timer
        self.world_status_timer = QTimer()
        self.world_status_timer.timeout.connect(self.update_world_status)
        self.world_status_timer.start(15000)  # Every 15 seconds
        
        # Auto-refresh world context timer
        self.world_context_timer = QTimer()
        self.world_context_timer.timeout.connect(self.auto_refresh_world_context)
        self.world_context_timer.start(30000)  # Every 30 seconds
        
        # Initial updates
        self.update_goal_display()
        self.update_world_status()
        self.refresh_world_context()

    def animate_speak_freely(self):
        if self.thinking_label.text().startswith("💡 Independent Thought"):
            self.speak_freely_pulse = not self.speak_freely_pulse
            self.thinking_label.setStyleSheet("color: #ffaa00; font-weight: bold; padding: 4px;" + 
                                            (" background-color: #333;" if self.speak_freely_pulse else ""))
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

    def update_world_status(self):
        """Update world awareness status indicators"""
        self.world_worker = WorldAwarenessWorker("status")
        self.world_worker.status_ready.connect(self.display_world_status)
        self.world_worker.start()

    def display_world_status(self, status):
        """Display world awareness status"""
        if status.get("status") == "unavailable":
            self.world_status_indicator.setText("🌍 World: Unavailable")
            self.world_status_indicator.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            return
        
        # Update main tab indicators
        system_status = status.get("status", "unknown")
        knowledge_count = status.get("knowledge_fragments_stored", 0)
        curiosity_count = status.get("active_curiosity_topics", 0)
        
        self.world_status_indicator.setText(f"🌍 World: {system_status.title()}")
        if system_status == "active":
            self.world_status_indicator.setStyleSheet("color: #98fb98; font-weight: bold;")
        else:
            self.world_status_indicator.setStyleSheet("color: #ffa500; font-weight: bold;")
        
        self.world_knowledge_count.setText(f"Knowledge: {knowledge_count} fragments")
        self.world_curiosity_indicator.setText(f"Curiosity: {curiosity_count} topics")
        
        # Update world tab status if it exists
        if hasattr(self, 'world_system_status'):
            self.world_system_status.setText(f"{system_status.title()}")
            self.world_fragments_count.setText(f"{knowledge_count}")
            self.world_curiosity_topics.setText(f"{curiosity_count}")
            self.world_background_status.setText("Active" if status.get("background_active", False) else "Inactive")
            
            last_update = status.get("last_update")
            if last_update:
                self.world_last_update.setText(f"{last_update[:19]}")  # Trim to readable format
            else:
                self.world_last_update.setText("Never")

    def search_world_info(self):
        """Search for world information"""
        query = self.world_search_input.text().strip()
        if not query:
            return
            
        self.world_search_results.append(f"🔍 Searching for: {query}\n")
        self.world_search_input.clear()
        
        # Start search worker
        self.search_worker = WorldAwarenessWorker("search", query)
        self.search_worker.search_ready.connect(self.display_search_results)
        self.search_worker.start()

    def display_search_results(self, results):
        """Display world search results"""
        self.world_search_results.append(f"{results}\n{'='*50}\n")
        self.world_search_results.moveCursor(QTextCursor.End)

    def refresh_world_context(self):
        """Refresh world context and insights"""
        self.context_worker = WorldAwarenessWorker("context")
        self.context_worker.update_ready.connect(self.display_world_context)
        self.context_worker.start()

    def auto_refresh_world_context(self):
        """Auto-refresh world context if enabled"""
        if hasattr(self, 'auto_refresh_checkbox') and self.auto_refresh_checkbox.isChecked():
            self.refresh_world_context()

    def display_world_context(self, context):
        """Display world context and insights"""
        if hasattr(self, 'world_context_display'):
            self.world_context_display.setPlainText(context)
            self.world_context_display.moveCursor(QTextCursor.End)

    def refresh_world_data(self):
        """Refresh all world awareness data"""
        self.update_world_status()
        self.refresh_world_context()

    def handle_input(self):
        self.thinking_label.setText("🤔 Thinking...")
        text = self.user_input.text()
        if text:
            # Check if world search mode is enabled
            if hasattr(self, 'world_search_mode') and self.world_search_mode.isChecked():
                # Add world context hint to the input processing
                self.thought_feed.append(f"[WORLD] Including world context in response...")
            
            state_dict = self_state.get_state()
            drive_dict = drives.get_state()
            memory_context = memory.get_context()

            self.worker = CognitionWorker(text, state_dict, drive_dict, memory_context)
            self.worker.setTerminationEnabled(True)
            self.worker.result_ready.connect(self.display_results)
            self.worker.start()

    def load_ebook(self):
        """Enhanced ebook loading with multi-format support"""
        # Multi-format file dialog
        file_filters = [
            "All Supported (*.txt *.pdf *.epub *.docx *.html *.htm)",
            "Text Files (*.txt)",
            "PDF Files (*.pdf)",
            "EPUB Files (*.epub)",
            "Word Documents (*.docx)",
            "HTML Files (*.html *.htm)",
            "All Files (*)"
        ]
        
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Book File", 
            "", 
            ";;".join(file_filters)
        )
        
        if path:
            try:
                # Show progress
                self.book_progress_bar.setVisible(True)
                self.book_progress_bar.setValue(0)
                self.book_status_label.setText("Processing book...")
                self.load_book_button.setEnabled(False)
                
                # Get ebook system from cognition engine
                engine = get_cognition_engine()
                ebook_system = getattr(engine, 'ebook_system', None)
                
                # Start enhanced processing
                self.ebook_worker = EbookWorker(path, ebook_system)
                self.ebook_worker.result_ready.connect(self.display_ebook_results)
                self.ebook_worker.start()
                
            except Exception as e:
                self.ebook_display.setPlainText(f"Error loading book: {e}")
                self.book_status_label.setText("Error occurred")
                self.load_book_button.setEnabled(True)
                self.book_progress_bar.setVisible(False)

    def display_ebook_results(self, results):
        """Display enhanced ebook processing results"""
        self.book_progress_bar.setVisible(False)
        self.load_book_button.setEnabled(True)
        self.book_status_label.setText("✅ Analysis complete!")
        
        self.ebook_display.setPlainText(results)
        self.ebook_display.moveCursor(QTextCursor.End)
        
        # Add to thought feed
        self.thought_feed.append("[BOOK] Enhanced book analysis completed with character, theme, and emotional insights.")

    def update_goal_display(self):
        goal_texts = [g['description'] for g in goals.get_active_goals()]
        self.goal_display.setPlainText("\n".join(goal_texts) if goal_texts else "No active goals.")

    def append_ebook_reflections(self, reflections):
        self.thought_feed.append(reflections)

    def display_results(self, internal_thought, response):
        # Set text color based on thought type
        if '[DREAM]' in internal_thought:
            self.thought_feed.setTextColor(Qt.lightGray)
        elif '[REFLECTION]' in internal_thought:
            self.thought_feed.setTextColor(Qt.green)
        elif '[THOUGHT]' in internal_thought:
            self.thought_feed.setTextColor(Qt.magenta)
        elif '[WORLD]' in internal_thought:
            self.thought_feed.setTextColor(Qt.cyan)
        elif '[BOOK]' in internal_thought:
            self.thought_feed.setTextColor(Qt.yellow)
        else:
            self.thought_feed.setTextColor(Qt.gray)
            
        # Display internal thought
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
