"""
AI Service using Google Gemini API - Handles BOTH Health Responses AND Translations
"""

import google.generativeai as genai
from config import Config
import logging
from typing import Dict, Any
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """Handles all AI operations including health responses and translations"""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.AI_MODEL
        self.temperature = Config.AI_TEMPERATURE
        self.max_tokens = Config.AI_MAX_TOKENS
        self.system_prompt = Config.SYSTEM_PROMPT
        
        # Store conversation history per session
        self.conversation_history = {}
        
        # Initialize Gemini
        if self.api_key and self.api_key != 'YOUR_GEMINI_API_KEY_HERE':
            try:
                genai.configure(api_key=self.api_key)
                
                # Try different model names
                models_to_try = [
                    self.model_name,
                    "gemini-2.0-flash",
                    "gemini-1.5-flash",
                    "gemini-pro",
                    "gemini-2.5-pro"
                ]
                
                self.is_available = False
                self.model = None
                
                for model_name in models_to_try:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        # Test the model
                        test_response = self.model.generate_content("Say OK")
                        if test_response and test_response.text:
                            self.model_name = model_name
                            self.is_available = True
                            logger.info(f"✅ AI Service initialized with Gemini model: {model_name}")
                            logger.info(f"✅ Gemini API test successful")
                            break
                    except Exception as e:
                        logger.warning(f"Failed to initialize model {model_name}: {e}")
                        continue
                
                if not self.is_available:
                    logger.error("❌ No working Gemini model found")
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
                self.is_available = False
                self.model = None
        else:
            logger.warning("⚠️ No valid Gemini API key found")
            self.is_available = False
            self.model = None
    
    def get_language_name(self, lang_code):
        """Get full language name from code"""
        languages = {
            'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi',
            'ta': 'Tamil', 'te': 'Telugu', 'bn': 'Bengali'
        }
        return languages.get(lang_code, 'English')
    
    def translate_text(self, text, target_lang, source_lang='auto'):
        """
        Translate text using Gemini AI
        """
        if not text or target_lang == 'en':
            return text
        
        try:
            translate_prompt = f"""Translate the following text from {source_lang if source_lang != 'auto' else 'the original language'} to {self.get_language_name(target_lang)}.

Text to translate: "{text}"

IMPORTANT: 
- Output ONLY the translated text
- Do NOT add any explanations or quotes
- Keep the same meaning and tone
- Preserve any formatting like bullet points or numbers

Translated text:"""
            
            response = self.model.generate_content(
                translate_prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 1000,
                }
            )
            
            translated = response.text.strip()
            logger.info(f"✅ Gemini translation: {text[:50]}... -> {translated[:50]}...")
            return translated
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def detect_language(self, text):
        """Detect language using Gemini AI"""
        if not text:
            return 'en'
        
        # Quick script-based detection for common cases
        if any('\u0900' <= char <= '\u097F' for char in text):
            # Check for Marathi indicators
            marathi_words = ['आहे', 'मी', 'तू', 'आम्ही', 'तुम्ही']
            if any(word in text for word in marathi_words):
                return 'mr'
            return 'hi'
        if any('\u0B80' <= char <= '\u0BFF' for char in text):
            return 'ta'
        if any('\u0C00' <= char <= '\u0C7F' for char in text):
            return 'te'
        if any('\u0980' <= char <= '\u09FF' for char in text):
            return 'bn'
        
        try:
            detect_prompt = f"""Identify the language of this text. Respond with ONLY the language code (en, hi, mr, ta, te, or bn).

Text: "{text}"

Language code:"""
            
            response = self.model.generate_content(detect_prompt)
            detected = response.text.strip().lower()[:2]
            
            if detected in ['en', 'hi', 'mr', 'ta', 'te', 'bn']:
                return detected
            return 'en'
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return 'en'
    
    def get_conversation_context(self, session_id: str, max_history: int = 5) -> str:
        """Get recent conversation history for context"""
        if session_id not in self.conversation_history:
            return ""
        
        history = self.conversation_history[session_id][-max_history:]
        if not history:
            return ""
        
        context = "\nPrevious conversation:\n"
        for msg in history:
            context += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n"
        context += "\nBased on the above conversation, continue naturally.\n"
        return context
    
    def store_conversation(self, session_id: str, user_message: str, assistant_response: str):
        """Store conversation in memory"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            'user': user_message,
            'assistant': assistant_response,
            'timestamp': time.time()
        })
        
        # Keep only last 20 messages
        if len(self.conversation_history[session_id]) > 20:
            self.conversation_history[session_id] = self.conversation_history[session_id][-20:]
    
    def get_health_response(self, user_query: str, session_id: str = None, language: str = 'en') -> Dict[str, Any]:
        """
        Generate health response directly in the user's language using Gemini
        """
        if not user_query or user_query.strip() == "":
            return {
                "response": "Please ask a health-related question.",
                "confidence": 1.0,
                "source": "system"
            }
        
        # Emergency detection
        emergency_keywords = ["suicide", "emergency", "heart attack", "bleeding heavily", "unconscious", "severe bleeding"]
        if any(keyword in user_query.lower() for keyword in emergency_keywords):
            emergency_responses = {
                'en': "🚨 MEDICAL EMERGENCY DETECTED 🚨\n\nPlease call emergency services (108 in India) or visit the nearest hospital immediately!\n\nDo not wait for online advice in case of emergency.",
                'hi': "🚨 चिकित्सा आपातकाल का पता चला 🚨\n\nकृपया तुरंत आपातकालीन सेवाओं (108) को कॉल करें या निकटतम अस्पताल जाएं!\n\nआपातकाल में ऑनलाइन सलाह की प्रतीक्षा न करें।",
                'mr': "🚨 वैद्यकीय आपातकाल आढळला 🚨\n\nकृपया त्वरित आपत्कालीन सेवांना (108) कॉल करा किंवा जवळच्या रुग्णालयात जा!"
            }
            return {
                "response": emergency_responses.get(language, emergency_responses['en']),
                "confidence": 1.0,
                "source": "emergency"
            }
        
        if self.is_available:
            return self._get_gemini_response(user_query, session_id, language)
        else:
            return self._get_fallback_response(user_query, language)
    
    def _get_gemini_response(self, user_query: str, session_id: str = None, language: str = 'en') -> Dict[str, Any]:
        """Get response directly from Gemini in the user's preferred language"""
        try:
            # Get conversation context
            context = ""
            if session_id:
                context = self.get_conversation_context(session_id)
            
            lang_name = self.get_language_name(language)
            
            # Updated prompt to ensure COMPLETE responses
            full_prompt = f"""You are AarogyaAI, a professional health assistant.

    IMPORTANT INSTRUCTIONS:
    1. Respond ONLY in {lang_name} language
    2. Write a COMPLETE response - do NOT cut off mid-sentence
    3. Make sure your response ends with a period, exclamation mark, or question mark
    4. Provide detailed, helpful health information

    {context}

    User's question in {lang_name}: {user_query}

    Provide a detailed, helpful health response in {lang_name} that includes:
    - Specific advice for the symptoms mentioned
    - Practical home remedies or self-care tips
    - Warning signs that need medical attention
    - A proper conclusion

    Write at least 4-6 complete sentences. Make sure your response feels complete and not cut off.

    Response in {lang_name}:"""
            
            logger.info(f"Generating response in {lang_name}")
            
            # Generate response with higher token limit
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1200,  # Increased
                    "top_p": 0.95,
                    "stop_sequences": []  # No stop sequences
                }
            )
            
            ai_response = response.text.strip()
            ai_response = self.ensure_complete_response(ai_response)
            
            # Ensure response is complete
            if ai_response:
                # Check if response ends properly
                if not ai_response[-1] in ['.', '!', '?', '"', '।', '」', '』', ':', ';']:
                    # Try to find the last complete sentence
                    last_period = ai_response.rfind('.')
                    last_exclaim = ai_response.rfind('!')
                    last_question = ai_response.rfind('?')
                    last_punctuation = max(last_period, last_exclaim, last_question)
                    
                    if last_punctuation > len(ai_response) // 2:
                        ai_response = ai_response[:last_punctuation + 1]
                    else:
                        # If no good punctuation found, add a period
                        ai_response = ai_response + "."
                
                # Log response length for debugging
                logger.info(f"Response length: {len(ai_response)} characters")
            
            # Add disclaimer if not present (but keep it concise)
            if "not a doctor" not in ai_response.lower() and "डॉक्टर" not in ai_response:
                disclaimer = {
                    'en': "\n\n⚠️ Remember: I'm an AI assistant, not a doctor. Please consult a healthcare provider.",
                    'hi': "\n\n⚠️ याद रखें: मैं AI सहायक हूं, डॉक्टर नहीं। कृपया डॉक्टर से सलाह लें।",
                    'mr': "\n\n⚠️ लक्षात ठेवा: मी AI सहाय्यक आहे, डॉक्टर नाही. कृपया डॉक्टरांचा सल्ला घ्या।"
                }
                ai_response += disclaimer.get(language, disclaimer['en'])
            
            # Store conversation
            if session_id:
                self.store_conversation(session_id, user_query, ai_response)
            
            logger.info(f"✅ Complete response generated ({len(ai_response)} chars)")
            return {
                "response": ai_response,
                "confidence": 0.9,
                "source": "gemini_ai",
                "language": language
            }
            
        except Exception as e:
            logger.error(f"❌ Gemini response error: {e}")
            return self._get_fallback_response(user_query, language)
    
    def _get_fallback_response(self, user_query: str, language: str = 'en') -> Dict[str, Any]:
        """Detailed fallback responses when AI is unavailable"""
        query_lower = user_query.lower()
        
        responses = {
            'en': {
                "fever": "🌡️ For fever:\n\n• Rest and stay hydrated\n• Take paracetamol if fever exceeds 101°F\n• Use a cold compress on your forehead\n• Monitor temperature every 4 hours\n\n⚠️ See a doctor if fever exceeds 103°F or lasts more than 3 days.\n\n⚠️ Remember: I'm an AI assistant, not a doctor.",
                "headache": "🤕 For headache:\n\n• Rest in a dark, quiet room\n• Stay hydrated\n• Apply cold or warm compress\n• Try caffeine if it's a migraine\n\n⚠️ See a doctor if severe, sudden, or accompanied by fever.\n\n⚠️ Remember: I'm an AI assistant, not a doctor.",
                "cold": "🤧 For cold:\n\n• Rest and stay warm\n• Drink warm fluids (tea, soup)\n• Use steam inhalation\n• Honey for cough (adults only)\n\n⚠️ See a doctor if symptoms last >10 days.\n\n⚠️ Remember: I'm an AI assistant, not a doctor."
            },
            'hi': {
                "fever": "🌡️ बुखार के लिए:\n\n• आराम करें और हाइड्रेटेड रहें\n• 101°F से अधिक बुखार होने पर पैरासिटामोल लें\n• माथे पर ठंडा सेक लगाएं\n• हर 4 घंटे में तापमान मापें\n\n⚠️ डॉक्टर को दिखाएं अगर बुखार 103°F से अधिक हो या 3 दिन से अधिक रहे।\n\n⚠️ याद रखें: मैं AI सहायक हूं, डॉक्टर नहीं।",
                "headache": "🤕 सिरदर्द के लिए:\n\n• अंधेरे, शांत कमरे में आराम करें\n• हाइड्रेटेड रहें\n• ठंडा या गर्म सेक लगाएं\n\n⚠️ डॉक्टर को दिखाएं अगर दर्द गंभीर या अचानक हो।\n\n⚠️ याद रखें: मैं AI सहायक हूं, डॉक्टर नहीं।"
            }
        }
        
        # Find matching response
        for key, response in responses.get(language, responses['en']).items():
            if key in query_lower:
                return {"response": response, "confidence": 0.7, "source": "fallback"}
        
        default = "💚 I'm here to help! Please tell me your symptoms (fever, headache, cold, etc.) for specific advice.\n\n⚠️ Remember: Always consult a doctor for medical advice."
        return {"response": default, "confidence": 0.6, "source": "fallback"}
    def ensure_complete_response(self, response_text):
        """Ensure the response is complete and not cut off"""
        if not response_text:
            return response_text
        
        # Common incomplete endings
        incomplete_endings = ['और', 'या', 'लेकिन', 'तो', 'भी', 'ही', 'and', 'or', 'but', 'so', 'also', 'with', 'without']
        
        # Check if response ends with incomplete word
        words = response_text.split()
        if words:
            last_word = words[-1].lower()
            if any(response_text.strip().endswith(word) for word in incomplete_endings):
                # Remove the incomplete last word
                response_text = ' '.join(words[:-1])
                response_text = response_text.rstrip(',.?!') + '.'
        
        # Ensure final punctuation
        if response_text and response_text[-1] not in ['.', '!', '?', '"', '।']:
            # Look for natural break points
            for punct in ['.', '!', '?', '।']:
                last_occurrence = response_text.rfind(punct)
                if last_occurrence > len(response_text) // 2:
                    response_text = response_text[:last_occurrence + 1]
                    break
            else:
                response_text = response_text + '.'
        
        return response_text
        
ai_service = AIService()
