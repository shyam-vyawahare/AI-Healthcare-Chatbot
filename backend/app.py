"""
Main Flask Application for AI Health Chatbot
Handles API routes, request processing, and response generation
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from config import Config
from ai_service import ai_service
from disease_data import disease_db
from auth import register_auth_routes
from utils import (
    validate_user_input, format_response_for_display, 
    extract_symptoms_from_query, get_severity_indicator,
    log_conversation, create_health_tip, is_medical_emergency_query,
    get_language_name, generate_session_id
)
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['JSON_AS_ASCII'] = False  # Support Unicode responses

# Enable CORS for React frontend
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

# Store conversation history (in production, use a database)
conversation_store = {}
register_auth_routes(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_available': ai_service.is_available,
        'supported_languages': translation_service.get_supported_languages()
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint with direct language response"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', generate_session_id())
        target_language = data.get('language', 'en')  # User's preferred language
        
        logger.info(f"📝 Received: {user_message[:100]}...")
        logger.info(f"🎯 Target language: {target_language}")
        
        # Validate input
        validation = validate_user_input(user_message)
        if not validation['is_valid']:
            return jsonify({'response': validation['message'], 'error': validation['message']}), 400
        
        cleaned_message = validation['cleaned_text']
        
        # Get AI response DIRECTLY in target language (Gemini handles translation)
        ai_result = ai_service.get_health_response(
            cleaned_message, 
            session_id, 
            target_language
        )
        
        response_text = ai_result['response']
        
        # Simulate thinking time for realistic feel (1-2 seconds)
        import time
        time.sleep(1.5)
        
        return jsonify({
            'response': response_text,
            'language': target_language,
            'session_id': session_id,
            'ai_source': ai_result.get('source', 'ai'),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'response': "I'm experiencing technical difficulties. Please try again. 🙏"}), 500
    
def get_emergency_response(language):
    """Get emergency message in user's language"""
    emergencies = {
        'en': "🚨 MEDICAL EMERGENCY DETECTED 🚨\n\nPlease call emergency services (108 in India) or visit the nearest hospital immediately!\n\nDo not wait for online advice in case of emergency.",
        'hi': "🚨 चिकित्सा आपातकाल का पता चला 🚨\n\nकृपया तुरंत आपातकालीन सेवाओं (108) को कॉल करें या निकटतम अस्पताल जाएं!\n\nआपातकाल में ऑनलाइन सलाह की प्रतीक्षा न करें।",
        'mr': "🚨 वैद्यकीय आपातकाल आढळला 🚨\n\nकृपया त्वरित आपत्कालीन सेवांना (108) कॉल करा किंवा जवळच्या रुग्णालयात जा!\n\nआपत्कालीन परिस्थितीत ऑनलाइन सल्ल्याची प्रतीक्षा करू नका।",
        'ta': "🚨 மருத்துவ அவசரநிலை கண்டறியப்பட்டது 🚨\n\nதயவுசெய்து அவசர சேவைகளை (108) அழைக்கவும் அல்லது உடனடியாக அருகிலுள்ள மருத்துவமனைக்குச் செல்லவும்!\n\nஅவசரநிலையில் ஆன்லைன் ஆலோசனைக்காக காத்திருக்க வேண்டாம்।"
    }
    return emergencies.get(language, emergencies['en'])

@app.route('/api/disease/<disease_name>', methods=['GET'])
def get_disease_info(disease_name):
    """
    Get detailed information about a specific disease
    """
    try:
        language = request.args.get('lang', 'en')
        
        # Get disease info from database
        disease_info = disease_db.get_disease_info(disease_name)
        
        if not disease_info:
            return jsonify({
                'error': f'Disease "{disease_name}" not found',
                'available_diseases': disease_db.get_all_diseases()
            }), 404
        
        # Translate if needed
        if language != 'en':
            disease_info = translation_service.translate_disease_info(disease_info, language)
        
        return jsonify({
            'disease': disease_info,
            'language': language
        }), 200
        
    except Exception as e:
        logger.error(f"Disease info error: {str(e)}")
        return jsonify({'error': 'Failed to fetch disease information'}), 500

