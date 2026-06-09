"""
Google Cloud Translation API Service
Free tier: 500,000 characters per month (never expires)
"""

from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import logging
import os
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleTranslateService:
    """Handles all translation operations using Google Cloud Translate API"""
    
    def __init__(self):
        self.supported_languages = Config.SUPPORTED_LANGUAGES
        
        # Initialize Google Translate client
        try:
            # Look for credentials file
            credentials_path = os.path.join(os.path.dirname(__file__), 'google-cloud-key.json')
            
            if os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                self.client = translate.Client(credentials=credentials)
                logger.info("✅ Google Translate API initialized with service account")
            else:
                # Try using environment variable
                credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
                if credentials_json:
                    import json
                    credentials_info = json.loads(credentials_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_info,
                        scopes=['https://www.googleapis.com/auth/cloud-platform']
                    )
                    self.client = translate.Client(credentials=credentials)
                    logger.info("✅ Google Translate API initialized from environment variable")
                else:
                    # Fallback to default credentials (for Google Cloud Run/App Engine)
                    self.client = translate.Client()
                    logger.info("✅ Google Translate API initialized with default credentials")
            
            self.is_available = True
            
            # Test the connection
            test_result = self.client.translate('Hello', target_language='hi')
            logger.info(f"✅ Google Translate test successful: 'Hello' -> '{test_result['translatedText']}'")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Translate API: {e}")
            self.is_available = False
            self.client = None
    
    def detect_language(self, text):
        """
        Detect the language of input text using Google Translate API
        """
        if not self.is_available or not text:
            return self._fallback_detect_language(text)
        
        try:
            result = self.client.detect_language(text)
            detected_lang = result['language']
            confidence = result.get('confidence', 0)
            
            # Map Google language codes to our supported languages
            lang_map = {
                'en': 'en', 'hi': 'hi', 'mr': 'mr', 
                'ta': 'ta', 'te': 'te', 'bn': 'bn'
            }
            
            # Check if detected language is in our supported list
            if detected_lang in lang_map:
                logger.info(f"Google API detected: {detected_lang} (confidence: {confidence})")
                return lang_map[detected_lang]
            
            # Check for Devanagari script (Hindi/Marathi fallback)
            devanagari_chars = [char for char in text if '\u0900' <= char <= '\u097F']
            if len(devanagari_chars) > 0:
                # Check for common Marathi words
                marathi_indicators = ['आहे', 'मी', 'तू', 'आम्ही', 'तुम्ही', 'का', 'काय', 'होतं']
                if any(word in text for word in marathi_indicators):
                    logger.info("Fallback: Detected Marathi")
                    return 'mr'
                logger.info("Fallback: Detected Hindi")
                return 'hi'
            
            # Default to English
            return 'en'
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return self._fallback_detect_language(text)
    
    def _fallback_detect_language(self, text):
        """Fallback language detection without API"""
        try:
            # Check for Devanagari script (Hindi, Marathi)
            devanagari_chars = [char for char in text if '\u0900' <= char <= '\u097F']
            if len(devanagari_chars) > 0:
                marathi_indicators = ['आहे', 'मी', 'तू', 'आम्ही', 'तुम्ही', 'का', 'काय', 'होतं']
                if any(word in text for word in marathi_indicators):
                    return 'mr'
                return 'hi'
            
            # Check for Tamil script
            if any('\u0B80' <= char <= '\u0BFF' for char in text):
                return 'ta'
            
            # Check for Telugu script
            if any('\u0C00' <= char <= '\u0C7F' for char in text):
                return 'te'
            
            # Check for Bengali script
            if any('\u0980' <= char <= '\u09FF' for char in text):
                return 'bn'
            
            return 'en'
        except:
            return 'en'
    
    def translate_to_english(self, text, source_lang=None):
        """
        Translate text to English using Google Translate API
        """
        if not text or text.strip() == "":
            return ""
        
        try:
            # Detect source language if not provided
            if not source_lang:
                source_lang = self.detect_language(text)
            
            logger.info(f"Source language: {source_lang}")
            
            # If already English, return as is
            if source_lang == 'en':
                return text
            
            if self.is_available:
                # Use Google Translate API
                result = self.client.translate(text, target_language='en')
                translated = result['translatedText']
                logger.info(f"Google API translation successful: {translated[:100]}...")
                return translated
            else:
                logger.warning("Google API not available, using fallback")
                return text
            
        except Exception as e:
            logger.error(f"Translation to English error: {e}")
            return text
    
    def translate_from_english(self, text, target_lang):
        """
        Translate text from English to target language using Google Translate API
        """
        if not text or text.strip() == "":
            return ""
        
        # If target is English, return as is
        if target_lang == 'en':
            return text
        
        try:
            logger.info(f"Translating to {target_lang}: {text[:100]}...")
            
            if self.is_available:
                # Map our language codes to Google's codes
                lang_map = {
                    'hi': 'hi', 'mr': 'mr', 'ta': 'ta', 
                    'te': 'te', 'bn': 'bn'
                }
                
                google_lang = lang_map.get(target_lang, target_lang)
                result = self.client.translate(text, target_language=google_lang)
                translated = result['translatedText']
                
                logger.info(f"Google API translation to {target_lang} successful")
                return translated
            else:
                logger.warning(f"Google API not available for {target_lang}")
                return text + f"\n\n[Note: Using English - {target_lang} translation temporarily unavailable]"
                
        except Exception as e:
            logger.error(f"Translation from English error: {e}")
            return text + f"\n\n[Note: Translation to {target_lang} temporarily unavailable]"
    
    def translate_text(self, text, target_lang, source_lang=None):
        """
        General translation method - detects source language automatically
        """
        if not text:
            return ""
        
        if target_lang == 'en':
            return self.translate_to_english(text, source_lang)
        else:
            # First translate to English if needed, then to target
            english_text = self.translate_to_english(text, source_lang)
            return self.translate_from_english(english_text, target_lang)
    
    def get_supported_languages(self):
        """
        Return list of supported languages with their codes and names
        """
        return [
            {'code': code, 'name': name} 
            for code, name in self.supported_languages.items()
        ]


# Create a singleton instance
google_translate_service = GoogleTranslateService()