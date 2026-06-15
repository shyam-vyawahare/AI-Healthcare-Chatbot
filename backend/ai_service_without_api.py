"""
AI Service using Free Public APIs (No API Key Required)
"""

import requests
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.is_available = True
        logger.info("✅ AI Service initialized (Free API Mode)")
    
    def get_health_response(self, user_query: str, session_id: str = None) -> Dict[str, Any]:
        if not user_query or user_query.strip() == "":
            return {"response": "Please ask a health-related question.", "confidence": 1.0, "source": "system"}
        
        # Emergency check
        emergency_keywords = ["suicide", "emergency", "heart attack", "bleeding", "unconscious"]
        if any(keyword in user_query.lower() for keyword in emergency_keywords):
            return {
                "response": "🚨 MEDICAL EMERGENCY DETECTED!\n\nPlease call emergency services (108 in India) or visit the nearest hospital immediately!\n\nDo not wait for online advice.",
                "confidence": 1.0,
                "source": "emergency"
            }
        
        return self._get_intelligent_response(user_query)
    
    def _get_intelligent_response(self, user_query: str) -> Dict[str, Any]:
        """Smart rule-based responses that feel natural"""
        query = user_query.lower()
        
        # Comprehensive response mapping
        response_map = [
            # Fever related
            {
                "keywords": ["fever", "बुखार", "ताप", "high temperature"],
                "response": """🌡️ **Managing Fever:**

• Rest as much as possible - your body needs energy to fight infection
• Stay hydrated with water, ORS, coconut water, or clear soups
• Take lukewarm sponge bath (not cold water)
• Use paracetamol (acetaminophen) for fever over 101°F (38.3°C) if you're an adult
• Wear light, breathable clothing
• Monitor temperature every 4-6 hours

**When to see a doctor:**
• Fever exceeds 103°F (39.4°C)
• Fever lasts more than 3 days
• Accompanied by severe headache, stiff neck, or difficulty breathing
• For infants under 3 months with any fever

⚠️ Remember: I'm an AI assistant, not a doctor."""
            },
            
            # Cold/Flu related
            {
                "keywords": ["cold", "flu", "ज़ुकाम", "सर्दी", "congestion", "runny nose"],
                "response": """🤧 **Managing Cold & Flu:**

**Home Remedies:**
• Steam inhalation 2-3 times daily with eucalyptus oil or Vicks
• Drink warm fluids: ginger tea, honey-lemon water, herbal tea, soup
• Gargle with warm salt water for sore throat
• Use saline nasal drops for congestion
• Get plenty of rest (7-9 hours sleep)
• Use a humidifier in your room

**Natural Relief:**
• Honey (1 teaspoon) for cough (adults and children over 1 year)
• Ginger tea with turmeric for inflammation
• Chicken soup for hydration and nutrients

**When to see a doctor:**
• Symptoms last more than 10 days
• Fever above 102°F (39°C)
• Difficulty breathing
• Severe sinus pain

⚠️ Remember: I'm an AI assistant, not a doctor."""
            },
            
            # Cough related
            {
                "keywords": ["cough", "खांसी", "khasni"],
                "response": """💊 **Managing Cough:**

**Home Remedies:**
• Honey - 1 teaspoon (for adults and children over 1 year)
• Ginger tea with honey and lemon
• Warm salt water gargle
• Stay hydrated with warm fluids
• Use a humidifier at night
• Elevate head while sleeping

**Types of cough:**
• Dry cough: Use honey, lozenges, steam
• Wet cough: Stay hydrated, use expectorants

**When to see a doctor:**
• Cough lasts more than 3 weeks
• Coughing up blood
• Accompanied by fever, chest pain, or difficulty breathing
• Wheezing or shortness of breath

⚠️ Remember: I'm an AI assistant, not a doctor."""
            },
            
            # Headache related
            {
                "keywords": ["headache", "सिरदर्द", "डोकेदुखी", "migraine"],
                "response": """🤕 **Headache Relief:**

**Immediate Relief:**
• Rest in a dark, quiet room
• Apply cold or warm compress to forehead/neck
• Stay hydrated - drink water slowly
• Gentle neck and shoulder stretches
• Deep breathing exercises (5-10 breaths)

**Natural Remedies:**
• Peppermint or lavender oil on temples
• Caffeine (tea/coffee) for migraines
• Magnesium-rich foods (nuts, seeds, leafy greens)

**When to seek medical help:**
• Sudden, severe 'thunderclap' headache
• Headache after head injury
• Accompanied by fever, stiff neck, confusion
• Vision changes or slurred speech
• Persistent headaches despite medication

⚠️ Remember: I'm an AI assistant, not a doctor."""
            },
            
            # COVID-19 specific
            {
                "keywords": ["covid", "corona", "कोविड"],
                "response": """🦠 **COVID-19 Information:**

**Common Symptoms:**
• Fever or chills
• Dry cough
• Fatigue
• Loss of taste or smell
• Sore throat
• Difficulty breathing (severe cases)

**Prevention:**
• Get vaccinated and boosted
• Wear mask in crowded places
• Maintain 6 feet distance
• Wash hands frequently (20+ seconds)
• Improve ventilation indoors

**If you test positive:**
• Isolate for at least 5-7 days
• Monitor oxygen levels with pulse oximeter
• Rest and stay hydrated
• Contact doctor for severe symptoms

**Emergency warning signs:**
• Trouble breathing
• Persistent chest pain
• New confusion
• Bluish lips or face

⚠️ Call emergency services immediately if you experience these symptoms!"""
            },
            
            # Dengue specific
            {
                "keywords": ["dengue", "डेंगू", "breakbone fever"],
                "response": """🦟 **Dengue Fever Awareness:**

**Symptoms (appear 4-10 days after bite):**
• Sudden high fever (104°F/40°C)
• Severe headache (especially behind eyes)
• Severe joint and muscle pain
• Nausea and vomiting
• Skin rash (appears 2-5 days after fever)
• Mild bleeding (nose/gums)

**Prevention:**
• Use mosquito repellent (DEET, picaridin)
• Wear long sleeves and pants
• Use mosquito nets while sleeping
• Remove standing water around home
• Install window screens

**Warning Signs (seek immediate care):**
• Severe abdominal pain
• Persistent vomiting
• Bleeding gums
• Blood in vomit
• Rapid breathing
• Fatigue/restlessness

**Treatment:**
• Take paracetamol (NOT aspirin or ibuprofen)
• Drink plenty of fluids (ORS, coconut water)
• Complete rest
• Monitor for warning signs

⚠️ Dengue can be serious - seek medical care if symptoms worsen!"""
            },
            
            # Malaria specific
            {
                "keywords": ["malaria", "मलेरिया"],
                "response": """🦟 **Malaria Information:**

**Symptoms (cyclic pattern):**
• High fever with shaking chills
• Severe headache
• Muscle pain
• Nausea and vomiting
• Fatigue and weakness
• Sweating followed by normal temperature

**Prevention:**
• Use insecticide-treated bed nets
• Apply mosquito repellent
• Take preventive medication if traveling to endemic areas
• Wear protective clothing
• Avoid outdoor activities at dusk/dawn

**When to seek immediate care:**
• Fever develops within 1 year of travel to malaria-endemic area
• Altered consciousness or seizures
• Difficulty breathing
• Dark urine

⚠️ Malaria requires immediate medical testing and prescription medication."""
            },
            
            # Diabetes specific
            {
                "keywords": ["diabetes", "मधुमेह", "sugar", "blood sugar"],
                "response": """📊 **Diabetes Awareness:**

**Common Symptoms:**
• Increased thirst (polydipsia)
• Frequent urination (polyuria)
• Extreme hunger (polyphagia)
• Unexplained weight loss
• Fatigue and weakness
• Blurred vision
• Slow-healing sores
• Tingling/numbness in hands/feet

**Prevention Tips:**
• Maintain healthy body weight
• Exercise 30 minutes daily
• Eat balanced diet (more fiber, less sugar)
• Limit processed foods and sugary drinks
• Get regular blood sugar checkups

**Management:**
• Monitor blood sugar regularly
• Take medications as prescribed
• Follow diabetic diet plan
• Exercise regularly
• Check feet daily for sores

**Emergency signs:**
• Very high/low blood sugar symptoms
• Fruity breath odor
• Difficulty breathing
• Confusion or loss of consciousness

⚠️ See a doctor if you experience symptoms or have risk factors."""
            },
            
            # General symptoms/advice
            {
                "keywords": ["what to do", "what should i do", "help me", "suggest"],
                "response": """💚 **General Health Advice:**

Based on common symptoms, here's what you can do:

**For Fever/Cold:**
• Rest and stay hydrated
• Monitor your temperature
• Take paracetamol if needed

**For Headache:**
• Rest in a dark room
• Stay hydrated
• Use cold compress

**General Self-Care:**
1. Get 7-9 hours of sleep
2. Drink 8-10 glasses of water daily
3. Eat light, nutritious meals
4. Avoid alcohol and smoking
5. Practice deep breathing for stress

⚠️ **When to see a doctor:**
• Symptoms lasting more than 3 days
• Severe pain or discomfort
• Difficulty breathing
• High fever (above 103°F)

⚠️ Remember: I'm an AI assistant, not a doctor. Please consult a healthcare provider for proper diagnosis."""
            }
        ]
        
        # Find matching response
        for item in response_map:
            if any(keyword in query for keyword in item["keywords"]):
                logger.info(f"Matched response for: {item['keywords'][0]}")
                return {"response": item["response"], "confidence": 0.85, "source": "smart_fallback"}
        
        # Default response
        return {
            "response": """💚 **AarogyaAI Health Assistant**

I can help you with information about:

🏥 **Symptoms:** Fever, cold, cough, headache
🦠 **Diseases:** COVID-19, Dengue, Malaria, Diabetes
💊 **Prevention:** Vaccines, hygiene, lifestyle tips
🏨 **When to see a doctor**

**Try asking:**
• "I have fever and headache"
• "What are COVID symptoms?"
• "How to prevent dengue?"
• "Tell me about diabetes"

⚠️ **Important:** This is for educational purposes only. Always consult a doctor for medical advice.

What would you like to know about today?""",
            "confidence": 0.8,
            "source": "default_response"
        }

ai_service = AIService()
