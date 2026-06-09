"""
Translation Service - Using HuggingFace (Completely Free, No Billing)
"""

from huggingface_translate_service import huggingface_translate_service
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationService:
    """Translation service using HuggingFace Inference API"""
    
    def __init__(self):
        self.default_lang = Config.DEFAULT_LANGUAGE
        self.supported_languages = Config.SUPPORTED_LANGUAGES
        self.service = huggingface_translate_service
        
        logger.info(f"✅ Translation Service ready with HuggingFace (No billing required)")
        logger.info(f"📍 Supported languages: {list(self.supported_languages.keys())}")
    
    def detect_language(self, text):
        return self.service.detect_language(text)
    
    def translate_to_english(self, text, source_lang=None):
        return self.service.translate_to_english(text, source_lang)
    
    def translate_from_english(self, text, target_lang):
        return self.service.translate_from_english(text, target_lang)
    
    def process_multilingual_query(self, user_input):
        detected_lang = self.detect_language(user_input)
        logger.info(f"Processing query in language: {detected_lang}")
        
        if detected_lang != 'en':
            english_text = self.translate_to_english(user_input, detected_lang)
        else:
            english_text = user_input
        
        return english_text, detected_lang
    
    def prepare_multilingual_response(self, english_response, target_lang):
        if target_lang == 'en':
            return english_response
        
        logger.info(f"Preparing response in target language: {target_lang}")
        return self.translate_from_english(english_response, target_lang)
    
    def get_supported_languages(self):
        return [
            {'code': code, 'name': name} 
            for code, name in self.supported_languages.items()
        ]


# Create a singleton instance
translation_service = TranslationService()