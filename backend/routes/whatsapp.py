# backend/routes/whatsapp.py
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
import logging
import hashlib
import hmac
import json
from typing import Dict, Any, Optional
import asyncio

from config import settings
from services.whatsapp_api import WhatsAppAPI
from services.nlp_engine import NPLEngine
from services.translator import Translator
from services.tts import TextToSpeech
from utils.helpers import validate_phone_number, sanitize_input
from utils.logger import setup_logger
from db.models import get_db_connection

# Initialize router
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

# Initialize services
whatsapp_api = WhatsAppAPI()
nlp_engine = NPLEngine()
translator = Translator()
tts = TextToSpeech()

# Initialize logger
logger = setup_logger(__name__)

class WhatsAppWebhookHandler:
    """Handler for WhatsApp webhook events"""
    
    def __init__(self):
        self.supported_message_types = ["text", "interactive", "button", "location"]
        self.supported_interactive_types = ["button_reply", "list_reply"]
    
    async def verify_webhook(self, request: Request) -> PlainTextResponse:
        """
        Verify WhatsApp webhook during setup
        """
        try:
            # Get query parameters
            mode = request.query_params.get("hub.mode")
            token = request.query_params.get("hub.verify_token")
            challenge = request.query_params.get("hub.challenge")
            
            logger.info(f"Webhook verification attempt: mode={mode}, token={token}")
            
            # Check if mode and token are present
            if mode and token:
                # Check the mode and token sent are correct
                if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
                    logger.info("WEBHOOK_VERIFIED")
                    return PlainTextResponse(content=challenge)
                else:
                    logger.warning("Verification failed - invalid token or mode")
                    return PlainTextResponse(content="Verification failed", status_code=403)
            else:
                logger.warning("Verification failed - missing parameters")
                return PlainTextResponse(content="Missing parameters", status_code=400)
                
        except Exception as e:
            logger.error(f"Error in webhook verification: {str(e)}")
            return PlainTextResponse(content="Server error", status_code=500)
    
    async def handle_webhook(self, request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
        """
        Handle incoming WhatsApp webhook events
        """
        try:
            # Verify signature for security
            if not await self._verify_signature(request):
                logger.warning("Invalid webhook signature")
                return JSONResponse(content={"status": "unauthorized"}, status_code=401)
            
            # Parse request body
            body = await request.json()
            logger.info(f"Received webhook: {json.dumps(body, indent=2)}")
            
            # Process webhook in background
            background_tasks.add_task(self._process_webhook, body)
            
            return JSONResponse(content={"status": "success"})
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook")
            return JSONResponse(content={"status": "invalid_json"}, status_code=400)
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return JSONResponse(content={"status": "error"}, status_code=500)
    
    async def _verify_signature(self, request: Request) -> bool:
        """
        Verify webhook signature for security
        """
        if not settings.WHATSAPP_ACCESS_TOKEN:
            return True  # Skip verification in development
        
        try:
            signature = request.headers.get("x-hub-signature-256", "")
            if not signature:
                logger.warning("Missing signature in webhook")
                return False
            
            # Get request body
            body = await request.body()
            
            # Verify signature
            expected_signature = hmac.new(
                key=settings.WHATSAPP_ACCESS_TOKEN.encode(),
                msg=body,
                digestmod=hashlib.sha256
            ).hexdigest()
            
            expected_header = f"sha256={expected_signature}"
            is_valid = hmac.compare_digest(expected_header, signature)
            
            if not is_valid:
                logger.warning(f"Invalid signature: expected {expected_header}, got {signature}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            return False
    
    async def _process_webhook(self, body: Dict[str, Any]) -> None:
        """
        Process webhook data and handle different event types
        """
        try:
            entry = body.get("entry", [])
            if not entry:
                logger.info("No entries in webhook")
                return
            
            for entry_item in entry:
                changes = entry_item.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    
                    # Handle different webhook events
                    if "messages" in value:
                        await self._handle_messages(value)
                    elif "message_template_status_updates" in value:
                        await self._handle_template_status_updates(value)
                    elif "message_deliveries" in value:
                        await self._handle_message_deliveries(value)
                    elif "message_reads" in value:
                        await self._handle_message_reads(value)
                    else:
                        logger.info(f"Unhandled webhook event type: {value.keys()}")
                        
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
    
    async def _handle_messages(self, value: Dict[str, Any]) -> None:
        """
        Handle incoming messages
        """
        try:
            messages = value.get("messages", [])
            metadata = value.get("metadata", {})
            
            for message in messages:
                await self._process_single_message(message, metadata)
                
        except Exception as e:
            logger.error(f"Error handling messages: {str(e)}")
    
    async def _process_single_message(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """
        Process a single incoming message
        """
        try:
            # Extract message details
            message_type = message.get("type")
            from_number = message.get("from")
            message_id = message.get("id")
            timestamp = message.get("timestamp")
            
            logger.info(f"Processing {message_type} message from {from_number}")
            
            # Validate phone number
            if not validate_phone_number(from_number):
                logger.warning(f"Invalid phone number: {from_number}")
                return
            
            # Handle different message types
            if message_type == "text":
                await self._handle_text_message(message, from_number, message_id, metadata)
            elif message_type == "interactive":
                await self._handle_interactive_message(message, from_number, message_id, metadata)
            elif message_type == "button":
                await self._handle_button_message(message, from_number, message_id, metadata)
            elif message_type == "location":
                await self._handle_location_message(message, from_number, message_id, metadata)
            elif message_type == "image":
                await self._handle_image_message(message, from_number, message_id, metadata)
            elif message_type == "audio":
                await self._handle_audio_message(message, from_number, message_id, metadata)
            else:
                logger.info(f"Unsupported message type: {message_type}")
                await self._send_unsupported_message(from_number)
                
        except Exception as e:
            logger.error(f"Error processing single message: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _handle_text_message(self, message: Dict[str, Any], from_number: str, 
                                 message_id: str, metadata: Dict[str, Any]) -> None:
        """
        Handle text messages
        """
        try:
            text_body = message.get("text", {}).get("body", "").strip()
            
            if not text_body:
                logger.warning("Empty text message received")
                await self._send_empty_message_response(from_number)
                return
            
            # Sanitize input
            text_body = sanitize_input(text_body)
            
            # Log the message
            self._log_interaction(from_number, text_body, "user", "whatsapp", message_id)
            
            # Process the message
            await self._process_user_query(from_number, text_body, metadata)
            
        except Exception as e:
            logger.error(f"Error handling text message: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _handle_interactive_message(self, message: Dict[str, Any], from_number: str,
                                        message_id: str, metadata: Dict[str, Any]) -> None:
        """
        Handle interactive messages (buttons, lists)
        """
        try:
            interactive = message.get("interactive", {})
            interactive_type = interactive.get("type")
            
            if interactive_type == "button_reply":
                button_reply = interactive.get("button_reply", {})
                button_id = button_reply.get("id")
                button_title = button_reply.get("title")
                
                logger.info(f"Button reply: {button_id} - {button_title}")
                
                # Log the interaction
                self._log_interaction(from_number, f"BUTTON: {button_id} - {button_title}", 
                                    "user", "whatsapp", message_id)
                
                # Process button click
                await self._process_button_click(from_number, button_id, button_title, metadata)
                
            elif interactive_type == "list_reply":
                list_reply = interactive.get("list_reply", {})
                list_id = list_reply.get("id")
                list_title = list_reply.get("title")
                list_description = list_reply.get("description")
                
                logger.info(f"List reply: {list_id} - {list_title}")
                
                # Log the interaction
                self._log_interaction(from_number, f"LIST: {list_id} - {list_title}", 
                                    "user", "whatsapp", message_id)
                
                # Process list selection
                await self._process_list_selection(from_number, list_id, list_title, metadata)
                
            else:
                logger.info(f"Unsupported interactive type: {interactive_type}")
                await self._send_unsupported_message(from_number)
                
        except Exception as e:
            logger.error(f"Error handling interactive message: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _handle_button_message(self, message: Dict[str, Any], from_number: str,
                                   message_id: str, metadata: Dict[str, Any]) -> None:
        """
        Handle button messages (legacy)
        """
        try:
            button = message.get("button", {})
            button_text = button.get("text")
            button_payload = button.get("payload")
            
            logger.info(f"Button message: {button_text} - {button_payload}")
            
            # Log the interaction
            self._log_interaction(from_number, f"BUTTON_LEGACY: {button_text}", 
                                "user", "whatsapp", message_id)
            
            # Process button click
            await self._process_button_click(from_number, button_payload, button_text, metadata)
            
        except Exception as e:
            logger.error(f"Error handling button message: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _handle_location_message(self, message: Dict[str, Any], from_number: str,
                                     message_id: str, metadata: Dict[str, Any]) -> None:
        """
        Handle location messages
        """
        try:
            location = message.get("location", {})
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            address = location.get("address", "")
            
            logger.info(f"Location received: {latitude}, {longitude} - {address}")
            
            # Log the interaction
            self._log_interaction(from_number, f"LOCATION: {latitude},{longitude}", 
                                "user", "whatsapp", message_id)
            
            # Store location for outbreak alerts
            await self._store_user_location(from_number, latitude, longitude, address)
            
            # Send location acknowledgment
            location_response = "📍 Thank you for sharing your location. This helps us provide relevant health alerts and information for your area."
            await whatsapp_api.send_message(from_number, location_response)
            
            # Log bot response
            self._log_interaction(from_number, location_response, "bot", "whatsapp")
            
        except Exception as e:
            logger.error(f"Error handling location message: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _handle_image_message(self, message: Dict[str, Any], from_number: str,
                                  message_id: str, metadata: Dict[str, Any]) -> None:
        """
        Handle image messages
        """
        try:
            image = message.get("image", {})
            image_id = image.get("id")
            caption = image.get("caption", "")
            
            logger.info(f"Image received: {image_id} - Caption: {caption}")
            
            # Log the interaction
            self._log_interaction(from_number, f"IMAGE: {caption}", "user", "whatsapp", message_id)
            
            # Send response for image messages
            image_response = "🖼️ I see you sent an image. Currently, I can only process text messages. Please describe your health concern in words."
            await whatsapp_api.send_message(from_number, image_response)
            
            # Log bot response
            self._log_interaction(from_number, image_response, "bot", "whatsapp")
            
        except Exception as e:
            logger.error(f"Error handling image message: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _handle_audio_message(self, message: Dict[str, Any], from_number: str,
                                  message_id: str, metadata: Dict[str, Any]) -> None:
        """
        Handle audio messages (voice notes)
        """
        try:
            audio = message.get("audio", {})
            audio_id = audio.get("id")
            
            logger.info(f"Audio received: {audio_id}")
            
            # Log the interaction
            self._log_interaction(from_number, "AUDIO_MESSAGE", "user", "whatsapp", message_id)
            
            if settings.FEATURE_VOICE:
                # TODO: Implement speech-to-text processing
                # For now, send a placeholder response
                audio_response = "🎤 I received your voice message. Voice message processing is coming soon! For now, please type your health concerns."
            else:
                audio_response = "🎤 I received your voice message. Currently, I can only process text messages. Please type your health concerns."
            
            await whatsapp_api.send_message(from_number, audio_response)
            
            # Log bot response
            self._log_interaction(from_number, audio_response, "bot", "whatsapp")
            
        except Exception as e:
            logger.error(f"Error handling audio message: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _process_user_query(self, from_number: str, user_message: str, 
                                metadata: Dict[str, Any]) -> None:
        """
        Process user query and send response
        """
        try:
            # Detect language
            detected_lang = translator.detect_language(user_message)
            logger.info(f"Detected language: {detected_lang} for user {from_number}")
            
            # Translate to English if needed
            if detected_lang != "en":
                english_message = translator.translate_to_english(user_message)
            else:
                english_message = user_message
            
            # Process with NLP engine
            nlp_response = nlp_engine.process_query(english_message)
            logger.info(f"NLP response - Intent: {nlp_response['intent']}, Confidence: {nlp_response['confidence']}")
            
            # Translate response back to user's language if needed
            if detected_lang != "en":
                final_response = translator.translate_from_english(nlp_response["response"], detected_lang)
            else:
                final_response = nlp_response["response"]
            
            # Generate voice message if needed and feature enabled
            voice_url = None
            if settings.FEATURE_VOICE and nlp_response.get("needs_voice", False):
                try:
                    voice_url = tts.generate_speech(final_response, detected_lang)
                except Exception as e:
                    logger.error(f"Error generating TTS: {str(e)}")
            
            # Send response
            await whatsapp_api.send_message(from_number, final_response, voice_url)
            
            # Log bot response
            self._log_interaction(from_number, final_response, "bot", "whatsapp", 
                                metadata={"intent": nlp_response["intent"], 
                                         "confidence": nlp_response["confidence"],
                                         "language": detected_lang})
            
            # Handle special intents
            await self._handle_special_intent(from_number, nlp_response["intent"], 
                                            nlp_response.get("entities", {}), metadata)
            
        except Exception as e:
            logger.error(f"Error processing user query: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _process_button_click(self, from_number: str, button_id: str, 
                                  button_title: str, metadata: Dict[str, Any]) -> None:
        """
        Process button click actions
        """
        try:
            # Map button IDs to actions
            button_actions = {
                "symptom_check": await self._start_symptom_check,
                "vaccine_info": await self._send_vaccine_info,
                "disease_info": await self._send_disease_info,
                "prevention_tips": await self._send_prevention_tips,
                "outbreak_alerts": await self._send_outbreak_alerts,
                "emergency_help": await self._send_emergency_help,
                "language_change": await self._change_language,
                "human_agent": await self._escalate_to_human,
            }
            
            action = button_actions.get(button_id)
            if action:
                await action(from_number, metadata)
            else:
                logger.warning(f"Unknown button ID: {button_id}")
                await self._send_unknown_button_response(from_number)
                
        except Exception as e:
            logger.error(f"Error processing button click: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _process_list_selection(self, from_number: str, list_id: str,
                                    list_title: str, metadata: Dict[str, Any]) -> None:
        """
        Process list selection actions
        """
        try:
            # Handle different list selections
            if list_id.startswith("disease_"):
                disease_name = list_id.replace("disease_", "")
                await self._send_disease_details(from_number, disease_name)
            elif list_id.startswith("symptom_"):
                symptom = list_id.replace("symptom_", "")
                await self._process_symptom_selection(from_number, symptom, metadata)
            elif list_id.startswith("vaccine_"):
                vaccine_type = list_id.replace("vaccine_", "")
                await self._send_vaccine_details(from_number, vaccine_type)
            else:
                logger.warning(f"Unknown list ID: {list_id}")
                await self._send_unknown_selection_response(from_number)
                
        except Exception as e:
            logger.error(f"Error processing list selection: {str(e)}")
            await self._send_error_message(from_number)
    
    async def _handle_special_intent(self, from_number: str, intent: str, 
                                   entities: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """
        Handle special intents that require additional actions
        """
        try:
            if intent == "emergency":
                await self._handle_emergency_intent(from_number, entities)
            elif intent == "symptom_check":
                await self._handle_symptom_check_intent(from_number, entities)
            elif intent == "vaccine_info":
                await self._handle_vaccine_info_intent(from_number, entities)
            elif intent == "outbreak_alert":
                await self._handle_outbreak_alert_intent(from_number, entities)
                
        except Exception as e:
            logger.error(f"Error handling special intent: {str(e)}")
    
    async def _handle_emergency_intent(self, from_number: str, entities: Dict[str, Any]) -> None:
        """Handle emergency situations"""
        emergency_message = "🚨 This appears to be an emergency. Please contact local emergency services immediately. For India: Dial 112 or 108 for ambulance."
        await whatsapp_api.send_message(from_number, emergency_message)
        
        # Log emergency
        self._log_interaction(from_number, "EMERGENCY_DETECTED", "system", "whatsapp")
    
    async def _handle_symptom_check_intent(self, from_number: str, entities: Dict[str, Any]) -> None:
        """Handle symptom checking flow"""
        # Start symptom check flow
        await self._start_symptom_check(from_number)
    
    async def _handle_vaccine_info_intent(self, from_number: str, entities: Dict[str, Any]) -> None:
        """Handle vaccine information requests"""
        vaccine_name = entities.get("vaccine")
        if vaccine_name:
            await self._send_vaccine_details(from_number, vaccine_name)
        else:
            await self._send_vaccine_info(from_number)
    
    async def _handle_outbreak_alert_intent(self, from_number: str, entities: Dict[str, Any]) -> None:
        """Handle outbreak alert requests"""
        location = entities.get("location")
        await self._send_outbreak_alerts(from_number, location)
    
    # Button action implementations
    async def _start_symptom_check(self, from_number: str, metadata: Dict[str, Any]) -> None:
        """Start symptom checking flow"""
        symptom_message = "Please describe your symptoms. For example: 'I have fever and headache since yesterday'"
        await whatsapp_api.send_message(from_number, symptom_message)
    
    async def _send_vaccine_info(self, from_number: str, metadata: Dict[str, Any] = None) -> None:
        """Send vaccine information"""
        vaccine_message = "💉 Here is information about vaccination schedules and available vaccines..."
        # TODO: Implement actual vaccine info
        await whatsapp_api.send_message(from_number, vaccine_message)
    
    async def _send_disease_info(self, from_number: str, metadata: Dict[str, Any] = None) -> None:
        """Send disease information"""
        disease_message = "🦠 Please tell me which disease you want information about, or type 'list' to see common diseases."
        await whatsapp_api.send_message(from_number, disease_message)
    
    async def _send_prevention_tips(self, from_number: str, metadata: Dict[str, Any] = None) -> None:
        """Send prevention tips"""
        prevention_message = "🛡️ Here are general prevention tips: Wash hands regularly, maintain social distancing, wear masks in crowded areas, and get vaccinated."
        await whatsapp_api.send_message(from_number, prevention_message)
    
    async def _send_outbreak_alerts(self, from_number: str, location: str = None, 
                                  metadata: Dict[str, Any] = None) -> None:
        """Send outbreak alerts"""
        if location:
            alert_message = f"📍 Checking outbreak alerts for {location}..."
        else:
            alert_message = "📍 Please share your location to get relevant outbreak alerts, or specify a location."
        await whatsapp_api.send_message(from_number, alert_message)
    
    async def _send_emergency_help(self, from_number: str, metadata: Dict[str, Any] = None) -> None:
        """Send emergency help information"""
        emergency_contacts = """
🚨 Emergency Contacts:
• National Emergency: 112
• Ambulance: 108
• Police: 100
• Fire: 101

Please describe your emergency situation.
"""
        await whatsapp_api.send_message(from_number, emergency_contacts)
    
    async def _change_language(self, from_number: str, metadata: Dict[str, Any] = None) -> None:
        """Handle language change request"""
        language_message = "🌐 Please type your preferred language: Hindi, English, Odia, Tamil, Telugu, etc."
        await whatsapp_api.send_message(from_number, language_message)
    
    async def _escalate_to_human(self, from_number: str, metadata: Dict[str, Any] = None) -> None:
        """Escalate to human agent"""
        escalation_message = "👥 Connecting you to a human agent. Please wait while we transfer your conversation."
        await whatsapp_api.send_message(from_number, escalation_message)
        
        # TODO: Implement actual escalation logic
        self._log_interaction(from_number, "HUMAN_ESCALATION_REQUESTED", "system", "whatsapp")
    
    async def _send_disease_details(self, from_number: str, disease_name: str) -> None:
        """Send detailed disease information"""
        # TODO: Implement disease details from database
        disease_message = f"🦠 Information about {disease_name}: Symptoms, prevention, and treatment details will be shown here."
        await whatsapp_api.send_message(from_number, disease_message)
    
    async def _process_symptom_selection(self, from_number: str, symptom: str, 
                                       metadata: Dict[str, Any]) -> None:
        """Process symptom selection in symptom check flow"""
        # TODO: Implement symptom check logic
        symptom_message = f"🔍 Analyzing symptom: {symptom}. Please describe any other symptoms."
        await whatsapp_api.send_message(from_number, symptom_message)
    
    async def _send_vaccine_details(self, from_number: str, vaccine_type: str) -> None:
        """Send detailed vaccine information"""
        # TODO: Implement vaccine details from database
        vaccine_message = f"💉 Information about {vaccine_type}: Schedule, dosage, and side effects will be shown here."
        await whatsapp_api.send_message(from_number, vaccine_message)
    
    async def _store_user_location(self, from_number: str, latitude: float, 
                                 longitude: float, address: str) -> None:
        """Store user location for personalized alerts"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_locations 
                (phone, latitude, longitude, address, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (from_number, latitude, longitude, address, datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored location for user {from_number}")
            
        except Exception as e:
            logger.error(f"Error storing user location: {str(e)}")
    
    async def _handle_template_status_updates(self, value: Dict[str, Any]) -> None:
        """Handle template message status updates"""
        try:
            status_updates = value.get("message_template_status_updates", [])
            for update in status_updates:
                message_id = update.get("id")
                status = update.get("status")
                timestamp = update.get("timestamp")
                
                logger.info(f"Template message {message_id} status: {status} at {timestamp}")
                
        except Exception as e:
            logger.error(f"Error handling template status updates: {str(e)}")
    
    async def _handle_message_deliveries(self, value: Dict[str, Any]) -> None:
        """Handle message delivery updates"""
        try:
            deliveries = value.get("message_deliveries", [])
            for delivery in deliveries:
                message_ids = delivery.get("message_ids", [])
                timestamp = delivery.get("timestamp")
                
                for message_id in message_ids:
                    logger.info(f"Message {message_id} delivered at {timestamp}")
                    
        except Exception as e:
            logger.error(f"Error handling message deliveries: {str(e)}")
    
    async def _handle_message_reads(self, value: Dict[str, Any]) -> None:
        """Handle message read updates"""
        try:
            reads = value.get("message_reads", [])
            for read in reads:
                message_ids = read.get("message_ids", [])
                timestamp = read.get("timestamp")
                
                for message_id in message_ids:
                    logger.info(f"Message {message_id} read at {timestamp}")
                    
        except Exception as e:
            logger.error(f"Error handling message reads: {str(e)}")
    
    async def _send_unsupported_message(self, from_number: str) -> None:
        """Send response for unsupported message types"""
        response = "❌ I can only process text messages at the moment. Please type your health concerns."
        await whatsapp_api.send_message(from_number, response)
    
    async def _send_error_message(self, from_number: str) -> None:
        """Send error response"""
        response = "⚠️ Sorry, I encountered an error. Please try again in a moment."
        await whatsapp_api.send_message(from_number, response)
    
    async def _send_empty_message_response(self, from_number: str) -> None:
        """Send response for empty messages"""
        response = "📝 I didn't receive any message. Please type your health question or concern."
        await whatsapp_api.send_message(from_number, response)
    
    async def _send_unknown_button_response(self, from_number: str) -> None:
        """Send response for unknown button clicks"""
        response = "❓ I didn't recognize that option. Please try again or type your question."
        await whatsapp_api.send_message(from_number, response)
    
    async def _send_unknown_selection_response(self, from_number: str) -> None:
        """Send response for unknown list selections"""
        response = "❓ I didn't recognize that selection. Please try again or type your question."
        await whatsapp_api.send_message(from_number, response)
    
    def _log_interaction(self, phone: str, message: str, sender: str, 
                        channel: str, message_id: str = None, metadata: Dict = None) -> None:
        """Log interaction to database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO interactions (phone, message, sender, channel, message_id, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (phone, message, sender, channel, message_id, 
                  json.dumps(metadata) if metadata else None, 
                  datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")

# Initialize handler
webhook_handler = WhatsAppWebhookHandler()

# Webhook routes
@router.get("/webhook")
async def webhook_verification(request: Request):
    """WhatsApp webhook verification endpoint"""
    return await webhook_handler.verify_webhook(request)

@router.post("/webhook")
async def webhook_receiver(request: Request, background_tasks: BackgroundTasks):
    """WhatsApp webhook receiver endpoint"""
    return await webhook_handler.handle_webhook(request, background_tasks)

@router.post("/send-message")
async def send_message(to: str, message: str, message_type: str = "text"):
    """Send message to WhatsApp user (for testing/admin)"""
    try:
        if not validate_phone_number(to):
            raise HTTPException(status_code=400, detail="Invalid phone number")
        
        result = await whatsapp_api.send_message(to, message, message_type=message_type)
        
        return {
            "status": "success",
            "message_id": result.get("message_id"),
            "recipient": to
        }
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/templates")
async def get_templates():
    """Get available WhatsApp message templates"""
    try:
        templates = await whatsapp_api.get_templates()
        return {
            "status": "success",
            "templates": templates
        }
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get templates")

@router.post("/send-template")
async def send_template_message(to: str, template_name: str, parameters: Dict[str, Any] = None):
    """Send WhatsApp template message"""
    try:
        if not validate_phone_number(to):
            raise HTTPException(status_code=400, detail="Invalid phone number")
        
        result = await whatsapp_api.send_template_message(to, template_name, parameters or {})
        
        return {
            "status": "success",
            "message_id": result.get("message_id"),
            "recipient": to,
            "template_name": template_name
        }
        
    except Exception as e:
        logger.error(f"Error sending template message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send template message")

# Health check endpoint for WhatsApp service
@router.get("/health")
async def whatsapp_health():
    """Check WhatsApp service health"""
    try:
        # Test WhatsApp API connectivity
        is_healthy = await whatsapp_api.health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "whatsapp",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"WhatsApp health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "whatsapp",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }