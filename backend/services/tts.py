# backend/services/tts.py
import os
import uuid
import logging
from typing import Optional
from gtts import gTTS
from config import settings

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Text-to-Speech service for generating voice responses"""
    
    def __init__(self):
        self.audio_dir = "audio_cache"
        self.supported_languages = {
            'en': 'en',
            'hi': 'hi',
            'bn': 'bn',
            'te': 'te',
            'ta': 'ta',
            'mr': 'mr',
            'gu': 'gu',
            'kn': 'kn',
            'ml': 'ml'
        }
        
        # Create audio cache directory if it doesn't exist
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
    
    def generate_speech(self, text: str, language: str = 'en') -> Optional[str]:
        """Generate speech from text and return file path or URL"""
        try:
            if not settings.FEATURE_TTS:
                logger.info("TTS feature is disabled")
                return None
            
            # Validate language
            if language not in self.supported_languages:
                language = 'en'
            
            # Generate unique filename
            filename = f"{uuid.uuid4().hex}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang=self.supported_languages[language], slow=False)
            tts.save(filepath)
            
            logger.info(f"Generated speech file: {filepath}")
            
            # Return URL path (assuming static serving)
            return f"/static/audio/{filename}"
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return None
    
    def generate_speech_with_emotion(self, text: str, language: str = 'en', 
                                     emotion: str = 'neutral') -> Optional[str]:
        """Generate speech with emotional tone (placeholder for advanced TTS)"""
        # In production, use advanced TTS APIs like Google Cloud TTS, AWS Polly, etc.
        # that support SSML and emotional tones
        logger.info(f"Generating speech with {emotion} emotion (using standard TTS)")
        return self.generate_speech(text, language)
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old audio files"""
        try:
            current_time = os.path.getctime
            for filename in os.listdir(self.audio_dir):
                filepath = os.path.join(self.audio_dir, filename)
                file_age = (time.time() - os.path.getctime(filepath)) / 3600
                
                if file_age > max_age_hours:
                    os.remove(filepath)
                    logger.info(f"Removed old audio file: {filename}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {str(e)}")