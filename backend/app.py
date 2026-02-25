# backend/app.py
from config import settings
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio

# Import custom modules
from services.nlp_engine import NPLEngine
from services.translator import Translator
from services.whatsapp_api import WhatsAppAPI
from services.outbreak_alerts import OutbreakAlertSystem
from services.tts import TextToSpeech
from utils.logger import setup_logger
from utils.helpers import validate_phone_number, sanitize_input
from db.models import init_db, get_db_connection

# Initialize logger
logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HealthMitra API",
    description="AI-Driven Public Health Chatbot for Disease Awareness",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
nlp_engine = NPLEngine()
translator = Translator()
whatsapp_api = WhatsAppAPI()
outbreak_alerts = OutbreakAlertSystem()
tts = TextToSpeech()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="dashboard"), name="static")
templates = Jinja2Templates(directory="dashboard")

@app.on_event("startup")
async def startup_event():
    if settings.DEBUG:
        logger.info("Running in DEBUG mode")
    
    # Use feature flags
    if settings.FEATURE_WHATSAPP:
        logger.info("WhatsApp feature enabled")
        
    """Initialize services on startup"""
    logger.info("Initializing HealthMitra services...")
    
    # Initialize database
    init_db()
    
    # Load health data
    await load_health_data()
    
    # Start background tasks
    asyncio.create_task(background_alert_checker())
    
    logger.info("HealthMitra services initialized successfully")

async def load_health_data():
    """Load health data from JSON files"""
    try:
        data_dir = "data"
        
        # Load FAQs
        with open(f"{data_dir}/health_faq.json", "r", encoding="utf-8") as f:
            app.state.faq_data = json.load(f)
        
        # Load vaccine data
        with open(f"{data_dir}/vaccines.json", "r", encoding="utf-8") as f:
            app.state.vaccine_data = json.load(f)
        
        # Load outbreak data
        with open(f"{data_dir}/outbreaks.json", "r", encoding="utf-8") as f:
            app.state.outbreak_data = json.load(f)
            
        logger.info("Health data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading health data: {str(e)}")

# Background task for checking outbreak alerts
async def background_alert_checker():
    """Background task to check for outbreak alerts"""
    while True:
        try:
            active_alerts = outbreak_alerts.check_active_alerts()
            if active_alerts:
                logger.info(f"Active outbreak alerts: {len(active_alerts)}")
            
            # Check every hour
            await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Error in background alert checker: {str(e)}")
            await asyncio.sleep(300)  # Wait 5 minutes on error

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "HealthMitra API"
    }

