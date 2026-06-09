"""
Utility Functions for Health Chatbot
Helper functions for validation, formatting, and common operations
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_user_input(text: str) -> Dict[str, Any]:
    """
    Validate and sanitize user input
    
    Args:
        text: User input text
    
    Returns:
        Dictionary with validation results
    """
    if not text or not isinstance(text, str):
        return {
            "is_valid": False,
            "message": "Empty or invalid input",
            "cleaned_text": ""
        }
    
    # Remove extra whitespace
    cleaned = text.strip()
    
    # Check length limits
    if len(cleaned) < 1:
        return {
            "is_valid": False,
            "message": "Input is too short",
            "cleaned_text": ""
        }
    
    if len(cleaned) > 500:
        return {
            "is_valid": False,
            "message": "Input is too long (maximum 500 characters)",
            "cleaned_text": cleaned[:500]
        }
    
    # Remove potentially harmful characters (basic XSS prevention)
    cleaned = re.sub(r'[<>{}]', '', cleaned)
    
    # Check for profanity (basic - can be extended)
    profanity_list = []  # Add profanity words if needed
    for word in profanity_list:
        if word in cleaned.lower():
            return {
                "is_valid": False,
                "message": "Please use respectful language",
                "cleaned_text": ""
            }
    
    return {
        "is_valid": True,
        "message": "Input validated",
        "cleaned_text": cleaned
    }


def format_response_for_display(response_text: str) -> str:
    """
    Format AI response for better display
    """
    if not response_text:
        return "I couldn't generate a response. Please try again."
    
    # Ensure proper line breaks
    formatted = response_text.replace('\\n', '\n')
    
    # Ensure disclaimer is present (if not already)
    disclaimer = "\n\n⚠️ **Medical Disclaimer**: This information is for educational purposes only. Always consult a qualified healthcare provider."
    
    if "not a doctor" not in formatted.lower() and "consult" not in formatted.lower():
        formatted += disclaimer
    
    return formatted


def extract_symptoms_from_query(query: str) -> List[str]:
    """
    Extract potential symptoms from user query
    
    Args:
        query: User's question
    
    Returns:
        List of mentioned symptoms
    """
    common_symptoms = [
        "fever", "headache", "cough", "cold", "sore throat", 
        "body ache", "fatigue", "nausea", "vomiting", "diarrhea",
        "rash", "difficulty breathing", "chest pain", "dizziness",
        "loss of appetite", "weight loss", "muscle pain", "joint pain",
        "बुखार", "सिरदर्द", "खांसी", "जुकाम", "थकान"
    ]
    
    query_lower = query.lower()
    found_symptoms = []
    
    for symptom in common_symptoms:
        if symptom in query_lower:
            found_symptoms.append(symptom)
    
    return found_symptoms


def get_severity_indicator(symptoms: List[str]) -> Dict[str, Any]:
    """
    Provide general severity guidance based on symptoms
    
    Args:
        symptoms: List of symptoms mentioned
    
    Returns:
        Severity assessment (not diagnostic)
    """
    high_severity = [
        "difficulty breathing", "chest pain", "bleeding", 
        "loss of consciousness", "seizure", "paralysis"
    ]
    
    medium_severity = [
        "high fever", "persistent vomiting", "severe headache",
        "dehydration", "confusion"
    ]
    
    severity_level = "low"
    recommendation = "Monitor symptoms at home with rest and hydration."
    
    for symptom in symptoms:
        if symptom in high_severity:
            severity_level = "high"
            recommendation = "⚠️ Please seek medical attention immediately or call emergency services."
            break
        elif symptom in medium_severity:
            severity_level = "medium"
            recommendation = "Consider consulting a doctor within 24 hours if symptoms persist or worsen."
    
    return {
        "severity": severity_level,
        "recommendation": recommendation,
        "symptom_count": len(symptoms)
    }


def generate_session_id() -> str:
    """
    Generate a unique session ID for conversation tracking
    """
    from uuid import uuid4
    return str(uuid4())


def log_conversation(user_input: str, bot_response: str, language: str, success: bool):
    """
    Log conversation for analytics (simple file-based logging)
    
    Args:
        user_input: User's message
        bot_response: Bot's response
        language: Detected/used language
        success: Whether request succeeded
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] LANG:{language} | SUCCESS:{success} | USER:{user_input[:100]} | BOT:{bot_response[:100]}\n"
    
    try:
        with open('conversation_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to log conversation: {e}")


def create_health_tip() -> Dict[str, str]:
    """
    Generate a random health tip for display
    
    Returns:
        Dictionary with health tip
    """
    import random
    
    health_tips = [
        {"title": "💧 Stay Hydrated", "tip": "Drink at least 8 glasses of water daily for optimal health."},
        {"title": "😴 Sleep Well", "tip": "Adults need 7-9 hours of quality sleep each night."},
        {"title": "🏃 Exercise", "tip": "30 minutes of moderate exercise 5 days a week improves heart health."},
        {"title": "🥗 Eat Colors", "tip": "Include colorful fruits and vegetables in every meal."},
        {"title": "🧼 Wash Hands", "tip": "Wash hands for 20 seconds to prevent infection spread."},
        {"title": "😊 Manage Stress", "tip": "Take deep breaths and short breaks to reduce stress."},
        {"title": "🦷 Oral Hygiene", "tip": "Brush twice daily and floss for healthy teeth and gums."},
        {"title": "🌞 Get Vitamin D", "tip": "15-20 minutes of morning sunlight helps vitamin D production."},
        {"title": "🚭 No Smoking", "tip": "Quitting smoking improves lung health within weeks."},
        {"title": "🏥 Regular Checkups", "tip": "Annual health checkups can detect issues early."}
    ]
    
    return random.choice(health_tips)


def validate_email(email: str) -> bool:
    """
    Validate email format (for future feedback feature)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_html(text: str) -> str:
    """
    Basic HTML sanitization for safe display
    """
    if not text:
        return ""
    
    # Remove script tags and event handlers
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'on\w+="[^"]*"', '', text)
    text = re.sub(r'on\w+=\'[^\']*\'', '', text)
    
    # Escape remaining HTML special characters
    html_escape = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;'
    }
    
    for char, escape in html_escape.items():
        text = text.replace(char, escape)
    
    return text


def get_language_name(code: str) -> str:
    """
    Get full language name from language code
    """
    languages = {
        'en': 'English',
        'hi': 'Hindi (हिन्दी)',
        'mr': 'Marathi (मराठी)',
        'ta': 'Tamil (தமிழ்)',
        'te': 'Telugu (తెలుగు)',
        'bn': 'Bengali (বাংলা)'
    }
    
    return languages.get(code, 'English')


def is_medical_emergency_query(query: str) -> bool:
    """
    Check if query indicates a medical emergency
    """
    emergency_phrases = [
        "heart attack", "stroke", "severe bleeding", "can't breathe",
        "unconscious", "seizure", "overdose", "poisoning",
        "chest pain", "difficulty breathing", "suicidal",
        "हार्ट अटैक", "सांस नहीं आ रही", "बेहोश"
    ]
    
    query_lower = query.lower()
    return any(phrase in query_lower for phrase in emergency_phrases)