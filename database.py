import sqlite3
import json
import os

DB_PATH = "data/gestures.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gestures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english_label TEXT NOT NULL,
            khmer_label TEXT NOT NULL,
            landmarks TEXT NOT NULL,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    # Default camera index
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('camera_index', '0')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('khmer_voice', 'km-KH-PisethNeural')") # Male: Piseth, Female: Sreymom
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('english_voice', 'en-US-GuyNeural')") # Male: Guy, Female: Aria
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('voice_gender', 'Male')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('tts_engine', 'Edge-TTS')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('voice_language', 'Khmer')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('khmer_font_size', '32')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('enable_face_tracking', '0')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('enable_eye_tracking', '0')")
    
    # Migration: Add image_path to gestures if it doesn't exist
    try:
        cursor.execute("ALTER TABLE gestures ADD COLUMN image_path TEXT")
    except sqlite3.OperationalError:
        pass
        
    # Create audio_paths table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gesture_id INTEGER,
            language TEXT,
            tts_engine TEXT,
            gender TEXT,
            file_path TEXT,
            FOREIGN KEY (gesture_id) REFERENCES gestures(id)
        )
    ''')
        
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
    conn.commit()
    conn.close()

def add_gesture(english_label, khmer_label, landmarks_list, image_path=None):
    """
    landmarks_list: a flattened list of 63 floats representing normalized coordinates
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    landmarks_json = json.dumps(landmarks_list)
    cursor.execute('''
        INSERT INTO gestures (english_label, khmer_label, landmarks, image_path)
        VALUES (?, ?, ?, ?)
    ''', (english_label, khmer_label, landmarks_json, image_path))
    conn.commit()
    conn.close()

def get_all_gestures():
    """
    Returns a list of dicts: [{'id': int, 'english': str, 'khmer': str, 'landmarks': [float, ...], 'image_path': str}]
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, english_label, khmer_label, landmarks, image_path FROM gestures')
    rows = cursor.fetchall()
    conn.close()
    
    gestures = []
    for row in rows:
        gestures.append({
            'id': row[0],
            'english': row[1],
            'khmer': row[2],
            'landmarks': json.loads(row[3]),
            'image_path': row[4]
        })
    return gestures

def delete_gesture(gesture_id):
    """
    Deletes the gesture and its associated audio paths from the DB.
    Returns a list of all associated file paths (image and audio) for disk cleanup.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Get image path
    cursor.execute('SELECT image_path FROM gestures WHERE id = ?', (gesture_id,))
    img_row = cursor.fetchone()
    image_path = img_row[0] if img_row else None
    
    # 2. Get all audio paths
    cursor.execute('SELECT file_path FROM audio_paths WHERE gesture_id = ?', (gesture_id,))
    audio_rows = cursor.fetchall()
    audio_paths = [row[0] for row in audio_rows if row[0]]
    
    # 3. Delete records
    cursor.execute('DELETE FROM gestures WHERE id = ?', (gesture_id,))
    cursor.execute('DELETE FROM audio_paths WHERE gesture_id = ?', (gesture_id,))
    
    conn.commit()
    conn.close()
    
    # Return all paths for disk deletion
    all_paths = []
    if image_path: all_paths.append(image_path)
    all_paths.extend(audio_paths)
    return all_paths

def update_gesture_labels(gesture_id, english_label, khmer_label):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Get all old audio paths associated with this gesture
    cursor.execute('SELECT file_path FROM audio_paths WHERE gesture_id = ?', (gesture_id,))
    rows = cursor.fetchall()
    old_audio_paths = [row[0] for row in rows if row[0]]
    
    # 2. Update labels
    cursor.execute('''
        UPDATE gestures 
        SET english_label = ?, khmer_label = ? 
        WHERE id = ?
    ''', (english_label, khmer_label, gesture_id))
    
    # 3. Delete audio records from DB so they will be regenerated
    cursor.execute('DELETE FROM audio_paths WHERE gesture_id = ?', (gesture_id,))
    
    conn.commit()
    conn.close()
    
    return old_audio_paths

def save_audio_path(gesture_id, language, tts_engine, gender, file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Check if exists
    cursor.execute('''
        SELECT id FROM audio_paths 
        WHERE gesture_id = ? AND language = ? AND tts_engine = ? AND gender = ?
    ''', (gesture_id, language, tts_engine, gender))
    row = cursor.fetchone()
    
    if row:
        cursor.execute('''
            UPDATE audio_paths SET file_path = ? WHERE id = ?
        ''', (file_path, row[0]))
    else:
        cursor.execute('''
            INSERT INTO audio_paths (gesture_id, language, tts_engine, gender, file_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (gesture_id, language, tts_engine, gender, file_path))
    conn.commit()
    conn.close()

def get_audio_path_from_db(gesture_id, language, tts_engine, gender):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT file_path FROM audio_paths 
        WHERE gesture_id = ? AND language = ? AND tts_engine = ? AND gender = ?
    ''', (gesture_id, language, tts_engine, gender))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
