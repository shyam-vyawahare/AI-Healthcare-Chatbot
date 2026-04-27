# backend/services/nlp_engine.py
import re
import json
from typing import Dict, Any, List, Tuple
import numpy as np
from difflib import get_close_matches

class NPLEngine:
    """Natural Language Processing Engine for Health Queries"""
    
    def __init__(self):
        self.intent_patterns = {
            "symptom_check": ["symptom", "pain", "fever", "cough", "headache", "feel", "hurting", "ache"],
            "disease_info": ["what is", "tell me about", "information about", "explain", "disease", "condition"],
            "treatment": ["treatment", "cure", "medicine", "medication", "therapy", "remedy"],
            "prevention": ["prevent", "avoid", "protection", "vaccine", "vaccination", "immunization"],
            "emergency": ["emergency", "urgent", "severe", "critical", "hospital", "ambulance", "serious"],
            "medication": ["medicine", "drug", "pill", "tablet", "dosage", "prescription"],
            "doctor": ["doctor", "specialist", "clinic", "appointment", "consult", "physician"],
            "vaccine": ["vaccine", "vaccination", "immunization", "shot", "dose"],
            "outbreak": ["outbreak", "epidemic", "pandemic", "spread", "cases", "infected"],
            "nutrition": ["diet", "food", "eat", "nutrition", "vitamin", "mineral", "healthy eating"],
            "fitness": ["exercise", "workout", "fitness", "activity", "physical", "gym"],
            "mental_health": ["stress", "anxiety", "depression", "mental", "therapy", "counseling"],
            "children": ["child", "baby", "infant", "toddler", "pediatric", "kid"],
            "elderly": ["elderly", "senior", "old", "aging", "geriatric"],
            "pregnancy": ["pregnant", "pregnancy", "antenatal", "prenatal", "baby"],
            "first_aid": ["first aid", "injury", "wound", "burn", "cut", "bleeding", "fracture"]
        }
        
        self.response_templates = self._load_response_templates()
        self.emergency_keywords = ["severe", "critical", "unconscious", "bleeding heavily", "not breathing", "chest pain"]
        
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different intents"""
        return {
            "symptom_check": [
                "Based on your symptoms, I recommend {advice}. Please consult a doctor if symptoms persist.",
                "The symptoms you described could indicate {condition}. It's important to {action}.",
                "For your symptoms of {symptoms}, you should {recommendation}."
            ],
            "disease_info": [
                "{disease} is a condition that affects {affected_area}. Common symptoms include {symptoms}. Treatment typically involves {treatment}.",
                "Here's what you should know about {disease}: {information}. For more details, consult a healthcare provider.",
                "{disease}: {description} Prevention includes {prevention_methods}."
            ],
            "treatment": [
                "Treatment for {condition} usually includes {treatments}. Always consult a doctor before starting any treatment.",
                "Common treatments for {condition} are {treatments}. Home remedies include {home_remedies}.",
                "Medical professionals often recommend {treatments} for {condition}. Follow-up care is important."
            ],
            "prevention": [
                "To prevent {disease}, you can {prevention_tips}. Vaccination is also recommended if available.",
                "Preventive measures for {disease} include {measures}. Maintaining good hygiene is essential.",
                "The best ways to prevent {disease} are: {prevention_list}. Regular check-ups help with early detection."
            ],
            "emergency": [
                "⚠️ This appears to be an emergency situation. Please call emergency services immediately!",
                "🚨 URGENT: Based on your description, seek immediate medical attention. Call emergency services or go to the nearest hospital.",
                "⚠️ EMERGENCY ALERT: Do not wait - get medical help right away. Call emergency services now!"
            ],
            "vaccine": [
                "The {vaccine_name} vaccine is recommended for {age_group}. It protects against {diseases}. Common side effects include {side_effects}.",
                "Vaccination schedule for {vaccine_name}: {schedule}. Consult your doctor for personalized advice.",
                "{vaccine_name}: {efficacy} effective. Booster doses may be needed every {booster_interval}."
            ],
            "outbreak": [
                "Current outbreak status: {status}. Affected areas include {areas}. Prevention measures: {measures}",
                "According to health authorities, {disease} outbreak is {severity}. Recommended actions: {actions}",
                "Outbreak alert: {disease} cases reported in {location}. Please follow these guidelines: {guidelines}"
            ],
            "general": [
                "Thank you for your query. For health concerns, it's always best to consult with a healthcare professional.",
                "I understand your concern. While I can provide general information, please consult a doctor for personalized medical advice.",
                "Here's some general information: {info}. Would you like to know more about specific aspects?"
            ]
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query and return response"""
        query_lower = query.lower()
        
        # Check for emergency first
        if self._is_emergency(query_lower):
            return self._get_emergency_response()
        
        # Detect intent
        intent, confidence = self._detect_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Generate response based on intent
        response = self._generate_response(intent, entities, query_lower)
        
        # Determine if voice is needed
        needs_voice = intent in ["emergency", "first_aid"] or len(response) > 300
        
        return {
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "needs_voice": needs_voice
        }
    
    def _is_emergency(self, text: str) -> bool:
        """Check if query indicates emergency"""
        emergency_phrases = [
            "heart attack", "severe bleeding", "can't breathe", "unconscious",
            "suicide", "kill myself", "emergency", "call ambulance",
            "chest pain", "stroke", "severe allergic reaction"
        ]
        
        for phrase in emergency_phrases:
            if phrase in text:
                return True
        
        # Check for severity indicators
        severity_count = sum(1 for keyword in self.emergency_keywords if keyword in text)
        return severity_count >= 2
    
    def _detect_intent(self, text: str) -> Tuple[str, float]:
        """Detect intent from user query"""
        intent_scores = {}
        
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                intent_scores[intent] = score / len(keywords)
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            return best_intent, intent_scores[best_intent]
        
        return "general", 0.3
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract important entities from query"""
        entities = {
            "symptoms": [],
            "diseases": [],
            "medications": [],
            "body_parts": [],
            "age_group": None,
            "duration": None
        }
        
        # Common symptoms
        symptoms_list = [
            "fever", "cough", "headache", "pain", "nausea", "vomiting",
            "fatigue", "weakness", "dizziness", "rash", "swelling"
        ]
        
        for symptom in symptoms_list:
            if symptom in text:
                entities["symptoms"].append(symptom)
        
        # Body parts
        body_parts = [
            "head", "chest", "stomach", "back", "throat", "nose", "ear",
            "eye", "arm", "leg", "hand", "foot", "neck", "shoulder"
        ]
        
        for part in body_parts:
            if part in text:
                entities["body_parts"].append(part)
        
        # Age group detection
        age_patterns = {
            "child": ["child", "kid", "baby", "infant", "toddler"],
            "adult": ["adult", "grown", "elder", "man", "woman"],
            "elderly": ["elderly", "senior", "old", "aging"]
        }
        
        for group, keywords in age_patterns.items():
            if any(keyword in text for keyword in keywords):
                entities["age_group"] = group
                break
        
        return entities
    
    def _generate_response(self, intent: str, entities: Dict, query: str) -> str:
        """Generate response based on intent and entities"""
        if intent == "emergency":
            return self._get_emergency_response()
        
        # Get template for intent
        templates = self.response_templates.get(intent, self.response_templates["general"])
        template = templates[0]  # Use first template for simplicity
        
        # Customize response based on entities
        response = self._customize_response(template, intent, entities, query)
        
        return response
    
    def _customize_response(self, template: str, intent: str, entities: Dict, query: str) -> str:
        """Customize response with specific information"""
        if intent == "symptom_check":
            if entities["symptoms"]:
                symptoms = ", ".join(entities["symptoms"])
                advice = "rest and stay hydrated"
                condition = "a common viral infection"
                action = "monitor your symptoms"
                recommendation = "take rest and consult a doctor if symptoms worsen"
                
                response = template.format(
                    advice=advice,
                    condition=condition,
                    symptoms=symptoms,
                    action=action,
                    recommendation=recommendation
                )
            else:
                response = "I notice you're describing some symptoms. For accurate advice, please specify what symptoms you're experiencing (e.g., fever, cough, headache)."
        
        elif intent == "disease_info":
            response = template.format(
                disease="the condition you mentioned",
                affected_area="various parts of the body",
                symptoms="varying symptoms",
                treatment="medical consultation",
                information="consult a healthcare provider for accurate diagnosis",
                description="Medical conditions vary greatly between individuals",
                prevention_methods="healthy lifestyle and regular check-ups"
            )
        
        elif intent == "treatment":
            response = template.format(
                condition="your condition",
                treatments="rest and medication as prescribed",
                home_remedies="proper rest, hydration, and nutrition"
            )
        
        elif intent == "prevention":
            response = template.format(
                disease="the disease",
                prevention_tips="maintain good hygiene and get vaccinated",
                measures="regular hand washing and social distancing",
                prevention_list="vaccination, hygiene, healthy lifestyle"
            )
        
        elif intent == "vaccine":
            response = template.format(
                vaccine_name="the recommended vaccine",
                age_group="your age group",
                diseases="specific diseases",
                side_effects="mild fever or soreness",
                schedule="as per national immunization schedule",
                efficacy="highly",
                booster_interval="recommended interval"
            )
        
        elif intent == "outbreak":
            response = template.format(
                status="currently being monitored",
                areas="affected regions",
                measures="follow health guidelines",
                disease="the disease",
                severity="being assessed",
                actions="stay informed and follow local health advisories",
                location="various locations",
                guidelines="maintain hygiene and avoid crowded places"
            )
        
        else:
            response = template.format(info="health awareness is important for everyone")
        
        # Add disclaimer for medical queries
        if intent not in ["emergency", "general"]:
            response += " Remember, this is general information. Please consult a healthcare professional for medical advice."
        
        return response
    
    def _get_emergency_response(self) -> str:
        """Get emergency response message"""
        return "⚠️ **EMERGENCY ALERT** ⚠️\n\nBased on your description, you may need immediate medical attention.\n\nPlease call emergency services (911, 108, or your local emergency number) immediately or go to the nearest hospital.\n\nDo not wait - your health and safety are most important!"