def update_journal_tab(self):
    """Update the reading journal display with better debugging"""
    if not self.current_book_id or not self.ebook_system:
        self.journal_display.setPlainText("No book selected or system unavailable")
        return
        
    try:
        print(f"DEBUG JOURNAL: Updating journal for book ID: {self.current_book_id}")
        
        # Method 1: Try system's export method
        journal_content = None
        if hasattr(self.ebook_system, 'export_reading_journal'):
            try:
                raw_journal = self.ebook_system.export_reading_journal(self.current_book_id)
                if isinstance(raw_journal, dict):
                    journal_content = json.dumps(raw_journal, indent=2, ensure_ascii=False)
                elif isinstance(raw_journal, str):
                    journal_content = raw_journal
                else:
                    journal_content = str(raw_journal)
                print(f"DEBUG JOURNAL: Got journal: {len(journal_content)} chars")
            except Exception as e:
                print(f"DEBUG JOURNAL: export_reading_journal failed: {e}")
        
        # Method 2: Try to get book data and create journal
        if not journal_content:
            try:
                book_data = None
                
                # Try to load book data
                if hasattr(self.ebook_system, '_load_book_data'):
                    book_data = self.ebook_system._load_book_data(self.current_book_id)
                
                if not book_data and hasattr(self.ebook_system, 'get_book_library'):
                    books = self.ebook_system.get_book_library()
                    for book in books:
                        if book.get('id') == self.current_book_id:
                            book_data = book
                            break
                
                if book_data:
                    journal_content = self.create_detailed_journal_entry(book_data)
                    print(f"DEBUG JOURNAL: Created detailed journal: {len(journal_content)} chars")
                else:
                    print("DEBUG JOURNAL: No book data found for detailed journal")
                    
            except Exception as e:
                print(f"DEBUG JOURNAL: Failed to create detailed journal: {e}")
        
        # Method 3: Create basic journal entry
        if not journal_content:
            journal_content = self.create_basic_journal_entry()
            print("DEBUG JOURNAL: Created basic journal entry")
        
        # Display the journal
        if journal_content:
            if not isinstance(journal_content, str):
                journal_content = json.dumps(journal_content, indent=2, ensure_ascii=False)
            self.journal_display.setPlainText(journal_content)
        else:
            self.journal_display.setPlainText("Unable to generate journal entry")
            
    except Exception as e:
        print(f"ERROR JOURNAL: Major error updating journal: {e}")
        self.journal_display.setPlainText(f"Error loading journal: {e}")

    def create_detailed_journal_entry(self, book_data):
        """Create a detailed journal entry from book data"""
        try:
            journal_text = f"📖 DETAILED READING LOG\n{'='*50}\n\n"
            
            # Basic info
            metadata = book_data.get('metadata', {})
            if metadata:
                title = metadata.get('title', 'Unknown Title')
                author = metadata.get('author', 'Unknown Author')
                journal_text += f"Title: {title}\n"
                journal_text += f"Author: {author}\n"
                journal_text += f"Word Count: {metadata.get('word_count', 0):,}\n"
                journal_text += f"Reading Level: Grade {metadata.get('reading_level', 0):.1f}\n"
                journal_text += f"Estimated Reading Time: {metadata.get('estimated_reading_time', 0)} minutes\n\n"
            
            # Analysis summary
            analysis = book_data.get('analysis', {})
            if analysis:
                journal_text += f"ANALYSIS SUMMARY\n{'-'*30}\n"
                
                # Characters
                characters = analysis.get('characters', [])
                journal_text += f"Characters Found: {len(characters)}\n"
                if characters:
                    journal_text += "Main Characters:\n"
                    for i, char in enumerate(characters[:5]):  # Top 5 characters
                        if isinstance(char, dict):
                            name = char.get('name', char.get('character', 'Unknown'))
                            mentions = char.get('mentions', char.get('count', 0))
                            journal_text += f"  • {name} ({mentions} mentions)\n"
                        elif isinstance(char, str):
                            journal_text += f"  • {char}\n"
                    journal_text += "\n"
                
                # Themes
                themes = analysis.get('themes', [])
                journal_text += f"Themes Identified: {len(themes)}\n"
                if themes:
                    journal_text += "Major Themes:\n"
                    for i, theme in enumerate(themes[:5]):  # Top 5 themes
                        if isinstance(theme, dict):
                            name = theme.get('theme', theme.get('name', 'Unknown'))
                            strength = theme.get('strength', theme.get('score', 0))
                            journal_text += f"  • {name} (strength: {strength:.2f})\n"
                        elif isinstance(theme, str):
                            journal_text += f"  • {theme}\n"
                    journal_text += "\n"
                
                # Emotional arc
                emotions = analysis.get('emotional_arc', [])
                journal_text += f"Emotional Data Points: {len(emotions)}\n"
                if emotions:
                    emotion_summary = {}
                    for emotion in emotions:
                        if isinstance(emotion, dict):
                            emo_name = emotion.get('emotion', emotion.get('feeling', 'unknown'))
                            if emo_name in emotion_summary:
                                emotion_summary[emo_name] += 1
                            else:
                                emotion_summary[emo_name] = 1
                        elif isinstance(emotion, str):
                            if emotion in emotion_summary:
                                emotion_summary[emotion] += 1
                            else:
                                emotion_summary[emotion] = 1
                    
                    if emotion_summary:
                        journal_text += "Dominant Emotions:\n"
                        for emo, count in sorted(emotion_summary.items(), key=lambda x: x[1], reverse=True)[:3]:
                            journal_text += f"  • {emo.title()} ({count} occurrences)\n"
                    journal_text += "\n"
                
                # Quotes
                quotes = analysis.get('quotes', [])
                journal_text += f"Notable Quotes: {len(quotes)}\n"
                if quotes:
                    journal_text += "Sample Quotes:\n"
                    for i, quote in enumerate(quotes[:3]):  # Top 3 quotes
                        if isinstance(quote, dict):
                            text = quote.get('text', quote.get('quote', 'No text'))
                            chapter = quote.get('chapter', quote.get('location', 'Unknown'))
                            journal_text += f"  • Chapter {chapter}: \"{text[:100]}{'...' if len(str(text)) > 100 else ''}\"\n"
                        elif isinstance(quote, str):
                            journal_text += f"  • \"{quote[:100]}{'...' if len(quote) > 100 else ''}\"\n"
                    journal_text += "\n"
            
            # Reading progress and dates
            journal_text += f"READING RECORD\n{'-'*30}\n"
            journal_text += f"Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            journal_text += f"Book ID: {self.current_book_id}\n"
            
            if metadata:
                progress = metadata.get('reading_progress', 0.0)
                journal_text += f"Reading Progress: {progress*100:.1f}%\n"
                
                if 'ingestion_date' in metadata:
                    journal_text += f"Added to Library: {metadata['ingestion_date']}\n"
            
            # Personal notes section
            journal_text += f"\nPERSONAL NOTES\n{'-'*30}\n"
            
            # Try to load existing personal notes
            try:
                notes_file = Path("logs/book_notes") / f"{self.current_book_id}_notes.txt"
                if notes_file.exists():
                    with open(notes_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "-" * 50 in content:
                            notes_part = content.split("-" * 50, 1)[1].strip()
                            journal_text += notes_part + "\n"
                        else:
                            journal_text += content + "\n"
                else:
                    journal_text += "No personal notes yet. Use the Personal Notes section to add your thoughts.\n"
            except Exception as e:
                journal_text += f"Error loading personal notes: {e}\n"
            
            journal_text += f"\n{'='*50}\n"
            journal_text += "End of Reading Log\n"
            
            return journal_text
            
        except Exception as e:
            print(f"ERROR: Failed to create detailed journal: {e}")
            return f"Error creating detailed journal: {e}""""
Enhanced EBook GUI for EchoMind - Full Featured Version - FIXED
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
import os

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
    
    def safe_get_attr(self, obj, attr, default=None):
        """Safely get attribute from object or dict"""
        try:
            if obj is None:
                return default
            elif isinstance(obj, dict):
                return obj.get(attr, default)
            elif isinstance(obj, str):
                # If it's a string and we're looking for 'name' or 'theme', return the string itself
                if attr in ['name', 'theme', 'text', 'emotion']:
                    return obj
                else:
                    return default
            elif isinstance(obj, (list, tuple)):
                return default
            else:
                return getattr(obj, attr, default)
        except (AttributeError, TypeError, KeyError):
            return default

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
        try:
            if self.ebook_system and hasattr(self.ebook_system, 'get_system_status'):
                status = self.ebook_system.get_system_status()
                supported = [fmt for fmt in status.get('supported_formats', []) if fmt]
                
                if supported:
                    self.format_status.setText(f"Supported: {', '.join(supported)}")
                    self.format_status.setStyleSheet("color: #98fb98; font-size: 10pt;")
                else:
                    self.format_status.setText("Only TXT files supported")
                    self.format_status.setStyleSheet("color: #ffa500; font-size: 10pt;")
            else:
                self.format_status.setText("System status unavailable")
                self.format_status.setStyleSheet("color: #ff6b6b; font-size: 10pt;")
        except Exception as e:
            self.format_status.setText(f"Status error: {str(e)[:30]}")
            self.format_status.setStyleSheet("color: #ff6b6b; font-size: 10pt;")
    
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
        try:
            self.progress_bar.setVisible(False)
            self.load_button.setEnabled(True)
            self.status_label.setText("✅ Analysis complete!")
            
            # Store current book data
            self.current_book_id = result.get('book_id')
            self.current_analysis = result.get('analysis_summary', {})
            
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
            metadata = result.get('metadata', {})
            analysis = result.get('analysis_summary', {})
            
            title = getattr(metadata, 'title', 'Unknown Title') if hasattr(metadata, 'title') else metadata.get('title', 'Unknown Title')
            chars_found = analysis.get('characters_found', 0)
            themes_found = analysis.get('themes_identified', 0)
            quotes_found = analysis.get('quotes_extracted', 0)
            
            QMessageBox.information(
                self, 
                "Analysis Complete", 
                f"Successfully analyzed '{title}'\n\n"
                f"Found {chars_found} characters, "
                f"{themes_found} themes, and "
                f"{quotes_found} significant quotes."
            )
        except Exception as e:
            QMessageBox.critical(self, "Display Error", f"Error displaying analysis: {e}")
    
    def handle_processing_error(self, error_message):
        """Handle processing errors"""
        self.progress_bar.setVisible(False)
        self.load_button.setEnabled(True)
        self.status_label.setText("❌ Processing failed")
        
        QMessageBox.critical(self, "Processing Error", f"Failed to process book:\n{error_message}")
    
    def update_book_info(self, result):
        """Update current book information display"""
        try:
            metadata = result.get('metadata', {})
            analysis = result.get('analysis_summary', {})
            
            # Safe attribute access
            title = getattr(metadata, 'title', 'Unknown Title') if hasattr(metadata, 'title') else metadata.get('title', 'Unknown Title')
            author = getattr(metadata, 'author', 'Unknown Author') if hasattr(metadata, 'author') else metadata.get('author', 'Unknown Author')
            word_count = getattr(metadata, 'word_count', 0) if hasattr(metadata, 'word_count') else metadata.get('word_count', 0)
            reading_level = getattr(metadata, 'reading_level', 0.0) if hasattr(metadata, 'reading_level') else metadata.get('reading_level', 0.0)
            reading_time = getattr(metadata, 'estimated_reading_time', 0) if hasattr(metadata, 'estimated_reading_time') else metadata.get('estimated_reading_time', 0)
            chapter_count = getattr(metadata, 'chapter_count', 0) if hasattr(metadata, 'chapter_count') else metadata.get('chapter_count', 0)
            
            self.book_title_label.setText(f"{title}")
            
            info_text = f"Author: {author}\n"
            info_text += f"Words: {word_count:,}\n"
            info_text += f"Reading Level: Grade {reading_level:.1f}\n"
            info_text += f"Estimated Time: {reading_time} minutes\n"
            info_text += f"Chapters: {chapter_count}\n"
            
            genre_hints = analysis.get('genre_hints', [])
            if genre_hints:
                info_text += f"Genre: {', '.join(genre_hints)}"
            
            self.book_details.setPlainText(info_text)
            
            # Update reading progress
            progress = getattr(metadata, 'reading_progress', 0.0) if hasattr(metadata, 'reading_progress') else metadata.get('reading_progress', 0.0)
            self.reading_progress_bar.setValue(int(progress * 100))
            self.reading_progress_label.setText(f"{progress*100:.1f}% complete")
        except Exception as e:
            self.book_title_label.setText("Error loading book info")
            self.book_details.setPlainText(f"Error: {e}")
    
    def update_overview_tab(self, result):
        """Update the overview tab with analysis results"""
        try:
            metadata = result.get('metadata', {})
            analysis = result.get('analysis_summary', {})
            
            # Safe access to metadata
            word_count = getattr(metadata, 'word_count', 0) if hasattr(metadata, 'word_count') else metadata.get('word_count', 0)
            reading_level = getattr(metadata, 'reading_level', 0.0) if hasattr(metadata, 'reading_level') else metadata.get('reading_level', 0.0)
            reading_time = getattr(metadata, 'estimated_reading_time', 0) if hasattr(metadata, 'estimated_reading_time') else metadata.get('estimated_reading_time', 0)
            chapter_count = getattr(metadata, 'chapter_count', 0) if hasattr(metadata, 'chapter_count') else metadata.get('chapter_count', 0)
            
            # Update statistics
            self.stats_labels['word_count'].setText(f"{word_count:,}")
            self.stats_labels['reading_level'].setText(f"Grade {reading_level:.1f}")
            self.stats_labels['estimated_time'].setText(f"{reading_time} min")
            self.stats_labels['chapters'].setText(str(chapter_count))
            self.stats_labels['characters_found'].setText(str(analysis.get('characters_found', 0)))
            self.stats_labels['themes_found'].setText(str(analysis.get('themes_identified', 0)))
            self.stats_labels['quotes_extracted'].setText(str(analysis.get('quotes_extracted', 0)))
            
            # Update genre
            genre_hints = analysis.get('genre_hints', [])
            if genre_hints:
                self.genre_label.setText(f"Genre hints: {', '.join(genre_hints)}")
            else:
                self.genre_label.setText("Genre: Not determined")
            
            # Update style description
            style_desc = analysis.get('writing_style_summary', 'Style analysis not available')
            self.style_description.setPlainText(style_desc)
            
            # Generate insights
            insights = self.generate_book_insights(result)
            self.insights_display.setPlainText(insights)
        except Exception as e:
            print(f"Error updating overview tab: {e}")
            self.insights_display.setPlainText(f"Error loading overview: {e}")
    
    def generate_book_insights(self, result):
        """Generate reading insights for the book"""
        try:
            metadata = result.get('metadata', {})
            analysis = result.get('analysis_summary', {})
            
            insights = []
            
            # Safe access to metadata
            word_count = getattr(metadata, 'word_count', 0) if hasattr(metadata, 'word_count') else metadata.get('word_count', 0)
            reading_level = getattr(metadata, 'reading_level', 0.0) if hasattr(metadata, 'reading_level') else metadata.get('reading_level', 0.0)
            
            # Reading level insights
            if reading_level > 15:
                insights.append("🎓 This is a highly sophisticated work that will challenge you intellectually.")
            elif reading_level < 8:
                insights.append("📖 This book offers accessible, straightforward reading.")
            else:
                insights.append("📚 This book strikes a good balance between accessibility and depth.")
            
            # Length insights
            if word_count > 100000:
                insights.append("📏 This is a substantial work that will require significant time investment.")
            elif word_count < 30000:
                insights.append("⚡ This is a concise work perfect for focused reading sessions.")
            
            # Character insights
            chars_found = analysis.get('characters_found', 0)
            if chars_found > 10:
                insights.append("👥 Rich cast of characters - you'll need to keep track of many personalities.")
            elif chars_found < 3:
                insights.append("👤 Character-focused narrative with intimate character development.")
            
            # Theme insights
            themes_found = analysis.get('themes_identified', 0)
            if themes_found > 5:
                insights.append("🎭 Complex thematic structure with multiple layers of meaning.")
            elif themes_found > 0:
                insights.append("💭 Clear thematic focus that will provide food for thought.")
            
            # Quote insights
            quotes_found = analysis.get('quotes_extracted', 0)
            if quotes_found > 20:
                insights.append("💎 Rich in memorable passages and quotable moments.")
            
            return "\n\n".join(insights)
        except Exception as e:
            return f"Error generating insights: {e}"
    
    def update_characters_tab(self, result):
        """FIXED - Update characters analysis tab with better debugging"""
        if not self.ebook_system or not self.current_book_id:
            return
        
        try:
            # Try multiple ways to get book data
            book_data = None
            
            # Method 1: Try system's load method
            if hasattr(self.ebook_system, '_load_book_data'):
                try:
                    book_data = self.ebook_system._load_book_data(self.current_book_id)
                    print(f"DEBUG: Loaded book data via _load_book_data: {type(book_data)}")
                except Exception as e:
                    print(f"DEBUG: _load_book_data failed: {e}")
                    book_data = None
            
            # Method 2: Use result data directly
            if not book_data and result:
                book_data = {'analysis': result.get('analysis', {})}
                print(f"DEBUG: Using result data: {type(book_data)}")
            
            # Method 3: Try to get from system's library
            if not book_data and hasattr(self.ebook_system, 'get_book_library'):
                try:
                    books = self.ebook_system.get_book_library()
                    for book in books:
                        if book.get('id') == self.current_book_id:
                            book_data = book
                            break
                    print(f"DEBUG: Found book in library: {book_data is not None}")
                except Exception as e:
                    print(f"DEBUG: Library search failed: {e}")
            
            if not book_data:
                self.character_tree.clear()
                error_item = QTreeWidgetItem()
                error_item.setText(0, "No book data available")
                error_item.setText(1, "0")
                error_item.setText(2, "0.0")
                error_item.setText(3, "Check console for debug info")
                self.character_tree.addTopLevelItem(error_item)
                print(f"DEBUG: No book data found for ID: {self.current_book_id}")
                return
            
            # Extract characters from various possible locations
            characters = []
            
            # Try different data structures
            if 'analysis' in book_data:
                analysis = book_data['analysis']
                characters = analysis.get('characters', [])
                print(f"DEBUG: Found {len(characters)} characters in analysis")
            
            if not characters and 'characters' in book_data:
                characters = book_data['characters']
                print(f"DEBUG: Found {len(characters)} characters in root")
            
            if not characters:
                # Try to find any field that might contain character data
                for key, value in book_data.items():
                    if isinstance(value, list) and key.lower().find('char') != -1:
                        characters = value
                        print(f"DEBUG: Found characters in field '{key}': {len(characters)} items")
                        break
            
            print(f"DEBUG: Final characters list: {len(characters)} items")
            if characters:
                print(f"DEBUG: First character sample: {characters[0]}")
            
            self.character_tree.clear()
            
            if not characters:
                no_chars_item = QTreeWidgetItem()
                no_chars_item.setText(0, "No characters found")
                no_chars_item.setText(1, "0")
                no_chars_item.setText(2, "0.0")
                no_chars_item.setText(3, "Analysis may be incomplete or using different format")
                self.character_tree.addTopLevelItem(no_chars_item)
                return
            
            for i, char in enumerate(characters):
                item = QTreeWidgetItem()
                
                try:
                    print(f"DEBUG: Processing character {i}: {type(char)} - {char}")
                    
                    # Handle different character data formats
                    if isinstance(char, str):
                        # Character is just a string (name only)
                        char_name = char
                        char_mentions = 1
                        char_significance = 0.5
                        char_description = "Name only available"
                    elif isinstance(char, dict):
                        # Character is a dictionary - try multiple key combinations
                        char_name = (char.get('name') or 
                                   char.get('character') or 
                                   char.get('Character') or 
                                   char.get('char_name') or 
                                   'Unknown')
                        
                        char_mentions = (char.get('mentions') or 
                                       char.get('count') or 
                                       char.get('frequency') or 
                                       char.get('occurrences') or 0)
                        
                        char_significance = (char.get('significance_score') or 
                                           char.get('importance') or 
                                           char.get('score') or 
                                           char.get('significance') or 0.0)
                        
                        char_description = (char.get('description') or 
                                          char.get('details') or 
                                          char.get('info') or 
                                          char.get('summary') or 
                                          'No description')
                    else:
                        # Character is an object
                        char_name = self.safe_get_attr(char, 'name', 'Unknown')
                        char_mentions = self.safe_get_attr(char, 'mentions', 0)
                        char_significance = self.safe_get_attr(char, 'significance_score', 0.0)
                        char_description = self.safe_get_attr(char, 'description', 'No description')
                    
                    # Ensure data types are correct
                    char_name = str(char_name) if char_name is not None else "Unknown"
                    char_mentions = int(float(str(char_mentions))) if char_mentions not in [None, ''] else 0
                    char_significance = float(str(char_significance)) if char_significance not in [None, ''] else 0.0
                    char_description = str(char_description) if char_description is not None else "No description"
                    
                    item.setText(0, char_name)
                    item.setText(1, str(char_mentions))
                    item.setText(2, f"{char_significance:.2f}")
                    item.setText(3, char_description[:50] + ("..." if len(char_description) > 50 else ""))
                    
                    # Store data for details view
                    char_dict = {
                        'name': char_name,
                        'mentions': char_mentions,
                        'significance_score': char_significance,
                        'description': char_description
                    }
                    item.setData(0, Qt.UserRole, char_dict)
                    
                    self.character_tree.addTopLevelItem(item)
                    print(f"DEBUG: Successfully added character: {char_name}")
                    
                except Exception as e:
                    print(f"ERROR: Failed to process character {i}: {e}")
                    # Add error item for this character
                    error_item = QTreeWidgetItem()
                    error_item.setText(0, f"Error: {str(char)[:20]}...")
                    error_item.setText(1, "0")
                    error_item.setText(2, "0.0")
                    error_item.setText(3, f"Parse error: {str(e)[:20]}")
                    self.character_tree.addTopLevelItem(error_item)
                    continue
            
            # Connect selection handler
            self.character_tree.itemClicked.connect(self.display_character_details)
            print(f"DEBUG: Characters tab updated successfully with {self.character_tree.topLevelItemCount()} items")
            
        except Exception as e:
            print(f"ERROR: Major error updating characters tab: {e}")
            self.character_tree.clear()
            error_item = QTreeWidgetItem()
            error_item.setText(0, "Critical Error")
            error_item.setText(1, "0")
            error_item.setText(2, "0.0")
            error_item.setText(3, f"Error: {str(e)[:30]}")
            self.character_tree.addTopLevelItem(error_item)

    def display_character_details(self, item):
        """Display detailed character information"""
        try:
            char_data = item.data(0, Qt.UserRole)
            if char_data:
                details = f"**{char_data['name']}**\n\n"
                details += f"Mentions: {char_data['mentions']}\n"
                details += f"Significance: {char_data['significance_score']:.2f}\n\n"
                
                if char_data.get('description'):
                    details += f"Description: {char_data['description']}\n\n"
                    
                self.character_details.setPlainText(details)
        except Exception as e:
            self.character_details.setPlainText(f"Error displaying character details: {e}")
    
    def update_themes_tab(self, result):
        """FIXED - Update themes analysis tab with better debugging"""
        if not self.ebook_system or not self.current_book_id:
            return
            
        try:
            # Try multiple ways to get book data
            book_data = None
            
            # Method 1: Try system's load method
            if hasattr(self.ebook_system, '_load_book_data'):
                try:
                    book_data = self.ebook_system._load_book_data(self.current_book_id)
                    print(f"DEBUG THEMES: Loaded book data via _load_book_data: {type(book_data)}")
                except Exception as e:
                    print(f"DEBUG THEMES: _load_book_data failed: {e}")
                    book_data = None
            
            # Method 2: Use result data directly
            if not book_data and result:
                book_data = {'analysis': result.get('analysis', {})}
                print(f"DEBUG THEMES: Using result data: {type(book_data)}")
            
            # Method 3: Try to get from system's library
            if not book_data and hasattr(self.ebook_system, 'get_book_library'):
                try:
                    books = self.ebook_system.get_book_library()
                    for book in books:
                        if book.get('id') == self.current_book_id:
                            book_data = book
                            break
                    print(f"DEBUG THEMES: Found book in library: {book_data is not None}")
                except Exception as e:
                    print(f"DEBUG THEMES: Library search failed: {e}")
            
            if not book_data:
                self.theme_tree.clear()
                error_item = QTreeWidgetItem()
                error_item.setText(0, "No book data available")
                error_item.setText(1, "0.0")
                error_item.setText(2, "0 chapters")
                error_item.setText(3, "Check console for debug info")
                self.theme_tree.addTopLevelItem(error_item)
                print(f"DEBUG THEMES: No book data found for ID: {self.current_book_id}")
                return
            
            # Extract themes from various possible locations
            themes = []
            
            # Try different data structures
            if 'analysis' in book_data:
                analysis = book_data['analysis']
                themes = analysis.get('themes', [])
                print(f"DEBUG THEMES: Found {len(themes)} themes in analysis")
            
            if not themes and 'themes' in book_data:
                themes = book_data['themes']
                print(f"DEBUG THEMES: Found {len(themes)} themes in root")
            
            if not themes:
                # Try to find any field that might contain theme data
                for key, value in book_data.items():
                    if isinstance(value, list) and key.lower().find('theme') != -1:
                        themes = value
                        print(f"DEBUG THEMES: Found themes in field '{key}': {len(themes)} items")
                        break
            
            print(f"DEBUG THEMES: Final themes list: {len(themes)} items")
            if themes:
                print(f"DEBUG THEMES: First theme sample: {themes[0]}")
            
            self.theme_tree.clear()
            
            if not themes:
                no_themes_item = QTreeWidgetItem()
                no_themes_item.setText(0, "No themes found")
                no_themes_item.setText(1, "0.0")
                no_themes_item.setText(2, "0 chapters")
                no_themes_item.setText(3, "Analysis may be incomplete or using different format")
                self.theme_tree.addTopLevelItem(no_themes_item)
                return
            
            for i, theme in enumerate(themes):
                item = QTreeWidgetItem()
                
                try:
                    print(f"DEBUG THEMES: Processing theme {i}: {type(theme)} - {theme}")
                    
                    # Handle different theme data formats
                    if isinstance(theme, str):
                        # Theme is just a string
                        theme_name = theme
                        theme_strength = 0.5
                        theme_chapters = []
                        theme_evidence = []
                    elif isinstance(theme, dict):
                        # Theme is a dictionary - try multiple key combinations
                        theme_name = (theme.get('theme') or 
                                    theme.get('name') or 
                                    theme.get('Theme') or 
                                    theme.get('topic') or 
                                    'Unknown Theme')
                        
                        theme_strength = (theme.get('strength') or 
                                        theme.get('score') or 
                                        theme.get('importance') or 
                                        theme.get('weight') or 0.0)
                        
                        theme_chapters = (theme.get('chapters') or 
                                        theme.get('locations') or 
                                        theme.get('chapter_list') or 
                                        theme.get('found_in') or [])
                        
                        theme_evidence = (theme.get('evidence') or 
                                        theme.get('examples') or 
                                        theme.get('quotes') or 
                                        theme.get('supporting_text') or [])
                    else:
                        # Theme is an object
                        theme_name = self.safe_get_attr(theme, 'theme', self.safe_get_attr(theme, 'name', 'Unknown Theme'))
                        theme_strength = self.safe_get_attr(theme, 'strength', self.safe_get_attr(theme, 'score', 0.0))
                        theme_chapters = self.safe_get_attr(theme, 'chapters', self.safe_get_attr(theme, 'locations', []))
                        theme_evidence = self.safe_get_attr(theme, 'evidence', self.safe_get_attr(theme, 'examples', []))
                    
                    # Ensure data types are correct
                    theme_name = str(theme_name) if theme_name is not None else "Unknown Theme"
                    theme_strength = float(str(theme_strength)) if theme_strength not in [None, ''] else 0.0
                    theme_chapters = list(theme_chapters) if theme_chapters is not None else []
                    theme_evidence = list(theme_evidence) if theme_evidence is not None else []
                    
                    item.setText(0, theme_name)
                    item.setText(1, f"{theme_strength:.2f}")
                    item.setText(2, f"{len(theme_chapters)} chapters")
                    item.setText(3, f"{len(theme_evidence)} evidence")
                    
                    # Store data for details view
                    theme_dict = {
                        'theme': theme_name,
                        'strength': theme_strength,
                        'chapters': theme_chapters,
                        'evidence': theme_evidence
                    }
                    item.setData(0, Qt.UserRole, theme_dict)
                    
                    self.theme_tree.addTopLevelItem(item)
                    print(f"DEBUG THEMES: Successfully added theme: {theme_name}")
                    
                except Exception as e:
                    print(f"ERROR THEMES: Failed to process theme {i}: {e}")
                    # Add error item for this theme
                    error_item = QTreeWidgetItem()
                    error_item.setText(0, f"Error: {str(theme)[:20]}...")
                    error_item.setText(1, "0.0")
                    error_item.setText(2, "0 chapters")
                    error_item.setText(3, f"Parse error: {str(e)[:20]}")
                    self.theme_tree.addTopLevelItem(error_item)
                    continue
            
            # Connect selection handler
            self.theme_tree.itemClicked.connect(self.display_theme_details)
            print(f"DEBUG THEMES: Themes tab updated successfully with {self.theme_tree.topLevelItemCount()} items")
            
        except Exception as e:
            print(f"ERROR THEMES: Major error updating themes tab: {e}")
            self.theme_tree.clear()
            error_item = QTreeWidgetItem()
            error_item.setText(0, "Critical Error")
            error_item.setText(1, "0.0")
            error_item.setText(2, "0 chapters")
            error_item.setText(3, f"Error: {str(e)[:30]}")
            self.theme_tree.addTopLevelItem(error_item)

    def display_theme_details(self, item):
        """Display detailed theme information"""
        try:
            theme_data = item.data(0, Qt.UserRole)
            if theme_data:
                details = f"**{theme_data['theme']}**\n\n"
                details += f"Strength: {theme_data['strength']:.2f}\n"
                details += f"Present in chapters: {', '.join(map(str, theme_data['chapters']))}\n\n"
                
                details += "Evidence:\n"
                for evidence in theme_data['evidence'][:5]:
                    details += f"• {evidence}\n"
                    
                self.theme_details.setPlainText(details)
        except Exception as e:
            self.theme_details.setPlainText(f"Error displaying theme details: {e}")
    
    def update_emotions_tab(self, result):
        """FIXED - Update emotional arc analysis tab"""
        if not self.ebook_system or not self.current_book_id:
            return
            
        try:
            # Try to get book data safely
            if hasattr(self.ebook_system, '_load_book_data'):
                book_data = self.ebook_system._load_book_data(self.current_book_id)
            else:
                # Fallback to result data
                book_data = {'analysis': result.get('analysis', {})}
            
            if not book_data:
                self.emotion_summary.setPlainText("No book data available for emotional analysis.")
                self.emotion_timeline.clear()
                return
            
            emotional_arc = book_data.get('analysis', {}).get('emotional_arc', [])
            
            if not emotional_arc:
                self.emotion_summary.setPlainText("No emotional analysis available for this book.")
                self.emotion_timeline.clear()
                return
            
            # Process emotions safely
            emotions_by_type = {}
            timeline_data = []
            
            for ep in emotional_arc:
                try:
                    # Handle different emotion data formats
                    if isinstance(ep, str):
                        # Emotion is just a string
                        emotion = ep
                        intensity = 0.5  # Default intensity
                        chapter = 0
                        trigger = "Unknown"
                    elif isinstance(ep, dict):
                        # Emotion is a dictionary
                        emotion = ep.get('emotion', ep.get('feeling', ep.get('type', 'unknown')))
                        intensity = ep.get('intensity', ep.get('strength', ep.get('score', 0.0)))
                        chapter = ep.get('chapter', ep.get('location', ep.get('position', 0)))
                        trigger = ep.get('trigger', ep.get('cause', ep.get('context', 'unknown')))
                    else:
                        # Emotion is an object
                        emotion = self.safe_get_attr(ep, 'emotion', self.safe_get_attr(ep, 'feeling', 'unknown'))
                        intensity = self.safe_get_attr(ep, 'intensity', self.safe_get_attr(ep, 'strength', 0.0))
                        chapter = self.safe_get_attr(ep, 'chapter', self.safe_get_attr(ep, 'location', 0))
                        trigger = self.safe_get_attr(ep, 'trigger', self.safe_get_attr(ep, 'cause', 'unknown'))
                    
                    # Ensure data types are correct
                    emotion = str(emotion) if emotion is not None else 'unknown'
                    intensity = float(intensity) if intensity is not None else 0.0
                    chapter = int(chapter) if chapter is not None else 0
                    trigger = str(trigger) if trigger is not None else 'unknown'
                    
                    # Collect for summary
                    if emotion not in emotions_by_type:
                        emotions_by_type[emotion] = []
                    emotions_by_type[emotion].append(intensity)
                    
                    # Collect for timeline
                    timeline_data.append({
                        'emotion': emotion,
                        'intensity': intensity,
                        'chapter': chapter,
                        'trigger': trigger
                    })
                    
                except Exception as e:
                    print(f"Error processing emotion point: {e}")
                    continue
            
            # Create summary
            summary_parts = []
            for emotion, intensities in emotions_by_type.items():
                if intensities:
                    avg_intensity = sum(intensities) / len(intensities)
                    summary_parts.append(f"{emotion.title()}: {avg_intensity:.2f} avg ({len(intensities)} times)")
            
            self.emotion_summary.setPlainText("\n".join(summary_parts) if summary_parts else "No emotional data")
            
            # Create timeline
            self.emotion_timeline.clear()
            
            if not timeline_data:
                no_emotions_item = QTreeWidgetItem()
                no_emotions_item.setText(0, "No emotional timeline available")
                self.emotion_timeline.addTopLevelItem(no_emotions_item)
                return
            
            # Group by chapter
            by_chapter = {}
            for item in timeline_data:
                chapter = item['chapter']
                if chapter not in by_chapter:
                    by_chapter[chapter] = []
                by_chapter[chapter].append(item)
            
            for chapter in sorted(by_chapter.keys()):
                chapter_item = QTreeWidgetItem()
                chapter_item.setText(0, f"Chapter {chapter}")
                
                chapter_emotions = by_chapter[chapter]
                if chapter_emotions:
                    dominant = max(chapter_emotions, key=lambda x: x['intensity'])
                    chapter_item.setText(1, dominant['emotion'].title())
                    chapter_item.setText(2, f"{dominant['intensity']:.2f}")
                    chapter_item.setText(3, dominant['trigger'][:50])
                
                self.emotion_timeline.addTopLevelItem(chapter_item)
            
        except Exception as e:
            print(f"Error updating emotions tab: {e}")
            self.emotion_summary.setPlainText(f"Error loading emotional analysis: {str(e)}")
            self.emotion_timeline.clear()

    def update_quotes_tab(self, result):
        """FIXED - Update quotes collection tab"""
        if not self.ebook_system or not self.current_book_id:
            return
            
        try:
            # Try to get book data safely
            if hasattr(self.ebook_system, '_load_book_data'):
                book_data = self.ebook_system._load_book_data(self.current_book_id)
            else:
                # Fallback to result data
                book_data = {'analysis': result.get('analysis', {})}
            
            if not book_data:
                self.quotes_list.clear()
                error_item = QListWidgetItem()
                error_item.setText("No book data available")
                self.quotes_list.addItem(error_item)
                return
            
            quotes = book_data.get('analysis', {}).get('quotes', [])
            self.quotes_list.clear()
            
            if not quotes:
                no_quotes_item = QListWidgetItem()
                no_quotes_item.setText("No quotes found - analysis may be incomplete")
                self.quotes_list.addItem(no_quotes_item)
                return
            
            for quote in quotes:
                try:
                    quote_text = self.safe_get_attr(quote, 'text', 'No text')
                    quote_chapter = self.safe_get_attr(quote, 'chapter', 0)
                    
                    display_text = str(quote_text)
                    if len(display_text) > 80:
                        display_text = display_text[:77] + "..."
                    
                    item = QListWidgetItem()
                    item.setText(f"Ch.{quote_chapter}: \"{display_text}\"")
                    
                    # Store quote data
                    quote_dict = {
                        'text': str(quote_text),
                        'chapter': int(quote_chapter),
                        'emotional_impact': self.safe_get_attr(quote, 'emotional_impact', 'unknown'),
                        'significance_score': self.safe_get_attr(quote, 'significance_score', 0.0)
                    }
                    item.setData(Qt.UserRole, quote_dict)
                    
                    self.quotes_list.addItem(item)
                    
                except Exception as e:
                    print(f"Error processing quote: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error updating quotes tab: {e}")
            self.quotes_list.clear()
            error_item = QListWidgetItem()
            error_item.setText(f"Error loading quotes: {str(e)[:50]}")
            self.quotes_list.addItem(error_item)

    def display_quote_details(self, item):
        """Display detailed quote information"""
        try:
            quote_data = item.data(Qt.UserRole)
            if quote_data:
                details = f"Chapter {quote_data['chapter']}\n"
                details += f"Emotional Impact: {quote_data.get('emotional_impact', 'Not analyzed')}\n"
                details += f"Significance: {quote_data.get('significance_score', 0):.2f}\n\n"
                details += f"\"{quote_data['text']}\"\n"
                
                self.quote_details.setPlainText(details)
        except Exception as e:
            self.quote_details.setPlainText(f"Error displaying quote details: {e}")
    
    def add_quote_annotation(self):
        """Add annotation to selected quote"""
        try:
            current_item = self.quotes_list.currentItem()
            if not current_item or not self.current_book_id:
                return
                
            annotation_text = self.annotation_input.text().strip()
            if not annotation_text:
                return
                
            quote_data = current_item.data(Qt.UserRole)
            if quote_data and self.ebook_system:
                # Add annotation to the system if method exists
                if hasattr(self.ebook_system, 'add_annotation'):
                    success = self.ebook_system.add_annotation(
                        self.current_book_id,
                        quote_data['chapter'],
                        quote_data['text'],
                        annotation_text
                    )
                else:
                    # Fallback - just save locally
                    success = self.save_annotation_locally(quote_data, annotation_text)
                
                if success:
                    self.annotation_input.clear()
                    
                    # Update display
                    current_details = self.quote_details.toPlainText()
                    updated_details = current_details + f"\n\nYour Note: {annotation_text}"
                    self.quote_details.setPlainText(updated_details)
                    
                    QMessageBox.information(self, "Annotation Added", "Your note has been saved!")
        except Exception as e:
            QMessageBox.critical(self, "Annotation Error", f"Failed to add annotation: {e}")

    def save_annotation_locally(self, quote_data, annotation_text):
        """Save annotation locally as fallback"""
        try:
            annotations_dir = Path("logs/annotations")
            annotations_dir.mkdir(exist_ok=True)
            
            annotation_file = annotations_dir / f"{self.current_book_id}_annotations.json"
            
            # Load existing annotations
            if annotation_file.exists():
                with open(annotation_file, 'r', encoding='utf-8') as f:
                    annotations = json.load(f)
            else:
                annotations = []
            
            # Add new annotation
            new_annotation = {
                'quote': quote_data['text'],
                'chapter': quote_data['chapter'],
                'annotation': annotation_text,
                'timestamp': datetime.datetime.now().isoformat()
            }
            annotations.append(new_annotation)
            
            # Save annotations
            with open(annotation_file, 'w', encoding='utf-8') as f:
                json.dump(annotations, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving annotation locally: {e}")
            return False
    
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
        
        # Start discussion worker if method exists
        if hasattr(self.ebook_system, 'ask_about_book'):
            self.discussion_worker = BookDiscussionWorker(
                self.current_book_id, 
                question, 
                self.ebook_system
            )
            self.discussion_worker.response_ready.connect(self.display_discussion_response)
            self.discussion_worker.start()
        else:
            # Fallback response
            self.display_discussion_response("I'm sorry, but the discussion feature is not available with the current ebook system.")
    
    def display_discussion_response(self, response):
        """Display EchoMind's response to the question"""
        try:
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
        except Exception as e:
            self.discussion_history.append(f"🤖 EchoMind: Error displaying response: {e}\n")
    
    def load_preset_question(self, question):
        """Load a preset question"""
        if question and question != "":
            self.question_input.setText(question)
    
    def update_journal_tab(self):
        """Update the reading journal display with better debugging"""
        if not self.current_book_id or not self.ebook_system:
            self.journal_display.setPlainText("No book selected or system unavailable")
            return

        try:
            print(f"DEBUG JOURNAL: Updating journal for book ID: {self.current_book_id}")
            journal_content = None

            # Try method 1
            if hasattr(self.ebook_system, 'export_reading_journal'):
                try:
                    journal_content = self.ebook_system.export_reading_journal(self.current_book_id)
                    if isinstance(journal_content, dict):
                        journal_content = json.dumps(journal_content, indent=2, ensure_ascii=False)
                    elif not isinstance(journal_content, str):
                        journal_content = str(journal_content)
                    print(f"DEBUG JOURNAL: Got journal: {len(journal_content)} chars")
                except Exception as e:
                    print(f"DEBUG JOURNAL: export_reading_journal failed: {e}")

            # Method 2
            if not journal_content:
                try:
                    book_data = None
                    if hasattr(self.ebook_system, '_load_book_data'):
                        book_data = self.ebook_system._load_book_data(self.current_book_id)

                    if not book_data and hasattr(self.ebook_system, 'get_book_library'):
                        books = self.ebook_system.get_book_library()
                        for book in books:
                            if book.get('id') == self.current_book_id:
                                book_data = book
                                break

                    if book_data:
                        journal_content = self.create_detailed_journal_entry(book_data)
                        print(f"DEBUG JOURNAL: Created detailed journal: {len(journal_content)} chars")
                    else:
                        print("DEBUG JOURNAL: No book data found for detailed journal")
                except Exception as e:
                    print(f"DEBUG JOURNAL: Failed to create detailed journal: {e}")

            # Method 3
            if not journal_content:
                journal_content = self.create_basic_journal_entry()
                print("DEBUG JOURNAL: Created basic journal entry")

            self.journal_display.setPlainText(journal_content or "Unable to generate journal entry")

        except Exception as e:
            print(f"ERROR JOURNAL: Major error updating journal: {e}")
            self.journal_display.setPlainText(f"Error loading journal: {e}")


    def create_basic_journal_entry(self):
        """Create a basic journal entry when full system is unavailable"""
        try:
            if not self.current_book_id:
                return "No book selected for journal entry."
                
            # Create a simple journal entry
            journal_text = f"📖 BASIC READING LOG\n{'='*50}\n\n"
            journal_text += f"Book ID: {self.current_book_id}\n"
            journal_text += f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Try to get basic info from UI elements
            if hasattr(self, 'book_title_label'):
                title = self.book_title_label.text()
                if title and title != "No book selected":
                    journal_text += f"Title: {title}\n\n"
            
            if hasattr(self, 'book_details'):
                details = self.book_details.toPlainText()
                if details:
                    journal_text += f"Book Details:\n{details}\n\n"
            
            # Add analysis summary if available
            if hasattr(self, 'current_analysis') and self.current_analysis:
                journal_text += f"ANALYSIS SUMMARY\n{'-'*30}\n"
                journal_text += f"Characters Found: {self.current_analysis.get('characters_found', 0)}\n"
                journal_text += f"Themes Identified: {self.current_analysis.get('themes_identified', 0)}\n"
                journal_text += f"Quotes Extracted: {self.current_analysis.get('quotes_extracted', 0)}\n\n"
            
            # Try to include personal notes
            journal_text += f"PERSONAL NOTES\n{'-'*30}\n"
            try:
                notes_file = Path("logs/book_notes") / f"{self.current_book_id}_notes.txt"
                if notes_file.exists():
                    with open(notes_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "-" * 50 in content:
                            notes_part = content.split("-" * 50, 1)[1].strip()
                            journal_text += notes_part + "\n"
                        else:
                            journal_text += content + "\n"
                else:
                    journal_text += "No personal notes yet. Use the Personal Notes section to add your thoughts.\n"
            except Exception as e:
                journal_text += f"Error loading personal notes: {e}\n"
            
            journal_text += f"\n{'-'*50}\n"
            journal_text += "Note: This is a basic journal entry. Full journaling features may not be available with the current ebook system.\n"
            journal_text += f"{'='*50}\n"
            
            return journal_text
        except Exception as e:
            return f"Error creating basic journal entry: {e}"
    
    def export_reading_journal(self):
        """Export the complete reading journal"""
        if not self.ebook_system:
            QMessageBox.warning(self, "System Error", "EBook system not available")
            return
            
        try:
            # Try to get journal from system
            if hasattr(self.ebook_system, 'export_reading_journal'):
                journal = self.ebook_system.export_reading_journal()
            else:
                # Fallback to current display
                journal = self.journal_display.toPlainText()
                if not journal:
                    journal = "No journal data available for export."
            
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
            QMessageBox.warning(self, "System Error", "EBook system not available")
            return
            
        try:
            # Get complete journal with better error handling
            if hasattr(self.ebook_system, 'get_book_library'):
                books = self.ebook_system.get_book_library()
                if books:
                    simple_journal = "📚 MY READING HISTORY\n\n"
                    for book in books[:10]:  # Last 10 books
                        # Safe access to book data
                        title = book.get('title', 'Unknown Title') if isinstance(book, dict) else str(book)
                        author = book.get('author', 'Unknown Author') if isinstance(book, dict) else 'Unknown Author'
                        date = book.get('ingestion_date', 'Unknown Date') if isinstance(book, dict) else 'Unknown Date'
                        
                        simple_journal += f"📖 '{title}' by {author}\n"
                        simple_journal += f"   Added: {date[:10] if date != 'Unknown Date' else 'Unknown'}\n\n"
                    
                    self.journal_display.setPlainText(simple_journal)
                else:
                    self.journal_display.setPlainText("No books found in library.")
            else:
                self.journal_display.setPlainText("Library access not available. Individual book analysis is still accessible in other tabs.")
                
        except Exception as e:
            print(f"Journal error: {e}")
            self.journal_display.setPlainText("Journal temporarily unavailable. Book analysis is still accessible in other tabs.")
    
    def get_reading_recommendations(self):
        """Get personalized reading recommendations"""
        if not self.ebook_system:
            QMessageBox.warning(self, "System Error", "EBook system not available")
            return
            
        try:
            if hasattr(self.ebook_system, 'get_reading_recommendations'):
                recommendations = self.ebook_system.get_reading_recommendations()
                
                rec_text = "📚 **Personalized Reading Recommendations**\n\n"
                for i, rec in enumerate(recommendations, 1):
                    rec_text += f"{i}. {rec}\n\n"
                
                self.journal_display.setPlainText(rec_text)
            else:
                # Provide generic recommendations
                generic_recs = [
                    "Based on your reading history, try exploring different genres",
                    "Consider books with similar themes to your favorites",
                    "Look for authors recommended by readers of your preferred books",
                    "Try books with different reading levels to expand your skills"
                ]
                
                rec_text = "📚 **General Reading Recommendations**\n\n"
                for i, rec in enumerate(generic_recs, 1):
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
            QMessageBox.information(self, "No Notes", "Please enter some notes before saving.")
            return
            
        try:
            # Save notes
            notes_dir = Path("logs/book_notes")
            notes_dir.mkdir(parents=True, exist_ok=True)
            
            notes_file = notes_dir / f"{self.current_book_id}_notes.txt"
            
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
            if hasattr(self.ebook_system, 'get_book_library'):
                books = self.ebook_system.get_book_library()
                
                self.library_list.clear()
                
                if not books:
                    no_books_item = QListWidgetItem()
                    no_books_item.setText("📚 No books in library - load a book to get started!")
                    self.library_list.addItem(no_books_item)
                    return
                
                for book in books:
                    item = QListWidgetItem()
                    
                    # Safe access to book data
                    title = book.get('title', 'Unknown Title')
                    author = book.get('author', 'Unknown Author')
                    reading_progress = book.get('reading_progress', 0.0)
                    genre_hints = book.get('genre_hints', [])
                    reading_level = book.get('reading_level', 0.0)
                    
                    # Format display text
                    progress_indicator = "✅" if reading_progress > 0.9 else "📖" if reading_progress > 0 else "📚"
                    display_text = f"{progress_indicator} {title}"
                    
                    if author != "Unknown Author":
                        display_text += f" - {author}"
                    
                    # Add genre hints if available
                    if genre_hints:
                        display_text += f" ({', '.join(genre_hints[:2])})"
                    
                    item.setText(display_text)
                    item.setData(Qt.UserRole, book)
                    
                    # Color coding based on reading level
                    if reading_level > 15:
                        item.setForeground(QColor("#ff6b6b"))  # Red for difficult
                    elif reading_level < 8:
                        item.setForeground(QColor("#98fb98"))  # Green for easy
                    else:
                        item.setForeground(QColor("#87ceeb"))  # Blue for moderate
                    
                    self.library_list.addItem(item)
            else:
                # System doesn't have library functionality
                self.library_list.clear()
                no_lib_item = QListWidgetItem()
                no_lib_item.setText("📚 Library feature not available with current system")
                self.library_list.addItem(no_lib_item)
                
        except Exception as e:
            print(f"Error refreshing library: {e}")
            self.library_list.clear()
            error_item = QListWidgetItem()
            error_item.setText(f"📚 Error loading library: {str(e)[:50]}")
            self.library_list.addItem(error_item)
    
    def select_book_from_library(self, item):
        """Select a book from the library"""
        try:
            book_data = item.data(Qt.UserRole)
            if book_data and self.ebook_system:
                book_id = book_data.get('id')
                if not book_id:
                    QMessageBox.warning(self, "Selection Error", "Invalid book data")
                    return
                    
                self.current_book_id = book_id
                
                # Load full book data
                if hasattr(self.ebook_system, '_load_book_data'):
                    full_book_data = self.ebook_system._load_book_data(self.current_book_id)
                    if full_book_data:
                        # Create a result-like structure for consistency
                        result = {
                            'book_id': self.current_book_id,
                            'metadata': full_book_data.get('metadata', {}),
                            'analysis_summary': {
                                'characters_found': len(full_book_data.get('analysis', {}).get('characters', [])),
                                'themes_identified': len(full_book_data.get('analysis', {}).get('themes', [])),
                                'quotes_extracted': len(full_book_data.get('analysis', {}).get('quotes', [])),
                                'emotional_data_points': len(full_book_data.get('analysis', {}).get('emotional_arc', [])),
                                'genre_hints': full_book_data.get('analysis', {}).get('genre_hints', []),
                                'reading_level': full_book_data.get('metadata', {}).get('reading_level', 0.0),
                                'writing_style_summary': full_book_data.get('analysis', {}).get('writing_style', {}).get('style_description', 'Not analyzed')
                            },
                            'analysis': full_book_data.get('analysis', {})
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
                    else:
                        QMessageBox.warning(self, "Load Error", "Could not load full book data")
                else:
                    # Fallback - use library data directly
                    self.current_book_id = book_id
                    self.book_title_label.setText(book_data.get('title', 'Unknown Title'))
                    self.book_details.setPlainText(f"Author: {book_data.get('author', 'Unknown')}\nLimited data available")
                    
        except Exception as e:
            QMessageBox.warning(self, "Selection Error", f"Failed to select book:\n{e}")
    
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
                        self.personal_notes.setPlainText(content)
            else:
                self.personal_notes.clear()
                
        except Exception as e:
            print(f"Error loading personal notes: {e}")
            self.personal_notes.clear()
    
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
            
            if not book1_data or not book2_data:
                QMessageBox.warning(self, "Comparison Error", "Invalid book selection")
                return
            
            # Try to use system comparison if available
            if hasattr(self.ebook_system, 'compare_books'):
                comparison = self.ebook_system.compare_books(book1_data.get('id'), book2_data.get('id'))
            else:
                # Fallback comparison
                comparison = self.create_basic_comparison(book1_data, book2_data)
            
            # Show comparison in a dialog
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Book Comparison")
            dialog.setText("Comparison Analysis")
            dialog.setDetailedText(comparison)
            dialog.setStandardButtons(QMessageBox.Ok)
            
            # Make dialog larger
            dialog.resize(600, 400)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Comparison Error", f"Failed to compare books:\n{e}")

    def create_basic_comparison(self, book1_data, book2_data):
        """Create a basic comparison when system method is unavailable"""
        try:
            comparison = f"BOOK COMPARISON\n\n"
            
            # Book 1
            comparison += f"📖 BOOK 1: {book1_data.get('title', 'Unknown')}\n"
            comparison += f"   Author: {book1_data.get('author', 'Unknown')}\n"
            comparison += f"   Reading Level: {book1_data.get('reading_level', 0):.1f}\n"
            comparison += f"   Progress: {book1_data.get('reading_progress', 0)*100:.1f}%\n\n"
            
            # Book 2
            comparison += f"📖 BOOK 2: {book2_data.get('title', 'Unknown')}\n"
            comparison += f"   Author: {book2_data.get('author', 'Unknown')}\n"
            comparison += f"   Reading Level: {book2_data.get('reading_level', 0):.1f}\n"
            comparison += f"   Progress: {book2_data.get('reading_progress', 0)*100:.1f}%\n\n"
            
            # Basic comparison
            comparison += "COMPARISON NOTES:\n"
            
            level1 = book1_data.get('reading_level', 0)
            level2 = book2_data.get('reading_level', 0)
            
            if abs(level1 - level2) < 1:
                comparison += "• Similar reading difficulty levels\n"
            elif level1 > level2:
                comparison += f"• Book 1 is more challenging (Grade {level1:.1f} vs {level2:.1f})\n"
            else:
                comparison += f"• Book 2 is more challenging (Grade {level2:.1f} vs {level1:.1f})\n"
            
            # Genre comparison if available
            genres1 = book1_data.get('genre_hints', [])
            genres2 = book2_data.get('genre_hints', [])
            
            if genres1 and genres2:
                common_genres = set(genres1) & set(genres2)
                if common_genres:
                    comparison += f"• Share common genres: {', '.join(common_genres)}\n"
                else:
                    comparison += "• Different genre focuses\n"
            
            comparison += "\nNote: This is a basic comparison. Full comparison features may not be available."
            
            return comparison
            
        except Exception as e:
            return f"Error creating comparison: {e}"

def integrate_enhanced_ebook_gui(main_gui, ebook_system):
    """Integrate the enhanced ebook GUI into the main EchoMind GUI"""
    
    try:
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
        
    except Exception as e:
        print(f"❌ Error integrating enhanced ebook GUI: {e}")
        return None

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    test_widget = EnhancedEbookTab()
    test_widget.setWindowTitle("Enhanced EBook System - Test")
    test_widget.resize(1200, 800)
    test_widget.show()
    
    sys.exit(app.exec_())