@app.post("/api/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook for WhatsApp messages"""
    try:
        body = await request.json()
        logger.info(f"Received WhatsApp webhook: {body}")
        
        # Extract message details
        message_data = whatsapp_api.parse_webhook(body)
        
        if not message_data:
            return JSONResponse(content={"status": "ignored"})
        
        user_phone = message_data["user_phone"]
        user_message = message_data["message"]
        message_id = message_data["message_id"]
        
        # Process message in background
        background_tasks.add_task(
            process_user_message,
            user_phone,
            user_message,
            message_id,
            "whatsapp"
        )
        
        return JSONResponse(content={"status": "received"})
        
    except Exception as e:
        logger.error(f"Error in WhatsApp webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/sms/webhook")
async def sms_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook for SMS messages (for simulation)"""
    try:
        body = await request.json()
        logger.info(f"Received SMS webhook: {body}")
        
        user_phone = body.get("phone")
        user_message = body.get("message")
        
        if not user_phone or not user_message:
            raise HTTPException(status_code=400, detail="Missing phone or message")
        
        # Process message in background
        background_tasks.add_task(
            process_user_message,
            user_phone,
            user_message,
            f"sms_{datetime.now().timestamp()}",
            "sms"
        )
        
        return JSONResponse(content={"status": "received"})
        
    except Exception as e:
        logger.error(f"Error in SMS webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_user_message(user_phone: str, user_message: str, message_id: str, channel: str):
    """Process user message and send response"""
    try:
        # Sanitize input
        user_phone = sanitize_input(user_phone)
        user_message = sanitize_input(user_message)
        
        # Log interaction
        log_interaction(user_phone, user_message, "user", channel)
        
        # Detect language and translate to English if needed
        detected_lang = translator.detect_language(user_message)
        if detected_lang != "en":
            english_message = translator.translate_to_english(user_message)
        else:
            english_message = user_message
        
        # Process with NLP engine
        nlp_response = nlp_engine.process_query(english_message)
        
        # Translate response back to user's language if needed
        if detected_lang != "en":
            final_response = translator.translate_from_english(nlp_response["response"], detected_lang)
        else:
            final_response = nlp_response["response"]
        
        # Generate voice message if needed
        voice_url = None
        if nlp_response.get("needs_voice", False):
            voice_url = tts.generate_speech(final_response, detected_lang)
        
        # Send response via appropriate channel
        if channel == "whatsapp":
            await whatsapp_api.send_message(user_phone, final_response, voice_url)
        elif channel == "sms":
            # For SMS, we'd integrate with SMS service
            # For demo, we'll just log it
            logger.info(f"SMS Response to {user_phone}: {final_response}")
        
        # Log bot response
        log_interaction(user_phone, final_response, "bot", channel, nlp_response)
        
        # Update analytics
        update_analytics(user_phone, detected_lang, nlp_response["intent"])
        
    except Exception as e:
        logger.error(f"Error processing user message: {str(e)}")
        # Send error message to user
        error_message = "Sorry, I'm having trouble processing your request. Please try again later."
        if channel == "whatsapp":
            await whatsapp_api.send_message(user_phone, error_message)
        log_interaction(user_phone, error_message, "bot", channel, {"intent": "error"})

def log_interaction(phone: str, message: str, sender: str, channel: str, metadata: Dict = None):
    """Log user-bot interaction to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions (phone, message, sender, channel, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (phone, message, sender, channel, 
              json.dumps(metadata) if metadata else None, 
              datetime.now()))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error logging interaction: {str(e)}")

def update_analytics(phone: str, language: str, intent: str):
    """Update analytics data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update language stats
        cursor.execute('''
            INSERT OR REPLACE INTO language_stats (language, query_count, last_updated)
            VALUES (?, COALESCE((SELECT query_count FROM language_stats WHERE language = ?), 0) + 1, ?)
        ''', (language, language, datetime.now()))
        
        # Update intent stats
        cursor.execute('''
            INSERT OR REPLACE INTO intent_stats (intent, query_count, last_updated)
            VALUES (?, COALESCE((SELECT query_count FROM intent_stats WHERE intent = ?), 0) + 1, ?)
        ''', (intent, intent, datetime.now()))
        
        # Update user activity
        cursor.execute('''
            INSERT OR REPLACE INTO user_activity (phone, last_active, query_count)
            VALUES (?, ?, COALESCE((SELECT query_count FROM user_activity WHERE phone = ?), 0) + 1)
        ''', (phone, datetime.now(), phone))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error updating analytics: {str(e)}")

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total queries
        cursor.execute('SELECT COUNT(*) FROM interactions WHERE sender = "user"')
        total_queries = cursor.fetchone()[0]
        
        # Unique users
        cursor.execute('SELECT COUNT(DISTINCT phone) FROM interactions')
        unique_users = cursor.fetchone()[0]
        
        # Language distribution
        cursor.execute('SELECT language, query_count FROM language_stats ORDER BY query_count DESC LIMIT 5')
        language_stats = cursor.fetchall()
        
        # Top intents
        cursor.execute('SELECT intent, query_count FROM intent_stats ORDER BY query_count DESC LIMIT 10')
        intent_stats = cursor.fetchall()
        
        # Recent activity
        cursor.execute('''
            SELECT phone, last_active, query_count 
            FROM user_activity 
            ORDER BY last_active DESC 
            LIMIT 10
        ''')
        recent_activity = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_queries": total_queries,
            "unique_users": unique_users,
            "language_distribution": [
                {"language": lang, "count": count} for lang, count in language_stats
            ],
            "top_intents": [
                {"intent": intent, "count": count} for intent, count in intent_stats
            ],
            "recent_activity": [
                {"phone": phone, "last_active": last_active, "query_count": count}
                for phone, last_active, count in recent_activity
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")

@app.get("/api/outbreaks/active")
async def get_active_outbreaks():
    """Get active outbreak alerts"""
    try:
        active_alerts = outbreak_alerts.get_active_alerts()
        return {"alerts": active_alerts}
    except Exception as e:
        logger.error(f"Error getting outbreak alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving outbreak alerts")

@app.get("/api/faq/categories")
async def get_faq_categories():
    """Get FAQ categories"""
    try:
        categories = list(app.state.faq_data.keys())
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting FAQ categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving FAQ categories")

@app.get("/api/faq/{category}")
async def get_faq_by_category(category: str):
    """Get FAQs by category"""
    try:
        if category not in app.state.faq_data:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return {"category": category, "faqs": app.state.faq_data[category]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting FAQs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving FAQs")

@app.post("/api/query/test")
async def test_query(query: Dict[str, str]):
    """Test endpoint for query processing"""
    try:
        user_message = query.get("message", "")
        language = query.get("language", "en")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Translate if needed
        if language != "en":
            english_message = translator.translate_to_english(user_message)
        else:
            english_message = user_message
        
        # Process with NLP
        nlp_response = nlp_engine.process_query(english_message)
        
        # Translate response back if needed
        if language != "en":
            final_response = translator.translate_from_english(nlp_response["response"], language)
        else:
            final_response = nlp_response["response"]
        
        return {
            "original_query": user_message,
            "processed_query": english_message,
            "response": final_response,
            "intent": nlp_response["intent"],
            "confidence": nlp_response["confidence"],
            "language": language
        }
        
    except Exception as e:
        logger.error(f"Error in test query: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing query")

@app.get("/api/vaccines/schedule")
async def get_vaccine_schedule(age_group: Optional[str] = None):
    """Get vaccine schedule"""
    try:
        vaccines = app.state.vaccine_data.get("vaccines", [])
        
        if age_group:
            vaccines = [v for v in vaccines if v.get("age_group") == age_group]
        
        return {"vaccines": vaccines}
    except Exception as e:
        logger.error(f"Error getting vaccine schedule: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving vaccine schedule")

if __name__ == "__main__":
    import uvicorn
    
    # Run the app
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )