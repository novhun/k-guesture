import sys
import os
import cv2
import time
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from googletrans import Translator

# Internal imports
from ui_main import MainWindowUI
from gesture_recognizer import GestureRecognizer
from database import init_db, add_gesture, get_all_gestures, get_setting, set_setting
from audio_player import AudioPlayer
from utils import draw_khmer_text, write_current_gesture, clear_current_gesture
import styles

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ui = MainWindowUI()
        
        # Initialize Core Modules
        init_db()
        self.load_tracking_settings()
        self.recognizer = GestureRecognizer(use_face=self.enable_face, use_eye=self.enable_eye)
        self.audio_player = AudioPlayer()
        self.translator = Translator()
        
        # State
        self.stored_gestures = get_all_gestures()
        self.current_landmarks = None
        self.current_detected_gesture = None
        self.last_sync_time = 0
        self.current_font_size = 32
        
        # UI Signals
        self.ui.btn_capture.clicked.connect(self.save_gesture)
        self.ui.btn_save_settings.clicked.connect(self.save_settings)
        self.ui.combo_theme.currentTextChanged.connect(self.apply_theme)
        self.ui.combo_ui_lang.currentTextChanged.connect(self.apply_ui_language)
        self.ui.combo_font_size.currentIndexChanged.connect(self.apply_font_size)
        self.ui.input_search.textChanged.connect(self.filter_gestures)
        
        self.update_gesture_count()
        self.refresh_camera_list() # Scan cameras first
        self.load_settings()
        self.refresh_gestures() # Populate table on startup
        
        # OpenCV Camera
        self.camera_index = int(get_setting('camera_index', 0))
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Main Loop Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_video_feed)
        self.timer.start(30) # ~33 fps
        
    def process_video_feed(self):
        ret, frame = self.cap.read()
        if not ret:
            return
            
        # Flip frame horizontally for selfie view
        frame = cv2.flip(frame, 1)
        
        # Process MediaPipe
        processed_frame, landmarks = self.recognizer.process_frame(frame)
        self.current_landmarks = landmarks
        
        # Gesture Matching
        if landmarks:
            match = self.recognizer.compare_gestures(landmarks, self.stored_gestures, threshold=0.6)
            
            if match:
                self.current_detected_gesture = match
                eng_label = match['english']
                khm_label = match['khmer']
                
                processed_frame = draw_khmer_text(
                    processed_frame, 
                    khm_label, 
                    position=(50, 50), 
                    font_size=self.current_font_size, 
                    color=(0, 255, 0) # Green
                )
                
                self.ui.lbl_khmer_res.setText(khm_label)
                self.ui.lbl_english_res.setText(eng_label)
                
                # Play Audio based on language setting
                lang_setting = get_setting('voice_language', 'Khmer')
                if lang_setting == "Khmer":
                    self.audio_player.play_voice(khm_label, is_khmer=True, gesture_id=match['id'])
                elif lang_setting == "English":
                    self.audio_player.play_voice(eng_label, is_khmer=False, gesture_id=match['id'])
                elif lang_setting == "Both":
                    # Play Khmer then English sequentially
                    self.audio_player.play_voice_sequence([
                        (khm_label, True),
                        (eng_label, False)
                    ], gesture_id=match['id'])
                
                # Data Sync every 1 second
                current_time = time.time()
                if current_time - self.last_sync_time >= 1.0:
                    write_current_gesture(eng_label, khm_label)
                    self.last_sync_time = current_time
                    
            else:
                self.current_detected_gesture = None
                self.clear_ui()
        else:
            self.current_detected_gesture = None
            self.clear_ui()
            
        # Update Status Bar
        if landmarks:
            self.ui.status_bar.showMessage("Hand Detected", 2000)
        else:
            self.ui.status_bar.showMessage("Ready", 1000)

        # Update UI
        self.ui.update_frame(processed_frame)

    def clear_ui(self):
        self.ui.lbl_khmer_res.setText("-")
        self.ui.lbl_english_res.setText("-")

    def save_gesture(self):
        if not self.current_landmarks:
            QMessageBox.warning(self.ui, "Warning", "No hand detected. Please hold your hand in front of the camera.")
            return
            
        eng = self.ui.input_english.text().strip()
        khm = self.ui.input_khmer.text().strip()
        
        if not eng:
            QMessageBox.warning(self.ui, "Warning", "English label is required.")
            return
            
        # Auto-translate to Khmer if empty
        if not khm:
            try:
                translated = self.translator.translate(eng, src='en', dest='km')
                khm = translated.text
                self.ui.input_khmer.setText(khm)
            except Exception as e:
                QMessageBox.warning(self.ui, "Translation Error", f"Could not auto-translate: {e}")
                return
        
        # Save a sample image (Finger Style / Skeleton)
        image_path = None
        if self.current_landmarks:
            os.makedirs("data/samples", exist_ok=True)
            image_path = f"data/samples/{int(time.time())}_{eng}.jpg"
            # Generate black canvas with skeleton
            skeleton_img = self.recognizer.draw_landmarks_on_black_canvas(self.current_landmarks)
            cv2.imwrite(image_path, skeleton_img)
                
        # Save to DB
        add_gesture(eng, khm, self.current_landmarks, image_path)
        QMessageBox.information(self.ui, "Success", f"Gesture '{eng}' / '{khm}' saved successfully!")
        
        self.ui.input_english.clear()
        self.ui.input_khmer.clear()
        self.refresh_gestures()
        
    def refresh_gestures(self):
        self.stored_gestures = get_all_gestures()
        self.update_gesture_count()
        self.populate_gesture_list()
        
    def populate_gesture_list(self):
        self.ui.table_gestures.setRowCount(0)
        
        from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout
        from PyQt5.QtGui import QPixmap
        
        for gesture in self.stored_gestures:
            row_idx = self.ui.table_gestures.rowCount()
            self.ui.table_gestures.insertRow(row_idx)
            
            # 1. Thumbnail (Clickable to view)
            lbl_img = QLabel()
            lbl_img.setAlignment(Qt.AlignCenter)
            lbl_img.setCursor(Qt.PointingHandCursor)
            if gesture['image_path'] and os.path.exists(gesture['image_path']):
                pixmap = QPixmap(gesture['image_path']).scaled(60, 60, Qt.KeepAspectRatio)
                lbl_img.setPixmap(pixmap)
                lbl_img.mousePressEvent = lambda event, p=gesture['image_path']: self.view_image_action(p)
            else:
                lbl_img.setText("No Image")
            self.ui.table_gestures.setCellWidget(row_idx, 0, lbl_img)
            
            # 2. English
            self.ui.table_gestures.setItem(row_idx, 1, QTableWidgetItem(gesture['english']))
            
            # 3. Khmer
            self.ui.table_gestures.setItem(row_idx, 2, QTableWidgetItem(gesture['khmer']))
            
            # 4. Audio Status (Khmer & English)
            audio_container = QWidget()
            audio_layout = QVBoxLayout(audio_container)
            
            # Khmer Status
            khm_path = self.audio_player.get_audio_path(gesture['khmer'], is_khmer=True)
            if os.path.exists(khm_path):
                audio_layout.addWidget(QLabel("🇰🇭 Khmer: ✅"))
            else:
                btn_khm = QPushButton("Get Khmer")
                btn_khm.setStyleSheet("background-color: #FF9800; color: white; font-size: 10px;")
                btn_khm.clicked.connect(lambda checked, g=gesture: self.audio_player.play_voice(g['khmer'], is_khmer=True, gesture_id=g['id']))
                audio_layout.addWidget(btn_khm)
                
            # English Status
            eng_path = self.audio_player.get_audio_path(gesture['english'], is_khmer=False)
            if os.path.exists(eng_path):
                audio_layout.addWidget(QLabel("🇺🇸 English: ✅"))
            else:
                btn_eng = QPushButton("Get English")
                btn_eng.setStyleSheet("background-color: #03A9F4; color: white; font-size: 10px;")
                btn_eng.clicked.connect(lambda checked, g=gesture: self.audio_player.play_voice(g['english'], is_khmer=False, gesture_id=g['id']))
                audio_layout.addWidget(btn_eng)
            
            audio_layout.setContentsMargins(2, 2, 2, 2)
            self.ui.table_gestures.setCellWidget(row_idx, 3, audio_container)
            
            # 5. Action (Edit & Delete Buttons)
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            
            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px;")
            btn_edit.clicked.connect(lambda checked, g=gesture: self.edit_gesture_action(g))
            
            btn_del = QPushButton("Delete")
            btn_del.setStyleSheet("background-color: #f44336; color: white; border-radius: 5px; padding: 5px;")
            btn_del.clicked.connect(lambda checked, g=gesture: self.delete_gesture_action(g))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_del)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            self.ui.table_gestures.setCellWidget(row_idx, 4, btn_container)

    def filter_gestures(self):
        query = self.ui.input_search.text().lower()
        for row in range(self.ui.table_gestures.rowCount()):
            eng_item = self.ui.table_gestures.item(row, 1)
            khm_item = self.ui.table_gestures.item(row, 2)
            
            show = False
            if eng_item and query in eng_item.text().lower():
                show = True
            elif khm_item and query in khm_item.text().lower():
                show = True
                
            self.ui.table_gestures.setRowHidden(row, not show)

    def view_image_action(self, image_path):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout
        from PyQt5.QtGui import QPixmap
        
        dialog = QDialog(self.ui)
        dialog.setWindowTitle("Gesture Sample (Finger Style)")
        layout = QVBoxLayout(dialog)
        
        lbl_full = QLabel()
        pixmap = QPixmap(image_path)
        if pixmap.width() > 500 or pixmap.height() > 500:
            pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio)
        lbl_full.setPixmap(pixmap)
        
        layout.addWidget(lbl_full)
        dialog.exec_()

    def edit_gesture_action(self, gesture):
        from PyQt5.QtWidgets import QInputDialog, QLineEdit
        
        # Edit English
        new_eng, ok1 = QInputDialog.getText(self.ui, 'Edit Gesture', 'English Label:', QLineEdit.Normal, gesture['english'])
        if not ok1 or not new_eng:
            return
            
        # Edit Khmer
        new_khm, ok2 = QInputDialog.getText(self.ui, 'Edit Gesture', 'Khmer Label:', QLineEdit.Normal, gesture['khmer'])
        if not ok2 or not new_khm:
            return
            
        # Update DB
        from database import update_gesture_labels
        old_files = update_gesture_labels(gesture['id'], new_eng, new_khm)
        
        # Delete old voice files from disk
        for filepath in old_files:
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"Deleted old voice file: {filepath}")
                except Exception as e:
                    print(f"Error deleting file {filepath}: {e}")
                    
        QMessageBox.information(self.ui, "Success", "Gesture labels updated and old voice files removed!")
        self.refresh_gestures()

    def delete_gesture_action(self, gesture):
        reply = QMessageBox.question(self.ui, 'Delete', 
                                    f"Are you sure you want to delete '{gesture['english']}'?\n"
                                    "This will also delete the saved image and all voice files.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            from database import delete_gesture
            # This returns a list of all file paths (image and all audio versions)
            files_to_delete = delete_gesture(gesture['id'])
            
            # Delete every file from disk
            for filepath in files_to_delete:
                if filepath and os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        print(f"Deleted file: {filepath}")
                    except Exception as e:
                        print(f"Error deleting file {filepath}: {e}")
                        
            self.refresh_gestures()
            QMessageBox.information(self.ui, "Deleted", "Gesture and all associated files have been removed.")

    def update_gesture_count(self):
        self.ui.lbl_gesture_count.setText(f"Total Gestures Trained: {len(self.stored_gestures)}")

    def get_camera_names(self):
        """Attempts to get camera names on macOS using system_profiler."""
        import subprocess
        cameras = []
        try:
            # On macOS, system_profiler can give us camera names
            cmd = ["system_profiler", "SPCameraDataType"]
            output = subprocess.check_output(cmd).decode("utf-8")
            for line in output.split("\n"):
                if "Model ID:" not in line and ":" in line and line.strip().endswith(":"):
                    name = line.strip()[:-1]
                    if name and name not in ["Video", "Cameras"]:
                        cameras.append(name)
        except Exception:
            pass
        return cameras

    def refresh_camera_list(self):
        self.ui.combo_camera.clear()
        
        # Try to get real names
        names = self.get_camera_names()
        
        # Scan for available indices (0-4)
        available_indices = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_indices.append(i)
                cap.release()
        
        for i in available_indices:
            # Map index to name if possible, else use generic
            name = names[i] if i < len(names) else f"Camera {i}"
            self.ui.combo_camera.addItem(f"{name} (Index {i})", i)

    def load_settings(self):
        idx = int(get_setting('camera_index', '0'))
        # Find the index in the combobox data
        cb_index = self.ui.combo_camera.findData(idx)
        if cb_index >= 0:
            self.ui.combo_camera.setCurrentIndex(cb_index)
        
        engine = get_setting('tts_engine', 'Edge-TTS')
        eng_idx = self.ui.combo_engine.findText(engine)
        if eng_idx >= 0:
            self.ui.combo_engine.setCurrentIndex(eng_idx)
            
        lang = get_setting('voice_language', 'Khmer')
        l_idx = self.ui.combo_language.findText(lang)
        if l_idx >= 0:
            self.ui.combo_language.setCurrentIndex(l_idx)
        
        gender = get_setting('voice_gender', 'Male')
        index = self.ui.combo_gender.findText("Male" if gender == "Male" else "Female")
        if index >= 0:
            self.ui.combo_gender.setCurrentIndex(index)
            
        self.ui.cb_enable_face.setChecked(get_setting('enable_face_tracking', '0') == '1')
        self.ui.cb_enable_eye.setChecked(get_setting('enable_eye_tracking', '0') == '1')
        self.load_tracking_settings()

        # UI Settings
        theme = get_setting('ui_theme', 'Dark')
        t_idx = self.ui.combo_theme.findText(theme)
        if t_idx >= 0:
            self.ui.combo_theme.setCurrentIndex(t_idx)
            
        ui_lang = get_setting('ui_language', 'English')
        u_idx = self.ui.combo_ui_lang.findText(ui_lang)
        if u_idx >= 0:
            self.ui.combo_ui_lang.setCurrentIndex(u_idx)
            
        font_size = int(get_setting('khmer_font_size', '32'))
        f_idx = self.ui.combo_font_size.findData(font_size)
        if f_idx >= 0:
            self.ui.combo_font_size.setCurrentIndex(f_idx)
            
        self.apply_theme()
        self.apply_ui_language()
        self.apply_font_size()
        self.apply_voice_settings()

    def apply_voice_settings(self):
        engine = self.ui.combo_engine.currentText()
        self.audio_player.tts_engine = engine
        set_setting('tts_engine', engine)
        
        lang = self.ui.combo_language.currentText()
        set_setting('voice_language', lang)
        self.apply_tracking_settings()
        
        gender = self.ui.combo_gender.currentText()
        if gender == "Male":
            self.audio_player.khmer_voice = "km-KH-PisethNeural"
            self.audio_player.english_voice = "en-US-GuyNeural"
            set_setting('voice_gender', 'Male')
        else:
            self.audio_player.khmer_voice = "km-KH-SreymomNeural"
            self.audio_player.english_voice = "en-US-AriaNeural"
            set_setting('voice_gender', 'Female')

    def apply_theme(self):
        theme = self.ui.combo_theme.currentText()
        set_setting('ui_theme', theme)
        
        if theme == "Dark":
            self.app.setStyleSheet(styles.DARK_THEME)
        elif theme == "Light":
            self.app.setStyleSheet(styles.LIGHT_THEME)
        else:
            # System (Default to dark for now or clear)
            self.app.setStyleSheet(styles.DARK_THEME)

    def apply_ui_language(self):
        lang = self.ui.combo_ui_lang.currentText()
        set_setting('ui_language', lang)
        self.ui.update_ui_language(lang)
        self.update_gesture_count()

    def apply_font_size(self):
        self.current_font_size = self.ui.combo_font_size.currentData()
        if self.current_font_size:
            set_setting('khmer_font_size', self.current_font_size)
            # Update the result label style
            self.ui.lbl_khmer_res.setStyleSheet(f"font-size: {self.current_font_size}px; font-weight: bold; color: #4CAF50;")

    def load_tracking_settings(self):
        self.enable_face = get_setting('enable_face_tracking', '0') == '1'
        self.enable_eye = get_setting('enable_eye_tracking', '0') == '1'

    def apply_tracking_settings(self):
        face = self.ui.cb_enable_face.isChecked()
        eye = self.ui.cb_enable_eye.isChecked()
        set_setting('enable_face_tracking', '1' if face else '0')
        set_setting('enable_eye_tracking', '1' if eye else '0')
        
        self.enable_face = face
        self.enable_eye = eye
        
        # Re-initialize recognizer with new settings
        self.recognizer = GestureRecognizer(use_face=face, use_eye=eye)

    def save_settings(self):
        new_idx = self.ui.combo_camera.currentData()
        if new_idx is None:
            QMessageBox.warning(self.ui, "Warning", "Please select a camera.")
            return
            
        set_setting('camera_index', new_idx)
        self.apply_voice_settings()
        
        # Restart camera if index changed
        if int(new_idx) != self.camera_index:
            if self.cap.isOpened():
                self.cap.release()
            self.camera_index = int(new_idx)
            self.cap = cv2.VideoCapture(self.camera_index)
            
        QMessageBox.information(self.ui, "Success", "Settings updated successfully!")

    def run(self):
        self.ui.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = MainApp()
    app.run()
