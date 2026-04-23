# K-Gesture: Sign Language to Khmer/English Translator

A professional, standalone Desktop Application designed to bridge the communication gap between sign language users and the Khmer/English-speaking public. Built with **PyQt5**, **OpenCV**, and **MediaPipe**, this tool provides real-time translation, localized UI, and high-quality speech synthesis.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Framework](https://img.shields.io/badge/framework-PyQt5-green)

---

## 🌟 Key Features

### 1. Real-time Recognition & Translation
- **MediaPipe Integration**: High-precision hand landmark detection (21 points).
- **Custom Training**: Train the system to recognize your specific signs in seconds.
- **Overlay Rendering**: Khmer text is rendered directly onto the video feed with adjustable transparency and font sizes.

### 2. Localization & Aesthetics
- **Bilingual Interface**: Full support for both **English** and **Khmer** languages.
- **Theme Support**: Professional **Dark Mode** and **Light Mode** tailored for readability.
- **Khmer Font Size Support**: Adjustable font sizes for Khmer text (Small to Extra Large) to ensure accessibility.
- **Premium Design**: Modern UI with smooth transitions, glassmorphism-inspired components, and consistent branding.

### 3. Advanced Audio System
- **Multi-Engine TTS**: Supports both **Edge-TTS** (high-quality neural voices) and **gTTS**.
- **Gender Selection**: Choose between Male and Female neural voices for both Khmer and English.
- **Voice Caching**: Audio files are generated once and saved locally in `data/audio/` for instant playback.
- **Automatic Cleanup**: Editing a gesture's labels automatically deletes outdated voice files and generates fresh ones.

### 4. Data Management & Sync
- **Local SQLite DB**: All gestures and settings are stored locally in `data/gestures.db`.
- **JSON Sync**: Real-time broadcast of the current gesture to `current_gesture.json` for integration with web applications or external displays.
- **Auto-Translation**: Integrated Google Translate to assist during the gesture labeling process.

---

## 🚀 Installation

### Prerequisites
- **Python 3.9+**
- **Webcam**
- **Internet Connection** (Initially for TTS generation and translation; core recognition is offline)

### Setup Steps
1. **Clone & Navigate**:
   ```bash
   cd k-guesture
   ```

2. **Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Fonts**:
   Ensure `assets/fonts/Battambang.ttf` is present. This font is used for high-quality Khmer rendering.

---

## 📖 Usage Guide

### 1. Launching the App
```bash
python main.py
```

### 2. Gesture Training & Management
- **Capture**: Navigate to the "Training" tab, perform your sign, and click "Capture".
- **Edit**: Click the "Edit" button in the gesture table to update labels. **Note**: This will automatically regenerate the associated voice files.
- **Delete**: Remove gestures and all associated images/audio from the disk with a single click.

### 3. Real-time Translation
- Simply perform a sign in front of the camera.
- The recognized text will appear on the video overlay and in the "Result" panel.
- Audio will play according to your selected "Playback Language" in Settings.

### 4. System Settings
- **Camera**: Select your preferred input device.
- **Voice Settings**: Choose TTS engine, gender, and language priority.
- **UI Settings**: Switch between Dark/Light themes and adjust the Khmer font size for better visibility.

---

## 🛠 Technical Architecture

- **`main.py`**: The central controller managing the event loop, camera feed, and module integration.
- **`ui_main.py`**: Defines the complex, tabbed UI structure and localization logic.
- **`gesture_recognizer.py`**: Handles MediaPipe landmark processing and Euclidean distance-based gesture matching.
- **`audio_player.py`**: Manages asynchronous TTS generation, caching, and playback using `edge-tts` and `pygame`.
- **`database.py`**: Handles all SQLite CRUD operations for gestures and persistent settings.
- **`styles.py`**: Contains the comprehensive CSS/QSS design system for Dark and Light themes.
- **`utils.py`**: Core utilities for PIL-based Khmer rendering and file sync operations.

---

## 📝 Notes & Optimization
- **Lighting**: For best results, ensure the hand is well-lit and the background is relatively static.
- **Performance**: The app is optimized for M1/M2/M3 chips and modern Windows hardware, maintaining a consistent 30+ FPS.
- **Storage**: Audio files are stored as MD5-hashed MP3s to avoid duplication and ensure fast lookups.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
