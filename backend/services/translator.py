# backend/services/translator.py
from typing import Dict, Optional
import json
import os

class Translator:
    """Multi-language translation service"""
    
    def __init__(self):
        # Language codes and names
        self.languages = {
            'en': 'English',
            'hi': 'Hindi',
            'bn': 'Bengali',
            'te': 'Telugu',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'ur': 'Urdu',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'or': 'Odia',
            'pa': 'Punjabi',
            'as': 'Assamese'
        }
        
        # Simple phrase translations for common health terms
        self.health_phrases = self._load_health_phrases()
        
    def _load_health_phrases(self) -> Dict:
        """Load common health phrases in multiple languages"""
        # Simplified translation dictionary (in production, use Google Translate API)
        return {
            'fever': {
                'hi': 'बुखार',
                'bn': 'জ্বর',
                'te': 'జ్వరం',
                'ta': 'காய்ச்சல்'
            },
            'cough': {
                'hi': 'खांसी',
                'bn': 'কাশি',
                'te': 'దగ్గు',
                'ta': 'இருமல்'
            },
            'headache': {
                'hi': 'सिरदर्द',
                'bn': 'মাথাব্যথা',
                'te': 'తలనొప్పి',
                'ta': 'தலைவலி'
            },
            'doctor': {
                'hi': 'डॉक्टर',
                'bn': 'ডাক্তার',
                'te': 'డాక్టర్',
                'ta': 'மருத்துவர்'
            },
            'medicine': {
                'hi': 'दवा',
                'bn': 'ওষুধ',
                'te': 'మందు',
                'ta': 'மருந்து'
            },
            'hospital': {
                'hi': 'अस्पताल',
                'bn': 'হাসপাতাল',
                'te': 'ఆసుపత్రి',
                'ta': 'மருத்துவமனை'
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        # Simplified language detection based on Unicode ranges
        # In production, use a proper language detection library like langdetect
        
        # Check for Devanagari (Hindi, Marathi, etc.)
        if any('\u0900' <= char <= '\u097F' for char in text):
            # Could be Hindi, Marathi, etc.
            # Simplified: assume Hindi for demo
            return 'hi'
        
        # Check for Bengali
        elif any('\u0980' <= char <= '\u09FF' for char in text):
            return 'bn'
        
        # Check for Tamil
        elif any('\u0B80' <= char <= '\u0BFF' for char in text):
            return 'ta'
        
        # Check for Telugu
        elif any('\u0C00' <= char <= '\u0C7F' for char in text):
            return 'te'
        
        # Default to English
        return 'en'
    
    def translate_to_english(self, text: str, source_lang: Optional[str] = None) -> str:
        """Translate text to English"""
        if not source_lang:
            source_lang = self.detect_language(text)
        
        if source_lang == 'en':
            return text
        
        # Simplified translation - replace known phrases
        # In production, use Google Translate API or similar
        translated = text
        
        for eng_word, translations in self.health_phrases.items():
            for lang, trans_word in translations.items():
                if lang == source_lang and trans_word in text:
                    translated = translated.replace(trans_word, eng_word)
        
        # If no translation occurred, return original with note
        if translated == text:
            translated = f"[Translated from {self.languages.get(source_lang, source_lang)}] {text}"
        
        return translated
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translate text from English to target language"""
        if target_lang == 'en':
            return text
        
        # Simplified translation - replace known phrases
        translated = text
        
        for eng_word, translations in self.health_phrases.items():
            if eng_word in text.lower() and target_lang in translations:
                translated = translated.replace(
                    eng_word, 
                    translations[target_lang],
                    1  # Replace first occurrence only
                )
                translated = translated.replace(
                    eng_word.capitalize(),
                    translations[target_lang]
                )
        
        # Add language note if needed
        if translated == text:
            translated = f"[{self.languages.get(target_lang, target_lang)}] {text}"
        
        return translated
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.languages