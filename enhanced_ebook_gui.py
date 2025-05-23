"""
Enhanced EBook GUI for EchoMind - Full Featured Version
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, 
    QPushButton, QFileDialog, QProgressBar, QListWidget, 
    QTabWidget, QGroupBox, QGridLayout, QLineEdit, QComboBox,
    QScrollArea, QFrame, QCheckBox, QSpinBox, QTextBrowser,
    QListWidgetItem, QMessageBox, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCharFormat, QPixmap
import json
import datetime
from pathlib import Path

class AdvancedEbookWorker(QThread):
    """Background thread for advanced ebook processing"""
    
    progress_update = pyqtSignal(str, int)
    analysis_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path, ebook_system):
        super().__init__()
        self.file_path = file_path
        self.ebook_system = ebook_system
        
    def run(self):
        try:
            self.progress_update.emit("Extracting content from file...", 10)
            result = self.ebook_system.ingest_book(self.file_path)
            
            if 'error' in result:
                self.error_occurred.emit(result['error'])
                return
            
            self.progress_update.emit("Analysis complete!", 100)
            self.analysis_complete.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class BookDiscussionWorker(QThread):
    """Background thread for book discussions"""
    
    response_ready = pyqtSignal(str)
    
    def __init__(self, book_id, question, ebook_system):
        super().__init__()
        self.book_id = book_id
        self.question = question
        self.ebook_system = ebook_system
        
    def run(self):
        try:
            response = self.ebook_system.ask_about_book(self.book_id, self.question)
            self.response_ready.emit(response)
        except Exception as e:
            self.response_ready.emit(f"Error processing question: {e}")

class EnhancedEbookTab(QWidget):
    """Enhanced ebook tab with comprehensive features"""
    
    def __init__(self, ebook_system=None):
        super().__init__()
        self.ebook_system = ebook_system
        self.current_book_id = None
        self.current_analysis = None
        
        self.init_ui()
        self.setup_timers()
        
    def init_ui(self):
        """Initialize the comprehensive ebook interface"""
        layout = QVBoxLayout()
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Library and controls
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel - Analysis and discussion
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        
        layout.addWidget(main_splitter)
        self.setLayout(layout)
        
    def create_left_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # File loading section
        load_group = QGroupBox("📚 Load New Book")
        load_layout = QVBoxLayout()
        
        # Format support status
        self.format_status = QLabel("Checking supported formats...")
        self.format_status.setStyleSheet("color: #87ceeb; font-size: 10pt;")
        load_layout.addWidget(self.format_status)
        
        # Load button
        self.load_button = QPushButton("📖 Select Book File")
        self.load_button.clicked.connect(self.load_book_file)
        self.load_button.setStyleSheet("background-color: #4a5568; color: white; padding: 8px; font-weight: bold;")
        load_layout.addWidget(self.load_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        load_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ffa500; font-weight: bold;")
        load_layout.addWidget(self.status_label)
        
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)
        
        # Library section
        library_group = QGroupBox("📋 My Library")
        library_layout = QVBoxLayout()
        
        # Library list
        self.library_list = QListWidget()
        self.library_list.itemClicked.connect(self.select_book_from_library)
        self.library_list.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #444;")
        library_layout.addWidget(self.library_list)
        
        # Library controls
        library_controls = QHBoxLayout()
        
        self.refresh_library_btn = QPushButton("🔄")
        self.refresh_library_btn.clicked.connect(self.refresh_library)
        self.refresh_library_btn.setMaximumWidth(40)
        
        self.compare_books_btn = QPushButton("⚖️ Compare")
        self.compare_books_btn.clicked.connect(self.compare_selected_books)
        self.compare_books_btn.setEnabled(False)
        
        library_controls.addWidget(self.refresh_library_btn)
        library_controls.addWidget(self.compare_books_btn)
        library_controls.addStretch()
        
        library_layout.addLayout(library_controls)
        library_group.setLayout(library_layout)
        layout.addWidget(library_group)
        
        # Current book info
        self.book_info_group = QGroupBox("📖 Current Book")
        book_info_layout = QVBoxLayout()
        
        self.book_title_label = QLabel("No book selected")
        self.book_title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.book_title_label.setStyleSheet("color: #61afef;")
        
        self.book_details = QTextEdit()
        self.book_details.setMaximumHeight(150)
        self.book_details.setReadOnly(True)
        self.book_details.setStyleSheet("background-color: #1a1a1a; color: #cccccc; border: 1px solid #444;")
        
        book_info_layout.addWidget(self.book_title_label)
        book_info_layout.addWidget(self.book_details)
        
        self.book_info_group.setLayout(book_info_layout)
        layout.addWidget(self.book_info_group)
        
        # Reading progress
        progress_group = QGroupBox("📊 Reading Progress")
        progress_layout = QVBoxLayout()
        
        self.reading_progress_bar = QProgressBar()
        self.reading_progress_label = QLabel("Not started")
        
        progress_layout.addWidget(self.reading_progress_bar)
        progress_layout.addWidget(self.reading_progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
        
    def create_right_panel(self):
        """Create the right analysis panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Analysis tabs
        self.analysis_tabs = QTabWidget()
        
        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.analysis_tabs.addTab(self.overview_tab, "📋 Overview")
        
        # Characters tab
        self.characters_tab = self.create_characters_tab()
        self.analysis_tabs.addTab(self.characters_tab, "👥 Characters")
        
        # Themes tab
        self.themes_tab = self.create_themes_tab()
        self.analysis_tabs.addTab(self.themes_tab, "🎭 Themes")
        
        # Emotional arc tab
        self.emotions_tab = self.create_emotions_tab()
        self.analysis_tabs.addTab(self.emotions_tab, "💫 Emotions")
        
        # Quotes tab
        self.quotes_tab = self.create_quotes_tab()
        self.analysis_tabs.addTab(self.quotes_tab, "💬 Quotes")
        
        # Discussion tab
        self.discussion_tab = self.create_discussion_tab()
        self.analysis_tabs.addTab(self.discussion_tab, "🗣️ Discussion")
        
        # Journal tab
        self.journal_tab = self.create_journal_tab()
        self.analysis_tabs.addTab(self.journal_tab, "📔 Journal")
        
        layout.addWidget(self.analysis_tabs)
        panel.setLayout(layout)
        return panel
    
    def create_overview_tab(self):
        """Create book overview tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Basic stats
        stats_group = QGroupBox("📊 Book Statistics")
        stats_layout = QGridLayout()
        
        self.stats_labels = {
            'word_count': QLabel("0"),
            'reading_level': QLabel("0.0"),
            'estimated_time': QLabel("0 min"),
            'chapters': QLabel("0"),
            'characters_found': QLabel("0"),
            'themes_found': QLabel("0"),
            'quotes_extracted': QLabel("0")
        }
        
        stats_layout.addWidget(QLabel("Word Count:"), 0, 0)
        stats_layout.addWidget(self.stats_labels['word_count'], 0, 1)
        stats_layout.addWidget(QLabel("Reading Level:"), 0, 2)
        stats_layout.addWidget(self.stats_labels['reading_level'], 0, 3)
        
        stats_layout.addWidget(QLabel("Est. Time:"), 1, 0)
        stats_layout.addWidget(self.stats_labels['estimated_time'], 1, 1)
        stats_layout.addWidget(QLabel("Chapters:"), 1, 2)
        stats_layout.addWidget(self.stats_labels['chapters'], 1, 3)
        
        stats_layout.addWidget(QLabel("Characters:"), 2, 0)
        stats_layout.addWidget(self.stats_labels['characters_found'], 2, 1)
        stats_layout.addWidget(QLabel("Themes:"), 2, 2)
        stats_layout.addWidget(self.stats_labels['themes_found'], 2, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Genre and style
        style_group = QGroupBox("🎨 Writing Style & Genre")
        style_layout = QVBoxLayout()
        
        self.genre_label = QLabel("Genre hints: Not analyzed")
        self.style_description = QTextEdit()
        self.style_description.setMaximumHeight(100)
        self.style_description.setReadOnly(True)
        self.style_description.setStyleSheet("background-color: #1a1a1a; color: #98fb98;")
        
        style_layout.addWidget(self.genre_label)
        style_layout.addWidget(QLabel("Style Analysis:"))
        style_layout.addWidget(self.style_description)
        
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # Reading recommendations
        rec_group = QGroupBox("💡 Reading Insights")
        rec_layout = QVBoxLayout()
        
        self.insights_display = QTextEdit()
        self.insights_display.setReadOnly(True)
        self.insights_display.setStyleSheet("background-color: #1a1a1a; color: #ffa500;")
        self.insights_display.setPlaceholderText("Insights will appear after book analysis...")
        
        rec_layout.addWidget(self.insights_display)
        rec_group.setLayout(rec_layout)
        layout.addWidget(rec_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_characters_tab(self):
        """Create characters analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Character list
        self.character_tree = QTreeWidget()
        self.character_tree.setHeaderLabels(["Character", "Mentions", "Significance", "Description"])
        self.character_tree.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #444;")
        layout.addWidget(self.character_tree)
        
        # Character details
        char_details_group = QGroupBox("Character Details")
        char_details_layout = QVBoxLayout()
        
        self.character_details = QTextEdit()
        self.character_details.setReadOnly(True)
        self.character_details.setMaximumHeight(150)
        self.character_details.setStyleSheet("background-color: #1a1a1a; color: #87ceeb;")
        self.character_details.setPlaceholderText("Select a character to see details...")
        
        char_details_layout.addWidget(self.character_details)
        char_details_group.setLayout(char_details_layout)
        layout.addWidget(char_details_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_themes_tab(self):
        """Create themes analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Theme list
        self.theme_tree = QTreeWidget()
        self.theme_tree.setHeaderLabels(["Theme", "Strength", "Chapters", "Evidence"])
        self.theme_tree.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #444;")
        layout.addWidget(self.theme_tree)
        
        # Theme details
        theme_details_group = QGroupBox("Theme Analysis")
        theme_details_layout = QVBoxLayout()
        
        self.theme_details = QTextEdit()
        self.theme_details.setReadOnly(True)
        self.theme_details.setMaximumHeight(150)
        self.theme_details.setStyleSheet("background-color: #1a1a1a; color: #98fb98;")
        self.theme_details.setPlaceholderText("Select a theme to see detailed analysis...")
        
        theme_details_layout.addWidget(self.theme_details)
        theme_details_group.setLayout(theme_details_layout)
        layout.addWidget(theme_details_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_emotions_tab(self):
        """Create emotional arc analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Emotional summary
        emotion_summary_group = QGroupBox("😊 Emotional Journey Summary")
        emotion_summary_layout = QVBoxLayout()
        
        self.emotion_summary = QTextEdit()
        self.emotion_summary.setReadOnly(True)
        self.emotion_summary.setMaximumHeight(100)
        self.emotion_summary.setStyleSheet("background-color: #1a1a1a; color: #ff69b4;")
        
        emotion_summary_layout.addWidget(self.emotion_summary)
        emotion_summary_group.setLayout(emotion_summary_layout)
        layout.addWidget(emotion_summary_group)
        
        # Emotional timeline
        timeline_group = QGroupBox("📈 Emotional Timeline")
        timeline_layout = QVBoxLayout()
        
        self.emotion_timeline = QTreeWidget()
        self.emotion_timeline.setHeaderLabels(["Chapter", "Emotion", "Intensity", "Trigger"])
        self.emotion_timeline.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #444;")
        
        timeline_layout.addWidget(self.emotion_timeline)
        timeline_group.setLayout(timeline_layout)
        layout.addWidget(timeline_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_quotes_tab(self):
        """Create quotes collection tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Quote list
        self.quotes_list = QListWidget()
        self.quotes_list.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #444;")
        self.quotes_list.itemClicked.connect(self.display_quote_details)
        layout.addWidget(self.quotes_list)
        
        # Quote details
        quote_details_group = QGroupBox("Quote Details")
        quote_details_layout = QVBoxLayout()
        
        self.quote_details = QTextEdit()
        self.quote_details.setReadOnly(True)
        self.quote_details.setMaximumHeight(120)
        self.quote_details.setStyleSheet("background-color: #1a1a1a; color: #ffe066;")
        self.quote_details.setPlaceholderText("Select a quote to see details...")
        
        # Annotation controls
        annotation_layout = QHBoxLayout()
        self.annotation_input = QLineEdit()
        self.annotation_input.setPlaceholderText("Add your thoughts about this quote...")
        self.add_annotation_btn = QPushButton("📝 Add Note")
        self.add_annotation_btn.clicked.connect(self.add_quote_annotation)
        
        annotation_layout.addWidget(self.annotation_input)
        annotation_layout.addWidget(self.add_annotation_btn)
        
        quote_details_layout.addWidget(self.quote_details)
        quote_details_layout.addLayout(annotation_layout)
        quote_details_group.setLayout(quote_details_layout)
        layout.addWidget(quote_details_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_discussion_tab(self):
        """Create interactive discussion tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Discussion history
        discussion_group = QGroupBox("💬 Book Discussion")
        discussion_layout = QVBoxLayout()
        
        self.discussion_history = QTextEdit()
        self.discussion_history.setReadOnly(True)
        self.discussion_history.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: 'Courier New';")
        
        # Question input
        question_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask EchoMind about this book...")
        self.question_input.returnPressed.connect(self.ask_question)
        
        self.ask_button = QPushButton("❓ Ask")
        self.ask_button.clicked.connect(self.ask_question)
        
        # Preset questions
        self.preset_questions = QComboBox()
        self.preset_questions.addItems([
            "Tell me about the main characters",
            "What are the major themes?",
            "How did the story make you feel?",
            "What's the most significant quote?",
            "How would you describe the writing style?",
            "What did you learn from this book?"
        ])
        self.preset_questions.currentTextChanged.connect(self.load_preset_question)
        
        question_layout.addWidget(self.question_input)
        question_layout.addWidget(self.ask_button)
        question_layout.addWidget(self.preset_questions)
        
        discussion_layout.addWidget(self.discussion_history)
        discussion_layout.addLayout(question_layout)
        discussion_group.setLayout(discussion_layout)
        layout.addWidget(discussion_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_journal_tab(self):
        """Create reading journal tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Journal controls
        journal_controls = QHBoxLayout()
        
        self.export_journal_btn = QPushButton("📄 Export Journal")
        self.export_journal_btn.clicked.connect(self.export_reading_journal)
        
        self.view_all_books_btn = QPushButton("📚 All Books")
        self.view_all_books_btn.clicked.connect(self.view_all_books_journal)
        
        self.get_recommendations_btn = QPushButton("💡 Get Recommendations")
        self.get_recommendations_btn.clicked.connect(self.get_reading_recommendations)
        
        journal_controls.addWidget(self.export_journal_btn)
        journal_controls.addWidget(self.view_all_books_btn)
        journal_controls.addWidget(self.get_recommendations_btn)
        journal_controls.addStretch()
        
        layout.addLayout(journal_controls)
        
        # Journal display
        self.journal_display = QTextEdit()
        self.journal_display.setReadOnly(True)
        self.journal_display.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0; font-family: 'Georgia';")
        self.journal_display.setPlaceholderText("Your reading journal will appear here...")
        
        layout.addWidget(self.journal_display)
        
        # Personal notes
        notes_group = QGroupBox("📝 Personal Notes")
        notes_layout = QVBoxLayout()
        
        self.personal_notes = QTextEdit()
        self.personal_notes.setMaximumHeight(100)
        self.personal_notes.setPlaceholderText("Add your personal thoughts about this book...")
        self.personal_notes.setStyleSheet("background-color: #1a1a1a; color: #cccccc;")
        
        notes_controls = QHBoxLayout()
        self.save_notes_btn = QPushButton("💾 Save Notes")
        self.save_notes_btn.clicked.connect(self.save_personal_notes)
        
        notes_controls.addWidget(self.save_notes_btn)
        notes_controls.addStretch()
        
        notes_layout.addWidget(self.personal_notes)
        notes_layout.addLayout(notes_controls)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        tab.setLayout(layout)
        return tab
    
    def setup_timers(self):
        """Setup update timers"""
        # Library refresh timer
        self.library_timer = QTimer()
        self.library_timer.timeout.connect(self.refresh_library)
        self.library_timer.start(30000)  # Refresh every 30 seconds
        
        # Initial setup
        self.refresh_library()
        self.update_format_support()
    
    def update_format_support(self):
        """Update format support status"""
        if self.ebook_system:
            status = self.ebook_system.get_system_status()
            supported = [fmt for fmt in status.get('supported_formats', []) if fmt]
            
            if supported:
                self.format_status.setText(f"Supported: {', '.join(supported)}")
                self.format_status.setStyleSheet("color: #98fb98; font-size: 10pt;")
            else:
                self.format_status.setText("Only TXT files supported")
                self.format_status.setStyleSheet("color: #ffa500; font-size: 10pt;")
    
    def load_book_file(self):
        """Load a new book file"""
        if not self.ebook_system:
            QMessageBox.warning(self, "System Error", "EBook system not available")
            return
        
        # File dialog with multiple format support
        file_dialog = QFileDialog()
        file_filters = [
            "All Supported (*.txt *.pdf *.epub *.docx *.html *.htm)",
            "Text Files (*.txt)",
            "PDF Files (*.pdf)",
            "EPUB Files (*.epub)",
            "Word Documents (*.docx)",
            "HTML Files (*.html *.htm)",
            "All Files (*)"
        ]
        
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "Select Book File", 
            "", 
            ";;".join(file_filters)
        )
        
        if file_path:
            self.start_book_processing(file_path)
    
    def start_book_processing(self, file_path):
        """Start processing a book file"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.load_button.setEnabled(False)
        
        # Start processing thread
        self.processing_worker = AdvancedEbookWorker(file_path, self.ebook_system)
        self.processing_worker.progress_update.connect(self.update_processing_progress)
        self.processing_worker.analysis_complete.connect(self.display_book_analysis)
        self.processing_worker.error_occurred.connect(self.handle_processing_error)
        self.processing_worker.start()
    
    def update_processing_progress(self, status, percentage):
        """Update processing progress"""
        self.status_label.setText(status)
        self.progress_bar.setValue(percentage)
    
    def display_book_analysis(self, result):
        """Display the completed book analysis"""
        self.progress_bar.setVisible(False)
        self.load_button.setEnabled(True)
        self.status_label.setText("✅ Analysis complete!")
        
        # Store current book data
        self.current_book_id = result['book_id']
        self.current_analysis = result['analysis_summary']
        
        # Update all displays
        self.update_book_info(result)
        self.update_overview_tab(result)
        self.update_characters_tab(result)
        self.update_themes_tab(result)
        self.update_emotions_tab(result)
        self.update_quotes_tab(result)
        self.update_journal_tab()
        
        # Refresh library
        self.refresh_library()
        
        # Show success message
        QMessageBox.information(
            self, 
            "Analysis Complete", 
            f"Successfully analyzed '{result['metadata'].title}'\n\n"
            f"Found {result['analysis_summary']['characters_found']} characters, "
            f"{result['analysis_summary']['themes_identified']} themes, and "
            f"{result['analysis_summary']['quotes_extracted']} significant quotes."
        )
    
    def handle_processing_error(self, error_message):
        """Handle processing errors"""
        self.progress_bar.setVisible(False)
        self.load_button.setEnabled(True)
        self.status_label.setText("❌ Processing failed")
        
        QMessageBox.critical(self, "Processing Error", f"Failed to process book:\n{error_message}")
    
    def update_book_info(self, result):
        """Update current book information display"""
        metadata = result['metadata']
        analysis = result['analysis_summary']
        
        self.book_title_label.setText(f"{metadata.title}")
        
        info_text = f"Author: {metadata.author}\n"
        info_text += f"Words: {metadata.word_count:,}\n"
        info_text += f"Reading Level: Grade {metadata.reading_level:.1f}\n"
        info_text += f"Estimated Time: {metadata.estimated_reading_time} minutes\n"
        info_text += f"Chapters: {metadata.chapter_count}\n"
        
        if analysis['genre_hints']:
            info_text += f"Genre: {', '.join(analysis['genre_hints'])}"
        
        self.book_details.setPlainText(info_text)
        
        # Update reading progress
        progress = getattr(metadata, 'reading_progress', 0.0)
        self.reading_progress_bar.setValue(int(progress * 100))
        self.reading_progress_label.setText(f"{progress*100:.1f}% complete")
    
    def update_overview_tab(self, result):
        """Update the overview tab with analysis results"""
        metadata = result['metadata']
        analysis = result['analysis_summary']
        
        # Update statistics
        self.stats_labels['word_count'].setText(f"{metadata.word_count:,}")
        self.stats_labels['reading_level'].setText(f"Grade {metadata.reading_level:.1f}")
        self.stats_labels['estimated_time'].setText(f"{metadata.estimated_reading_time} min")
        self.stats_labels['chapters'].setText(str(metadata.chapter_count))
        self.stats_labels['characters_found'].setText(str(analysis['characters_found']))
        self.stats_labels['themes_found'].setText(str(analysis['themes_identified']))
        self.stats_labels['quotes_extracted'].setText(str(analysis['quotes_extracted']))
        
        # Update genre
        if analysis['genre_hints']:
            self.genre_label.setText(f"Genre hints: {', '.join(analysis['genre_hints'])}")
        else:
            self.genre_label.setText("Genre: Not determined")
        
        # Update style description
        style_desc = analysis.get('writing_style_summary', 'Style analysis not available')
        self.style_description.setPlainText(style_desc)
        
        # Generate insights
        insights = self.generate_book_insights(result)
        self.insights_display.setPlainText(insights)
    
    def generate_book_insights(self, result):
        """Generate reading insights for the book"""
        metadata = result['metadata']
        analysis = result['analysis_summary']
        
        insights = []
        
        # Reading level insights
        if metadata.reading_level > 15:
            insights.append("🎓 This is a highly sophisticated work that will challenge you intellectually.")
        elif metadata.reading_level < 8:
            insights.append("📖 This book offers accessible, straightforward reading.")
        else:
            insights.append("📚 This book strikes a good balance between accessibility and depth.")
        
        # Length insights
        if metadata.word_count > 100000:
            insights.append("📏 This is a substantial work that will require significant time investment.")
        elif metadata.word_count < 30000:
            insights.append("⚡ This is a concise work perfect for focused reading sessions.")
        
        # Character insights
        if analysis['characters_found'] > 10:
            insights.append("👥 Rich cast of characters - you'll need to keep track of many personalities.")
        elif analysis['characters_found'] < 3:
            insights.append("👤 Character-focused narrative with intimate character development.")
        
        # Theme insights
        if analysis['themes_identified'] > 5:
            insights.append("🎭 Complex thematic structure with multiple layers of meaning.")
        elif analysis['themes_identified'] > 0:
            insights.append("💭 Clear thematic focus that will provide food for thought.")
        
        # Quote insights
        if analysis['quotes_extracted'] > 20:
            insights.append("💎 Rich in memorable passages and quotable moments.")
        
        return "\n\n".join(insights)
    
    def update_characters_tab(self, result):
        """Update characters analysis tab"""
        if not self.ebook_system or not self.current_book_id:
            return
        
        try:
            book_data = self.ebook_system._load_book_data(self.current_book_id)
            if not book_data:
                return
            
            characters = book_data['analysis'].get('characters', [])
            
            self.character_tree.clear()
            
            for char in characters:
                item = QTreeWidgetItem()
                item.setText(0, char['name'])
                item.setText(1, str(char['mentions']))
                item.setText(2, f"{char['significance_score']:.2f}")
                item.setText(3, char.get('description', 'No description')[:50] + "...")
                
                # Store full character data
                item.setData(0, Qt.UserRole, char)
                
                self.character_tree.addTopLevelItem(item)
            
            # Connect selection handler
            self.character_tree.itemClicked.connect(self.display_character_details)
            
        except Exception as e:
            print(f"Error updating characters tab: {e}")
    
    def display_character_details(self, item):
        """Display detailed character information"""
        char_data = item.data(0, Qt.UserRole)
        if char_data:
            details = f"**{char_data['name']}**\n\n"
            details += f"Mentions: {char_data['mentions']}\n"
            details += f"Significance: {char_data['significance_score']:.2f}\n\n"
            
            if char_data.get('description'):
                details += f"Description: {char_data['description']}\n\n"
            
            if char_data.get('first_appearance'):
                details += f"First appears in chapter: {char_data['first_appearance']}\n"
            
            if char_data.get('relationships'):
                details += f"Relationships: {', '.join(char_data['relationships'].keys())}\n"
                
            self.character_details.setPlainText(details)
    
    def update_themes_tab(self, result):
        """Update themes analysis tab"""
        if not self.ebook_system or not self.current_book_id:
            return
            
        try:
            book_data = self.ebook_system._load_book_data(self.current_book_id)
            if not book_data:
                return
            
            themes = book_data['analysis'].get('themes', [])
            
            self.theme_tree.clear()
            
            for theme in themes:
                item = QTreeWidgetItem()
                item.setText(0, theme['theme'])
                item.setText(1, f"{theme['strength']:.2f}")
                item.setText(2, f"{len(theme['chapters'])} chapters")
                item.setText(3, f"{len(theme['evidence'])} pieces of evidence")
                
                # Store full theme data
                item.setData(0, Qt.UserRole, theme)
                
                self.theme_tree.addTopLevelItem(item)
            
            # Connect selection handler
            self.theme_tree.itemClicked.connect(self.display_theme_details)
            
        except Exception as e:
            print(f"Error updating themes tab: {e}")
    
    def display_theme_details(self, item):
        """Display detailed theme information"""
        theme_data = item.data(0, Qt.UserRole)
        if theme_data:
            details = f"**{theme_data['theme']}**\n\n"
            details += f"Strength: {theme_data['strength']:.2f}\n"
            details += f"Present in chapters: {', '.join(map(str, theme_data['chapters']))}\n\n"
            
            details += "Evidence:\n"
            for evidence in theme_data['evidence'][:5]:
                details += f"• {evidence}\n"
                
            self.theme_details.setPlainText(details)
    
    def update_emotions_tab(self, result):
        """Update emotional arc analysis tab"""
        if not self.ebook_system or not self.current_book_id:
            return
            
        try:
            book_data = self.ebook_system._load_book_data(self.current_book_id)
            if not book_data:
                return
            
            emotional_arc = book_data['analysis'].get('emotional_arc', [])
            
            if not emotional_arc:
                self.emotion_summary.setPlainText("No emotional analysis available for this book.")
                return
            
            # Create emotional summary
            emotions_by_type = {}
            for ep in emotional_arc:
                if ep['emotion'] not in emotions_by_type:
                    emotions_by_type[ep['emotion']] = []
                emotions_by_type[ep['emotion']].append(ep['intensity'])
            
            summary_parts = []
            for emotion, intensities in emotions_by_type.items():
                avg_intensity = sum(intensities) / len(intensities)
                summary_parts.append(f"{emotion.title()}: {avg_intensity:.2f} avg intensity ({len(intensities)} occurrences)")
            
            self.emotion_summary.setPlainText("\n".join(summary_parts))
            
            # Populate timeline
            self.emotion_timeline.clear()
            
            # Group by chapter for better display
            by_chapter = {}
            for ep in emotional_arc:
                if ep['chapter'] not in by_chapter:
                    by_chapter[ep['chapter']] = []
                by_chapter[ep['chapter']].append(ep)
            
            for chapter in sorted(by_chapter.keys()):
                chapter_item = QTreeWidgetItem()
                chapter_item.setText(0, f"Chapter {chapter}")
                
                # Find dominant emotion for chapter
                chapter_emotions = by_chapter[chapter]
                dominant = max(chapter_emotions, key=lambda x: x['intensity'])
                
                chapter_item.setText(1, dominant['emotion'].title())
                chapter_item.setText(2, f"{dominant['intensity']:.2f}")
                chapter_item.setText(3, dominant['trigger'])
                
                self.emotion_timeline.addTopLevelItem(chapter_item)
                
                # Add individual emotional moments as children
                for ep in chapter_emotions:
                    if ep['intensity'] > 0.6:  # Only show high-intensity moments
                        child_item = QTreeWidgetItem()
                        child_item.setText(1, ep['emotion'])
                        child_item.setText(2, f"{ep['intensity']:.2f}")
                        child_item.setText(3, ep['trigger'])
                        chapter_item.addChild(child_item)
            
        except Exception as e:
            print(f"Error updating emotions tab: {e}")
    
    def update_quotes_tab(self, result):
        """Update quotes collection tab"""
        if not self.ebook_system or not self.current_book_id:
            return
            
        try:
            book_data = self.ebook_system._load_book_data(self.current_book_id)
            if not book_data:
                return
            
            quotes = book_data['analysis'].get('quotes', [])
            
            self.quotes_list.clear()
            
            for quote in quotes:
                item = QListWidgetItem()
                
                # Truncate long quotes for list display
                display_text = quote['text']
                if len(display_text) > 80:
                    display_text = display_text[:77] + "..."
                
                item.setText(f"Ch.{quote['chapter']}: \"{display_text}\"")
                item.setData(Qt.UserRole, quote)
                
                self.quotes_list.addItem(item)
                
        except Exception as e:
            print(f"Error updating quotes tab: {e}")
    
    def display_quote_details(self, item):
        """Display detailed quote information"""
        quote_data = item.data(Qt.UserRole)
        if quote_data:
            details = f"Chapter {quote_data['chapter']}\n"
            details += f"Emotional Impact: {quote_data.get('emotional_impact', 'Not analyzed')}\n"
            details += f"Significance: {quote_data.get('significance_score', 0):.2f}\n\n"
            details += f"\"{quote_data['text']}\"\n"
            
            self.quote_details.setPlainText(details)
    
    def add_quote_annotation(self):
        """Add annotation to selected quote"""
        current_item = self.quotes_list.currentItem()
        if not current_item or not self.current_book_id:
            return
            
        annotation_text = self.annotation_input.text().strip()
        if not annotation_text:
            return
            
        quote_data = current_item.data(Qt.UserRole)
        if quote_data and self.ebook_system:
            # Add annotation to the system
            success = self.ebook_system.add_annotation(
                self.current_book_id,
                quote_data['chapter'],
                quote_data['text'],
                annotation_text
            )
            
            if success:
                self.annotation_input.clear()
                
                # Update display
                current_details = self.quote_details.toPlainText()
                updated_details = current_details + f"\n\nYour Note: {annotation_text}"
                self.quote_details.setPlainText(updated_details)
                
                QMessageBox.information(self, "Annotation Added", "Your note has been saved!")
    
    def ask_question(self):
        """Ask a question about the current book"""
        if not self.current_book_id or not self.ebook_system:
            QMessageBox.warning(self, "No Book", "Please select a book first.")
            return
            
        question = self.question_input.text().strip()
        if not question:
            return
            
        # Add question to discussion
        self.discussion_history.append(f"\n🤔 You: {question}\n")
        self.question_input.clear()
        
        # Show thinking indicator
        self.discussion_history.append("🤖 EchoMind: *thinking...*\n")
        
        # Start discussion worker
        self.discussion_worker = BookDiscussionWorker(
            self.current_book_id, 
            question, 
            self.ebook_system
        )
        self.discussion_worker.response_ready.connect(self.display_discussion_response)
        self.discussion_worker.start()
    
    def display_discussion_response(self, response):
        """Display EchoMind's response to the question"""
        # Remove thinking indicator
        current_text = self.discussion_history.toPlainText()
        if "*thinking...*" in current_text:
            current_text = current_text.replace("🤖 EchoMind: *thinking...*\n", "")
            self.discussion_history.setPlainText(current_text)
        
        # Add response
        self.discussion_history.append(f"🤖 EchoMind: {response}\n")
        self.discussion_history.append("-" * 50 + "\n")
        
        # Scroll to bottom
        cursor = self.discussion_history.textCursor()
        cursor.movePosition(cursor.End)
        self.discussion_history.setTextCursor(cursor)
    
    def load_preset_question(self, question):
        """Load a preset question"""
        if question and question != "":
            self.question_input.setText(question)
    
    def update_journal_tab(self):
        """Update the reading journal display"""
        if not self.current_book_id or not self.ebook_system:
            return
            
        try:
            # Export journal for current book
            journal_entry = self.ebook_system.export_reading_journal(self.current_book_id)
            self.journal_display.setPlainText(journal_entry)
        except Exception as e:
            self.journal_display.setPlainText(f"Error loading journal: {e}")
    
    def export_reading_journal(self):
        """Export the complete reading journal"""
        if not self.ebook_system:
            return
            
        try:
            journal = self.ebook_system.export_reading_journal()
            
            # Save to file
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Reading Journal",
                f"reading_journal_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(journal)
                
                QMessageBox.information(self, "Export Complete", f"Journal exported to:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export journal:\n{e}")
    
    def view_all_books_journal(self):
        """View journal entries for all books"""
        if not self.ebook_system:
            return
            
        try:
            # Get complete journal
            complete_journal = self.ebook_system.export_reading_journal()
            self.journal_display.setPlainText(complete_journal)
        except Exception as e:
            self.journal_display.setPlainText(f"Error loading complete journal: {e}")
    
    def get_reading_recommendations(self):
        """Get personalized reading recommendations"""
        if not self.ebook_system:
            return
            
        try:
            recommendations = self.ebook_system.get_reading_recommendations()
            
            rec_text = "📚 **Personalized Reading Recommendations**\n\n"
            for i, rec in enumerate(recommendations, 1):
                rec_text += f"{i}. {rec}\n\n"
            
            self.journal_display.setPlainText(rec_text)
            
        except Exception as e:
            self.journal_display.setPlainText(f"Error generating recommendations: {e}")
    
    def save_personal_notes(self):
        """Save personal notes for the current book"""
        if not self.current_book_id:
            QMessageBox.warning(self, "No Book", "Please select a book first.")
            return
            
        notes = self.personal_notes.toPlainText().strip()
        if not notes:
            return
            
        try:
            # Save notes
            notes_file = Path("logs/book_notes") / f"{self.current_book_id}_notes.txt"
            notes_file.parent.mkdir(exist_ok=True)
            
            with open(notes_file, 'w', encoding='utf-8') as f:
                f.write(f"Personal Notes for Book ID: {self.current_book_id}\n")
                f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 50 + "\n")
                f.write(notes)
            
            QMessageBox.information(self, "Notes Saved", "Your personal notes have been saved!")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save notes:\n{e}")
    
    def refresh_library(self):
        """Refresh the book library display"""
        if not self.ebook_system:
            return
            
        try:
            books = self.ebook_system.get_book_library()
            
            self.library_list.clear()
            
            for book in books:
                item = QListWidgetItem()
                
                # Format display text
                progress_indicator = "✅" if book['reading_progress'] > 0.9 else "📖" if book['reading_progress'] > 0 else "📚"
                display_text = f"{progress_indicator} {book['title']}"
                
                if book['author'] != "Unknown":
                    display_text += f" - {book['author']}"
                
                # Add genre hints if available
                if book['genre_hints']:
                    display_text += f" ({', '.join(book['genre_hints'][:2])})"
                
                item.setText(display_text)
                item.setData(Qt.UserRole, book)
                
                # Color coding based on reading level
                if book['reading_level'] > 15:
                    item.setForeground(QColor("#ff6b6b"))  # Red for difficult
                elif book['reading_level'] < 8:
                    item.setForeground(QColor("#98fb98"))  # Green for easy
                else:
                    item.setForeground(QColor("#87ceeb"))  # Blue for moderate
                
                self.library_list.addItem(item)
                
        except Exception as e:
            print(f"Error refreshing library: {e}")
    
    def select_book_from_library(self, item):
        """Select a book from the library"""
        book_data = item.data(Qt.UserRole)
        if book_data and self.ebook_system:
            self.current_book_id = book_data['id']
            
            # Load full book data
            try:
                full_book_data = self.ebook_system._load_book_data(self.current_book_id)
                if full_book_data:
                    # Create a result-like structure for consistency
                    result = {
                        'book_id': self.current_book_id,
                        'metadata': type('obj', (object,), full_book_data['metadata'])(),
                        'analysis_summary': {
                            'characters_found': len(full_book_data['analysis'].get('characters', [])),
                            'themes_identified': len(full_book_data['analysis'].get('themes', [])),
                            'quotes_extracted': len(full_book_data['analysis'].get('quotes', [])),
                            'emotional_data_points': len(full_book_data['analysis'].get('emotional_arc', [])),
                            'genre_hints': full_book_data['analysis'].get('genre_hints', []),
                            'reading_level': full_book_data['metadata']['reading_level'],
                            'writing_style_summary': full_book_data['analysis'].get('writing_style', {}).get('style_description', 'Not analyzed')
                        }
                    }
                    
                    # Update all displays
                    self.update_book_info(result)
                    self.update_overview_tab(result)
                    self.update_characters_tab(result)
                    self.update_themes_tab(result)
                    self.update_emotions_tab(result)
                    self.update_quotes_tab(result)
                    self.update_journal_tab()
                    
                    # Load personal notes if they exist
                    self.load_personal_notes()
                    
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Failed to load book data:\n{e}")
    
    def load_personal_notes(self):
        """Load personal notes for the current book"""
        if not self.current_book_id:
            return
            
        try:
            notes_file = Path("logs/book_notes") / f"{self.current_book_id}_notes.txt"
            
            if notes_file.exists():
                with open(notes_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract just the notes part (after the header)
                    if "-" * 50 in content:
                        notes_part = content.split("-" * 50, 1)[1].strip()
                        self.personal_notes.setPlainText(notes_part)
            else:
                self.personal_notes.clear()
                
        except Exception as e:
            print(f"Error loading personal notes: {e}")
    
    def compare_selected_books(self):
        """Compare two selected books"""
        selected_items = self.library_list.selectedItems()
        
        if len(selected_items) != 2:
            QMessageBox.information(
                self, 
                "Book Comparison", 
                "Please select exactly 2 books to compare.\n\nHold Ctrl while clicking to select multiple books."
            )
            return
        
        if not self.ebook_system:
            return
            
        try:
            book1_data = selected_items[0].data(Qt.UserRole)
            book2_data = selected_items[1].data(Qt.UserRole)
            
            comparison = self.ebook_system.compare_books(book1_data['id'], book2_data['id'])
            
            # Show comparison in a dialog
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Book Comparison")
            dialog.setText("Comparison Analysis")
            dialog.setDetailedText(comparison)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Comparison Error", f"Failed to compare books:\n{e}")

def integrate_enhanced_ebook_gui(main_gui, ebook_system):
    """Integrate the enhanced ebook GUI into the main EchoMind GUI"""
    
    enhanced_ebook_tab = EnhancedEbookTab(ebook_system)
    
    if hasattr(main_gui, 'tabs'):
        # Find and replace existing ebook tab
        for i in range(main_gui.tabs.count()):
            if "Ebook" in main_gui.tabs.tabText(i):
                main_gui.tabs.removeTab(i)
                break
        
        main_gui.tabs.addTab(enhanced_ebook_tab, "📚 Advanced Ebooks")
        main_gui.enhanced_ebook_tab = enhanced_ebook_tab
        
        print("✅ Enhanced ebook GUI integrated successfully")
    else:
        print("❌ Could not integrate enhanced ebook GUI - main GUI structure not compatible")
    
    return enhanced_ebook_tab

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    test_widget = EnhancedEbookTab()
    test_widget.setWindowTitle("Enhanced EBook System - Test")
    test_widget.show()
    
    sys.exit(app.exec_())
