import os
import threading
import hashlib
import asyncio
import edge_tts
from gtts import gTTS
import pygame

AUDIO_DIR = "data/audio"

class AudioPlayer:
    def __init__(self):
        os.makedirs(AUDIO_DIR, exist_ok=True)
        # Initialize pygame mixer
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.is_playing = False
        self.last_played_text = None
        
        # Engine settings
        self.tts_engine = "Edge-TTS" # Default
        
        # Default voices for Edge-TTS
        self.khmer_voice = "km-KH-PisethNeural" # Male
        self.english_voice = "en-US-GuyNeural" # Male

    def get_audio_path(self, text, is_khmer=True):
        """Returns the local path where the audio file should be."""
        if self.tts_engine == "Edge-TTS":
            voice = self.khmer_voice if is_khmer else self.english_voice
            text_hash = hashlib.md5(f"edge_{text}_{voice}".encode('utf-8')).hexdigest()
        else:
            lang = 'km' if is_khmer else 'en'
            text_hash = hashlib.md5(f"gtts_{text}_{lang}".encode('utf-8')).hexdigest()
            
        return os.path.join(AUDIO_DIR, f"{text_hash}.mp3")

    async def _generate_audio_edge(self, text, voice, filepath):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)

    def _generate_audio_gtts(self, text, is_khmer, filepath):
        lang = 'km' if is_khmer else 'en'
        tts = gTTS(text=text, lang=lang)
        tts.save(filepath)

    def play_voice_sequence(self, sequence, gesture_id=None):
        """
        sequence: list of (text, is_khmer) tuples
        """
        if self.is_playing:
            return
            
        def run_sequence():
            self.is_playing = True
            for text, is_khmer in sequence:
                self._play_audio_thread(text, is_khmer, wait=True, gesture_id=gesture_id)
            self.is_playing = False
            
        threading.Thread(target=run_sequence, daemon=True).start()

    def _play_audio_thread(self, text, is_khmer=True, wait=False, gesture_id=None):
        if not text:
            if not wait: self.is_playing = False
            return

        # Engine settings
        gender = "Male" if (is_khmer and self.khmer_voice == "km-KH-PisethNeural") or (not is_khmer and self.english_voice == "en-US-GuyNeural") else "Female"
        lang = "Khmer" if is_khmer else "English"
        
        # 1. Check DB first
        if gesture_id:
            from database import get_audio_path_from_db, save_audio_path
            db_path = get_audio_path_from_db(gesture_id, lang, self.tts_engine, gender)
            if db_path and os.path.exists(db_path):
                filepath = db_path
            else:
                filepath = None
        else:
            filepath = None

        if not filepath:
            # 2. Check by hash (fallback/legacy)
            if self.tts_engine == "Edge-TTS":
                voice = self.khmer_voice if is_khmer else self.english_voice
                text_hash = hashlib.md5(f"edge_{text}_{voice}".encode('utf-8')).hexdigest()
            else:
                l_code = 'km' if is_khmer else 'en'
                text_hash = hashlib.md5(f"gtts_{text}_{l_code}".encode('utf-8')).hexdigest()

            safe_filename = f"{text_hash}.mp3"
            filepath = os.path.join(AUDIO_DIR, safe_filename)

        # Generate audio file if it doesn't exist
        if not os.path.exists(filepath):
            try:
                if self.tts_engine == "Edge-TTS":
                    voice = self.khmer_voice if is_khmer else self.english_voice
                    asyncio.run(self._generate_audio_edge(text, voice, filepath))
                else:
                    self._generate_audio_gtts(text, is_khmer, filepath)
                
                # Save to DB for future use
                if gesture_id:
                    from database import save_audio_path
                    save_audio_path(gesture_id, lang, self.tts_engine, gender, filepath)
                    
            except Exception as e:
                print(f"Error generating TTS audio ({self.tts_engine}) for {text}: {e}")
                if not wait: self.is_playing = False
                return

        try:
            # Play audio
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"Error playing audio: {e}")
        finally:
            if not wait:
                self.is_playing = False

    def play_voice(self, text, is_khmer=True, gesture_id=None):
        """
        Play audio using selected engine.
        """
        if self.is_playing or not text:
            return

        threading.Thread(target=self._play_audio_thread, args=(text, is_khmer, False, gesture_id), daemon=True).start()
        self.is_playing = True
