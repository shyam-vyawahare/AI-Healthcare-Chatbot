# backend/services/whatsapp_api.py
import httpx
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)

class WhatsAppAPI:
    """WhatsApp Business API integration"""
    
    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_version = settings.WHATSAPP_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        self.enabled = bool(self.api_token and self.phone_number_id)
        
        if not self.enabled:
            logger.warning("WhatsApp API not configured. Running in simulation mode.")
    
    async def send_message(self, to_phone: str, message: str, voice_url: Optional[str] = None) -> bool:
        """Send a message via WhatsApp"""
        try:
            if not self.enabled:
                logger.info(f"[SIMULATION] WhatsApp message to {to_phone}: {message[:100]}...")
                return True
            
            # Prepare message payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            # If voice URL is provided, send voice message instead
            if voice_url and settings.FEATURE_TTS:
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": to_phone,
                    "type": "audio",
                    "audio": {
                        "link": voice_url
                    }
                }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"WhatsApp message sent to {to_phone}")
                    return True
                else:
                    logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False
    
    def parse_webhook(self, body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse incoming WhatsApp webhook data"""
        try:
            # Check if it's a WhatsApp message
            if "entry" not in body:
                return None
            
            for entry in body["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    if "messages" in value:
                        for message in value["messages"]:
                            # Extract message details
                            message_data = {
                                "message_id": message.get("id"),
                                "user_phone": message.get("from"),
                                "timestamp": datetime.fromtimestamp(
                                    int(message.get("timestamp", 0))
                                ),
                                "type": message.get("type")
                            }
                            
                            # Extract text message
                            if message.get("type") == "text":
                                message_data["message"] = message.get("text", {}).get("body", "")
                                return message_data
                            
                            # Handle other message types
                            elif message.get("type") == "audio":
                                message_data["message"] = "[Voice message received]"
                                return message_data
                            
                            elif message.get("type") == "button":
                                message_data["message"] = message.get("button", {}).get("text", "")
                                return message_data
                            
                            elif message.get("type") == "interactive":
                                interactive = message.get("interactive", {})
                                if "button_reply" in interactive:
                                    message_data["message"] = interactive["button_reply"].get("title", "")
                                elif "list_reply" in interactive:
                                    message_data["message"] = interactive["list_reply"].get("title", "")
                                return message_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing WhatsApp webhook: {str(e)}")
            return None
    
    async def send_template_message(self, to_phone: str, template_name: str, components: Optional[Dict] = None) -> bool:
        """Send a template message (for approved templates only)"""
        try:
            if not self.enabled:
                logger.info(f"[SIMULATION] WhatsApp template to {to_phone}: {template_name}")
                return True
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "en"
                    }
                }
            }
            
            if components:
                payload["template"]["components"] = components
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error sending template message: {str(e)}")
            return False
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        try:
            if not self.enabled:
                return True
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")
            return False