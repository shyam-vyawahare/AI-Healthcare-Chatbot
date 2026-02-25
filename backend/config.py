# .env.example
# Copy this file to .env and update with your actual values

# App Configuration
DEBUG=True
ENVIRONMENT="development"
HOST="0.0.0.0"
PORT=8000
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# API Keys - AI/NLP Services
OPENAI_API_KEY="your_openai_api_key_here"
DEEPSEEK_API_KEY="your_deepseek_api_key_here"
HUGGINGFACE_API_KEY="your_huggingface_api_key_here"

# WhatsApp Business API Configuration
WHATSAPP_BUSINESS_ACCOUNT_ID="your_whatsapp_business_account_id"
WHATSAPP_PHONE_NUMBER_ID="your_whatsapp_phone_number_id"
WHATSAPP_ACCESS_TOKEN="your_whatsapp_access_token"
WHATSAPP_VERIFY_TOKEN="your_whatsapp_verify_token"

# SMS Service Configuration (Optional)
TWILIO_ACCOUNT_SID="your_twilio_account_sid"
TWILIO_AUTH_TOKEN="your_twilio_auth_token"
TWILIO_PHONE_NUMBER="your_twilio_phone_number"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./healthmitra.db")
DATABASE_NAME="healthmitra"

# NLP Configuration
DEFAULT_NLP_PROVIDER="deepseek"
NLP_CONFIDENCE_THRESHOLD=0.6
MAX_QUERY_LENGTH=500

# Translation Configuration
DEFAULT_SOURCE_LANGUAGE="en"
SUPPORTED_LANGUAGES=["en", "hi", "or", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa", "ur"]

# Text-to-Speech Configuration
TTS_ENABLED=True
TTS_DEFAULT_LANGUAGE="en"
TTS_VOICE_SPEED=150
TTS_CACHE_DIR="./cache/tts"

# Outbreak Alert Configuration
ALERT_CHECK_INTERVAL=3600

# Analytics Configuration
ANALYTICS_ENABLED=True
ANALYTICS_RETENTION_DAYS=90

# Security Configuration
SECRET_KEY=""
ALLOWED_HOSTS=["localhost", "127.0.0.1", "0.0.0.0"]
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=900

# Cache Configuration
CACHE_ENABLED=True
CACHE_TTL=300
REDIS_URL="redis://localhost:6379/0"

# Logging Configuration
LOG_LEVEL="INFO"
LOG_FILE="healthmitra.log"

# File Storage Configuration
UPLOAD_DIR="./uploads"
MAX_FILE_SIZE=10485760

# Health Data Configuration
HEALTH_DATA_DIR="./data"
FAQ_FILE="health_faq.json"
VACCINE_FILE="vaccines.json"
OUTBREAK_FILE="outbreaks.json"

# Feature Flags
FEATURE_WHATSAPP=True
FEATURE_SMS=True
FEATURE_VOICE=True
FEATURE_ALERTS=True
FEATURE_ANALYTICS=True

# Government Data Integration
GOV_DATA_API_URL="https://api.health.gov.in/v1"
GOV_DATA_API_KEY=""

# Fallback Configuration
FALLBACK_TO_HUMAN=True
HUMAN_ESCALATION_PHONE=+911234567890
HUMAN_ESCALATION_EMAIL="escalation@healthmitra.org"

# Monitoring Configuration
SENTRY_DSN="your_sentry_dsn_here"
HEALTH_CHECK_INTERVAL=30