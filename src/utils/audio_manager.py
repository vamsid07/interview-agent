import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import io
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def speech_to_text(self, audio_file) -> str:
        """Converts Streamlit audio_input (wav/webm bytes) to text."""
        try:
            # 1. Load audio using pydub (Handles WebM/WAV differences)
            # Note: This requires ffmpeg installed on your system
            audio = AudioSegment.from_file(audio_file)
            
            # 2. Normalize audio (Mono, 16kHz) for better recognition
            audio = audio.set_channels(1).set_frame_rate(16000)
            
            # 3. Export to clean WAV container in memory
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)

            # 4. Transcribe
            with sr.AudioFile(wav_io) as source:
                # Optional: Adjust for noise if recording environment is loud
                # self.recognizer.adjust_for_ambient_noise(source)
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                logger.info(f"Transcribed: {text}")
                return text
                
        except sr.UnknownValueError:
            logger.warning("Speech Recognition: Audio was empty or unintelligible")
            return ""
        except sr.RequestError as e:
            logger.error(f"STT Service Error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Audio Processing Error: {e}")
            if "ffmpeg" in str(e).lower():
                 logger.error("CRITICAL: FFmpeg not found. Please install FFmpeg on your system.")
            return ""

    def text_to_speech(self, text: str) -> bytes:
        """Converts text to MP3 audio bytes."""
        try:
            if not text:
                return None
            tts = gTTS(text=text, lang='en')
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return mp3_fp.read()
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return None