@app.route('/api/diseases', methods=['GET'])
def list_diseases():
    """
    List all available diseases
    """
    try:
        language = request.args.get('lang', 'en')
        diseases = disease_db.get_all_diseases()
        
        disease_list = []
        for disease_key in diseases:
            info = disease_db.get_disease_info(disease_key)
            if language != 'en':
                name = translation_service.translate_from_english(info['name'], language)
            else:
                name = info['name']
            
            disease_list.append({
                'key': disease_key,
                'name': name
            })
        
        return jsonify({
            'diseases': disease_list,
            'count': len(disease_list),
            'language': language
        }), 200
        
    except Exception as e:
        logger.error(f"List diseases error: {str(e)}")
        return jsonify({'error': 'Failed to fetch disease list'}), 500

@app.route('/api/health-tip', methods=['GET'])
def get_health_tip():
    """
    Get a random health tip
    """
    try:
        language = request.args.get('lang', 'en')
        tip = create_health_tip()
        
        if language != 'en':
            tip['title'] = translation_service.translate_from_english(tip['title'], language)
            tip['tip'] = translation_service.translate_from_english(tip['tip'], language)
        
        return jsonify(tip), 200
        
    except Exception as e:
        logger.error(f"Health tip error: {str(e)}")
        return jsonify({'title': 'Stay Healthy', 'tip': 'Regular checkups help prevent diseases'}), 200

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """
    Get list of supported languages
    """
    try:
        languages = translation_service.get_supported_languages()
        return jsonify({
            'languages': languages,
            'default': 'en'
        }), 200
    except Exception as e:
        logger.error(f"Languages endpoint error: {str(e)}")
        return jsonify({'error': 'Failed to fetch languages'}), 500

@app.route('/api/conversation/<session_id>', methods=['GET'])
def get_conversation_history(session_id):
    """
    Get conversation history for a session
    """
    try:
        history = conversation_store.get(session_id, [])
        return jsonify({
            'session_id': session_id,
            'history': history,
            'count': len(history)
        }), 200
    except Exception as e:
        logger.error(f"Conversation history error: {str(e)}")
        return jsonify({'error': 'Failed to fetch history'}), 500

@app.route('/api/clear-conversation/<session_id>', methods=['DELETE'])
def clear_conversation(session_id):
    """
    Clear conversation history for a session
    """
    try:
        if session_id in conversation_store:
            conversation_store[session_id] = []
        return jsonify({
            'session_id': session_id,
            'message': 'Conversation cleared successfully'
        }), 200
    except Exception as e:
        logger.error(f"Clear conversation error: {str(e)}")
        return jsonify({'error': 'Failed to clear conversation'}), 500

@app.route('/api/symptom-checker', methods=['POST'])
def symptom_checker():
    """
    Basic symptom checker (educational only, not diagnostic)
    """
    try:
        data = request.json
        symptoms = data.get('symptoms', [])
        
        if not symptoms:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        severity_info = get_severity_indicator(symptoms)
        
        # Get general advice based on severity
        if severity_info['severity'] == 'high':
            advice = "Please seek immediate medical attention. Do not wait."
        elif severity_info['severity'] == 'medium':
            advice = "Consider consulting a healthcare provider within 24 hours."
        else:
            advice = "Monitor your symptoms. Rest, stay hydrated, and consult a doctor if symptoms worsen."
        
        return jsonify({
            'symptoms_analyzed': symptoms,
            'severity': severity_info['severity'],
            'recommendation': severity_info['recommendation'],
            'advice': advice,
            'disclaimer': "⚠️ This is not a medical diagnosis. Always consult a qualified healthcare provider."
        }), 200
        
    except Exception as e:
        logger.error(f"Symptom checker error: {str(e)}")
        return jsonify({'error': 'Failed to analyze symptoms'}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting AI Health Chatbot Backend...")
    logger.info(f"📍 Running on http://{Config.HOST}:{Config.PORT}")
    logger.info(f"🤖 AI Available: {ai_service.is_available}")
    logger.info(f"🌐 Supported Languages: {list(Config.SUPPORTED_LANGUAGES.keys())}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )