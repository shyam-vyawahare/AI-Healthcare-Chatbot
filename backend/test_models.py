import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
    print("❌ Please add your valid Gemini API key to the .env file")
    exit()

# Configure the API
genai.configure(api_key=api_key)

print("=" * 60)
print("AVAILABLE GEMINI MODELS (that support generateContent)")
print("=" * 60)

# List and filter models that can generate content
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(f"\n📌 Model: {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description[:100]}..." if len(model.description) > 100 else f"   Description: {model.description}")
        print(f"   Input Token Limit: {model.input_token_limit:,}")
        print(f"   Output Token Limit: {model.output_token_limit:,}")
        print(f"   Temperature Range: 0.0 - {model.temperature}")