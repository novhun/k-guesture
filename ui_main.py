import sys
import cv2
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTabWidget,
                             QFormLayout, QMessageBox, QGroupBox, QGridLayout,
                             QScrollArea, QComboBox, QStatusBar, QMainWindow)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class MainWindowUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Translation Dictionary
        self.trans = {
            'English': {
                'title': 'K-Gesture: Sign Language Translator',
                'tab_translate': 'Real-time Translation',
                'tab_training': 'Training & Management',
                'tab_settings': 'Settings',
                'lbl_detect': 'Detecting Sign...',
                'lbl_khm': 'Khmer:',
                'lbl_eng': 'English:',
                'btn_capture': 'Capture Gesture',
                'lbl_status': 'Status:',
                'lbl_count': 'Total Gestures Trained:',
                'col_img': 'Image',
                'col_khm': 'Khmer',
                'col_eng': 'English',
                'col_audio': 'Audio',
                'col_act': 'Action',
                'set_cam': 'Camera Settings',
                'set_voice': 'Voice Settings',
                'set_ui': 'UI Settings',
                'ui_theme': 'Theme:',
                'ui_lang': 'UI Language:',
                'ui_font_size': 'Khmer Font Size:',
                'set_tracking': 'Tracking Settings',
                'track_face': 'Enable Face Tracking',
                'track_eye': 'Enable Eye Tracking (Iris)',
                'voice_eng': 'TTS Engine:',
                'voice_gen': 'Voice Gender:',
                'voice_lang': 'Playback Language:',
                'search_holder': 'Search gestures...'
            },
            'Khmer': {
                'title': 'K-Gesture: អ្នកបកប្រែភាសាសញ្ញា',
                'tab_translate': 'ការបកប្រែផ្ទាល់',
                'tab_training': 'ការបណ្តុះបណ្តាល និងគ្រប់គ្រង',
                'tab_settings': 'ការកំណត់',
                'lbl_detect': 'កំពុងស្វែងរកសញ្ញា...',
                'lbl_khm': 'ខ្មែរ:',
                'lbl_eng': 'អង់គ្លេស:',
                'btn_capture': 'រក្សាទុកសញ្ញា',
                'lbl_status': 'ស្ថានភាព:',
                'lbl_count': 'ចំនួនសញ្ញាសរុប:',
                'col_img': 'រូបភាព',
                'col_khm': 'ខ្មែរ',
                'col_eng': 'អង់គ្លេស',
                'col_audio': 'សំឡេង',
                'col_act': 'សកម្មភាព',
                'set_cam': 'ការកំណត់កាមេរ៉ា',
                'set_voice': 'ការកំណត់សំឡេង',
                'set_ui': 'ការកំណត់ UI',
                'ui_theme': 'ស្បែក (Theme):',
                'ui_lang': 'ភាសា UI:',
                'ui_font_size': 'ទំហំអក្សរខ្មែរ:',
                'set_tracking': 'ការកំណត់ការតាមដាន',
                'track_face': 'បើកការតាមដានផ្ទៃមុខ',
                'track_eye': 'បើកការតាមដានគ្រាប់ភ្នែក',
                'voice_eng': 'ម៉ាស៊ីនសំឡេង:',
                'voice_gen': 'ភេទសំឡេង:',
                'voice_lang': 'ភាសានិយាយ:',
                'search_holder': 'ស្វែងរកសញ្ញា...'
            }
        }
        
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("K-Gesture: Sign Language Translator")
        self.setMinimumSize(1000, 750)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Tab 1: Translation
        self.tab_translate = QWidget()
        self.setup_translation_tab()
        self.tabs.addTab(self.tab_translate, "Real-time Translation")
        
        # Tab 2: Training
        self.tab_training = QWidget()
        self.setup_training_tab()
        self.tabs.addTab(self.tab_training, "Training & Management")
        
        # Tab 3: Settings
        self.tab_settings = QWidget()
        self.setup_settings_tab()
        self.tabs.addTab(self.tab_settings, "Settings")

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("System Ready")

    def setup_translation_tab(self):
        layout = QHBoxLayout(self.tab_translate)
        
        # Left: Video
        left_layout = QVBoxLayout()
        self.lbl_video = QLabel()
        self.lbl_video.setStyleSheet("background-color: black; border-radius: 10px;")
        self.lbl_video.setFixedSize(640, 480)
        self.lbl_video.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.lbl_video)
        
        self.btn_capture = QPushButton("Capture Gesture")
        self.btn_capture.setFixedHeight(50)
        left_layout.addWidget(self.btn_capture)
        layout.addLayout(left_layout)
        
        # Right: Result
        right_layout = QVBoxLayout()
        self.lbl_detecting = QLabel("Detecting Sign...")
        self.lbl_detecting.setObjectName("subtitle")
        self.lbl_detecting.setStyleSheet("font-size: 24px; font-weight: bold;")
        right_layout.addWidget(self.lbl_detecting)
        
        # Labels
        res_group = QGroupBox("Result")
        res_layout = QGridLayout(res_group)
        
        self.lbl_khm_tag = QLabel("Khmer:")
        self.lbl_khmer_res = QLabel("-")
        self.lbl_khmer_res.setStyleSheet("font-size: 32px; font-weight: bold; color: #4CAF50;")
        
        self.lbl_eng_tag = QLabel("English:")
        self.lbl_english_res = QLabel("-")
        self.lbl_english_res.setStyleSheet("font-size: 24px; color: #2196F3;")
        
        res_layout.addWidget(self.lbl_khm_tag, 0, 0)
        res_layout.addWidget(self.lbl_khmer_res, 0, 1)
        res_layout.addWidget(self.lbl_eng_tag, 1, 0)
        res_layout.addWidget(self.lbl_english_res, 1, 1)
        
        right_layout.addWidget(res_group)
        
        # Quick Capture Inputs
        quick_group = QGroupBox("Quick Labeling")
        quick_layout = QFormLayout(quick_group)
        self.input_english = QLineEdit()
        self.input_khmer = QLineEdit()
        quick_layout.addRow("Eng Label:", self.input_english)
        quick_layout.addRow("Khm Label:", self.input_khmer)
        right_layout.addWidget(quick_group)
        
        right_layout.addStretch()
        layout.addLayout(right_layout)

    def setup_training_tab(self):
        layout = QVBoxLayout(self.tab_training)
        
        top_layout = QHBoxLayout()
        self.lbl_gesture_count = QLabel("Total Gestures Trained: 0")
        self.lbl_gesture_count.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(self.lbl_gesture_count)
        
        top_layout.addStretch()
        
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Search gestures...")
        self.input_search.setFixedWidth(250)
        top_layout.addWidget(self.input_search)
        
        layout.addLayout(top_layout)
        
        from PyQt5.QtWidgets import QTableWidget, QHeaderView
        self.table_gestures = QTableWidget()
        self.table_gestures.setColumnCount(5)
        self.table_gestures.setHorizontalHeaderLabels(["Image", "English", "Khmer", "Audio", "Action"])
        self.table_gestures.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_gestures.verticalHeader().setDefaultSectionSize(70)
        layout.addWidget(self.table_gestures)

    def setup_settings_tab(self):
        layout = QVBoxLayout(self.tab_settings)
        
        # Header
        self.lbl_settings_header = QLabel("System Settings")
        self.lbl_settings_header.setObjectName("setting_header")
        self.lbl_settings_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_settings_header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        
        # Camera Settings
        self.cam_group = QGroupBox("Camera Settings")
        cam_layout = QFormLayout(self.cam_group)
        self.combo_camera = QComboBox()
        cam_layout.addRow("Select Camera:", self.combo_camera)
        scroll_layout.addWidget(self.cam_group)
        
        # Voice Settings
        self.voice_group = QGroupBox("Voice Settings")
        voice_layout = QFormLayout(self.voice_group)
        
        self.combo_engine = QComboBox()
        self.combo_engine.addItems(["Edge-TTS", "gTTS"])
        voice_layout.addRow("TTS Engine:", self.combo_engine)
        
        self.combo_gender = QComboBox()
        self.combo_gender.addItems(["Male", "Female"])
        voice_layout.addRow("Voice Gender:", self.combo_gender)
        
        self.combo_language = QComboBox()
        self.combo_language.addItems(["Khmer", "English", "Both"])
        voice_layout.addRow("Playback Language:", self.combo_language)
        
        scroll_layout.addWidget(self.voice_group)

        # UI Settings
        self.ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout(self.ui_group)
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Dark", "Light"])
        ui_layout.addRow("Theme:", self.combo_theme)
        
        self.combo_ui_lang = QComboBox()
        self.combo_ui_lang.addItems(["English", "Khmer"])
        ui_layout.addRow("UI Language:", self.combo_ui_lang)
        
        self.combo_font_size = QComboBox()
        self.combo_font_size.addItem("Small (24px)", 24)
        self.combo_font_size.addItem("Medium (32px)", 32)
        self.combo_font_size.addItem("Large (48px)", 48)
        self.combo_font_size.addItem("Extra Large (64px)", 64)
        self.lbl_font_size_tag = QLabel("Khmer Font Size:")
        ui_layout.addRow(self.lbl_font_size_tag, self.combo_font_size)
        
        scroll_layout.addWidget(self.ui_group)
        
        # Tracking Settings
        from PyQt5.QtWidgets import QCheckBox
        self.tracking_group = QGroupBox("Tracking Settings")
        track_layout = QVBoxLayout(self.tracking_group)
        self.cb_enable_face = QCheckBox("Enable Face Tracking")
        self.cb_enable_eye = QCheckBox("Enable Eye Tracking (Iris)")
        track_layout.addWidget(self.cb_enable_face)
        track_layout.addWidget(self.cb_enable_eye)
        scroll_layout.addWidget(self.tracking_group)
        
        # Save Button
        self.btn_save_settings = QPushButton("Save Settings")
        scroll_layout.addWidget(self.btn_save_settings)
        
        scroll_layout.addStretch()
        container.setLayout(scroll_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def update_ui_language(self, lang):
        t = self.trans.get(lang, self.trans['English'])
        
        # Tabs
        self.tabs.setTabText(0, t['tab_translate'])
        self.tabs.setTabText(1, t['tab_training'])
        self.tabs.setTabText(2, t['tab_settings'])
        
        # Translation Tab
        self.btn_capture.setText(t['btn_capture'])
        self.lbl_detecting.setText(t['lbl_detect'])
        self.lbl_khm_tag.setText(t['lbl_khm'])
        self.lbl_eng_tag.setText(t['lbl_eng'])
        
        # Training Tab
        self.table_gestures.setHorizontalHeaderLabels([
            t['col_img'], t['col_eng'], t['col_khm'], t['col_audio'], t['col_act']
        ])
        self.input_search.setPlaceholderText(t['search_holder'])
        
        # Settings Groups
        self.cam_group.setTitle(t['set_cam'])
        self.voice_group.setTitle(t['set_voice'])
        self.ui_group.setTitle(t['set_ui'])
        self.tracking_group.setTitle(t['set_tracking'])
        self.cb_enable_face.setText(t['track_face'])
        self.cb_enable_eye.setText(t['track_eye'])
        self.lbl_font_size_tag.setText(t['ui_font_size'])
        self.lbl_settings_header.setText(t['tab_settings'])

    def update_frame(self, cv_img):
        """Updates the image_label with a new opencv image"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        self.lbl_video.setPixmap(QPixmap.fromImage(p))
