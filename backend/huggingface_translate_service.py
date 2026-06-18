"""
HuggingFace Translation Service - With Better Error Handling and Fallbacks
"""

import requests
import logging
import time
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceTranslateService:
    """Handles translations using HuggingFace's free Inference API"""
    
    def __init__(self):
        self.supported_languages = Config.SUPPORTED_LANGUAGES
        self.api_key = Config.HUGGINGFACE_API_KEY
        
        # Alternative API endpoints (if main one fails)
        self.api_endpoints = [
            "https://api-inference.huggingface.co/models/",
            "https://router.huggingface.co/hf-inference/models/"
        ]
        
        # Free translation models on HuggingFace
        self.models = {
            ('en', 'hi'): 'Helsinki-NLP/opus-mt-en-hi',
            ('hi', 'en'): 'Helsinki-NLP/opus-mt-hi-en',

            ('en', 'ta'): 'Helsinki-NLP/opus-mt-en-ta',
            ('ta', 'en'): 'Helsinki-NLP/opus-mt-ta-en',

            ('en', 'te'): 'Helsinki-NLP/opus-mt-en-te',
            ('te', 'en'): 'Helsinki-NLP/opus-mt-te-en',

            ('en', 'bn'): 'Helsinki-NLP/opus-mt-en-bn',
            ('bn', 'en'): 'Helsinki-NLP/opus-mt-bn-en',
        }
        
        # For Marathi (use Hindi model as fallback since Marathi specific is limited)
        self.models['mr'] = 'Helsinki-NLP/opus-mt-en-hi'
        
        self.is_available = bool(self.api_key and self.api_key != 'YOUR_HUGGINGFACE_API_KEY_HERE')
        
        if self.is_available:
            logger.info("✅ HuggingFace Translation Service initialized")
        else:
            logger.warning("⚠️ No valid HuggingFace API key found")
            logger.warning("Get your free key at: https://huggingface.co/settings/tokens")
    
    def detect_language(self, text):
        """
        Detect language using script detection (faster, no API call)
        """
        if not text:
            return 'en'
        
        # Check for Devanagari script (Hindi/Marathi)
        devanagari_chars = [char for char in text if '\u0900' <= char <= '\u097F']
        if len(devanagari_chars) > 0:
            # Check for common Marathi words
            marathi_indicators = ['आहे', 'मी', 'तू', 'आम्ही', 'तुम्ही', 'का', 'काय', 'होतं', 'असतं']
            text_lower = text.lower()
            if any(word in text_lower for word in marathi_indicators):
                logger.info("Detected Marathi language")
                return 'mr'
            logger.info("Detected Hindi language")
            return 'hi'
        
        # Check for Tamil script
        if any('\u0B80' <= char <= '\u0BFF' for char in text):
            logger.info("Detected Tamil language")
            return 'ta'
        
        # Check for Telugu script
        if any('\u0C00' <= char <= '\u0C7F' for char in text):
            logger.info("Detected Telugu language")
            return 'te'
        
        # Check for Bengali script
        if any('\u0980' <= char <= '\u09FF' for char in text):
            logger.info("Detected Bengali language")
            return 'bn'
        
        # Default to English
        return 'en'
    
    def translate_to_english(self, text, source_lang=None):
        """
        Translate any language to English
        """
        if not text or text.strip() == "":
            return ""
        
        # Detect source language if not provided
        if not source_lang:
            source_lang = self.detect_language(text)
        
        logger.info(f"Source language: {source_lang}")
        
        # If already English, return as is
        if source_lang == 'en':
            return text
        
        # Try multiple methods
        if self.is_available:
            # Try HuggingFace first
            result = self._translate_with_huggingface(text, source_lang, 'en')
            if result != text:
                return result
            
            # If HuggingFace fails, try alternative
            return self._translate_with_fallback(text, source_lang)
        else:
            return self._translate_with_fallback(text, source_lang)
    
    def translate_from_english(self, text, target_lang):
        """
        Translate English to target language
        """
        if not text or text.strip() == "":
            return ""
        
        if target_lang == 'en':
            return text
        
        logger.info(f"Translating to {target_lang}: {text[:100]}...")
        
        if self.is_available:
            result = self._translate_with_huggingface(text, 'en', target_lang)
            if result != text:
                return result
        
        # Fallback: Return English with note
        return f"[Translation to {target_lang} temporarily unavailable]\n\n{text}"
    
    def _translate_with_huggingface(self, text, source_lang, target_lang):
        """
        Perform translation using HuggingFace models with retry logic
        """
        # Get appropriate model
        model = self._get_model_for_pair(source_lang, target_lang)
        if not model:
            logger.warning(f"No model found for {source_lang}->{target_lang}")
            return text
        
        # Try different API endpoints
        for endpoint in self.api_endpoints:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "inputs": text
                }
                
                logger.info(f"Calling HuggingFace API with model: {model}")
                logger.info(f"Using endpoint: {endpoint}")
                
                # Add timeout and retry logic
                response = requests.post(
                    f"{endpoint}{model}",
                    headers=headers,
                    json=payload,
                    timeout=60,  # Increased timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Parse response
                    translated = self._parse_response(result, text)
                    if translated and translated != text:
                        logger.info(f"✅ Translation successful via {endpoint}")
                        return translated
                    else:
                        logger.warning(f"Empty or unchanged translation")
                        
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    logger.info("Model is loading, waiting 5 seconds...")
                    retry_delay = 2
                    for attempt in range(3):

                        response = requests.post(...)

                        if response.status_code == 503:
                            logger.info(f"Model loading... retrying in {retry_delay}s")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                else:
                    logger.warning(f"API error {response.status_code}: {response.text[:100]}")
                    continue
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout with endpoint {endpoint}")
                continue
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error with {endpoint}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error with endpoint {endpoint}: {e}")
                continue
        
        logger.error("All translation attempts failed")
        return text
    
    def _parse_response(self, result, original_text):
        """Parse HuggingFace API response"""
        try:
            if isinstance(result, list) and len(result) > 0:
                if 'translation_text' in result[0]:
                    return result[0]['translation_text']
                elif 'generated_text' in result[0]:
                    gen_text = result[0]['generated_text']
                    # Remove the original text if it's prepended
                    if gen_text.startswith(original_text):
                        return gen_text[len(original_text):].strip()
                    return gen_text
                elif isinstance(result[0], str):
                    return result[0]
            elif isinstance(result, dict):
                if 'translation_text' in result:
                    return result['translation_text']
                elif 'generated_text' in result:
                    return result['generated_text']
            
            return original_text
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return original_text
    
    def _get_model_for_pair(self, source_lang, target_lang):
        """
        Get appropriate HuggingFace model for language pair
        """
        # English to Indian languages
        if source_lang == 'en':
            if target_lang in self.models:
                return self.models[target_lang]
        
        # Indian languages to English
        if target_lang == 'en':
            if source_lang in self.models:
                return self.models[source_lang]
        
        # Default for Hindi (most supported)
        if source_lang == 'en' and target_lang == 'hi':
            return 'Helsinki-NLP/opus-mt-en-hi'
        if source_lang == 'hi' and target_lang == 'en':
            return 'Helsinki-NLP/opus-mt-en-hi'
        
        return self.models.get((source_lang, target_lang))
    
    def _translate_with_fallback(self, text, source_lang):
        """
        Simple fallback translation using word mapping for common health terms
        """
        # Common health terms mapping (Hindi to English)
        word_map = {
            'बुखार': 'fever',
            'सिरदर्द': 'headache',
            'खांसी': 'cough',
            'ज़ुकाम': 'cold',
            'दर्द': 'pain',
            'थकान': 'fatigue',
            'मतली': 'nausea',
            'उल्टी': 'vomiting',
            'दस्त': 'diarrhea',
            'बीमार': 'sick',
            'दवा': 'medicine',
            'डॉक्टर': 'doctor',
            'अस्पताल': 'hospital',
            'तापमान': 'temperature',
            'संक्रमण': 'infection'
        }
        
        translated_words = []
        for word in text.split():
            if word in word_map:
                translated_words.append(word_map[word])
            else:
                translated_words.append(word)
        
        result = ' '.join(translated_words)
        if result != text:
            logger.info(f"Fallback translation: {text} -> {result}")
            return result
        
        return text

# Create singleton instance
huggingface_translate_service = HuggingFaceTranslateService()
