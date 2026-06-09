"""
Disease Awareness Module
Static database of diseases with symptoms, prevention, and care tips
"""

class DiseaseData:
    """Class to manage disease information"""
    
    def __init__(self):
        self.diseases = {
            "covid19": {
                "name": "COVID-19",
                "symptoms": [
                    "Fever or chills",
                    "Cough", 
                    "Shortness of breath",
                    "Fatigue",
                    "Muscle or body aches",
                    "Headache",
                    "New loss of taste or smell",
                    "Sore throat",
                    "Congestion or runny nose"
                ],
                "prevention": [
                    "Get vaccinated and boosted",
                    "Wear a mask in crowded places",
                    "Maintain 6 feet distance",
                    "Wash hands frequently with soap",
                    "Use hand sanitizer with 60%+ alcohol",
                    "Avoid touching face",
                    "Stay home when sick"
                ],
                "basic_care": [
                    "Rest and stay hydrated",
                    "Take over-the-counter fever reducers",
                    "Monitor oxygen levels with pulse oximeter",
                    "Isolate from family members",
                    "Use separate bathroom if possible"
                ],
                "when_to_see_doctor": "Seek immediate medical attention if you have: Trouble breathing, Persistent chest pain, New confusion, Inability to wake or stay awake, Bluish lips or face"
            },
            
            "dengue": {
                "name": "Dengue Fever",
                "symptoms": [
                    "Sudden high fever (104°F/40°C)",
                    "Severe headache (especially behind eyes)",
                    "Severe joint and muscle pain",
                    "Nausea and vomiting",
                    "Skin rash (appears 2-5 days after fever)",
                    "Mild bleeding (nose/gums)"
                ],
                "prevention": [
                    "Use mosquito repellent (DEET, picaridin)",
                    "Wear long sleeves and pants",
                    "Use mosquito nets while sleeping",
                    "Remove standing water around home",
                    "Install window screens",
                    "Use mosquito coils or vaporizers"
                ],
                "basic_care": [
                    "Take paracetamol (NOT aspirin or ibuprofen)",
                    "Drink plenty of fluids (ORS, coconut water)",
                    "Get complete rest",
                    "Monitor for warning signs",
                    "Keep fever under control"
                ],
                "when_to_see_doctor": "Warning signs require immediate hospital visit: Severe abdominal pain, Persistent vomiting, Bleeding gums, Blood in vomit, Rapid breathing, Fatigue/restlessness"
            },
            
            "malaria": {
                "name": "Malaria",
                "symptoms": [
                    "High fever (cycles of chills, fever, sweating)",
                    "Severe shaking chills",
                    "Headache",
                    "Muscle pain",
                    "Nausea and vomiting",
                    "Fatigue and weakness"
                ],
                "prevention": [
                    "Use insecticide-treated bed nets",
                    "Apply mosquito repellent",
                    "Take preventive medication if traveling",
                    "Wear protective clothing",
                    "Spray insecticides in living areas",
                    "Avoid outdoor activities at dusk/dawn"
                ],
                "basic_care": [
                    "Seek immediate medical testing",
                    "Take prescribed antimalarial drugs",
                    "Complete full course of medication",
                    "Get plenty of rest",
                    "Maintain fluid intake"
                ],
                "when_to_see_doctor": "See doctor immediately if fever develops within 1 year of travel to malaria-endemic area. Emergency signs: Altered consciousness, Seizures, Difficulty breathing, Dark urine"
            },
            
            "diabetes": {
                "name": "Diabetes Mellitus",
                "symptoms": [
                    "Increased thirst (polydipsia)",
                    "Frequent urination (polyuria)",
                    "Extreme hunger (polyphagia)",
                    "Unexplained weight loss",
                    "Fatigue and weakness",
                    "Blurred vision",
                    "Slow-healing sores",
                    "Tingling/numbness in hands/feet"
                ],
                "prevention": [
                    "Maintain healthy body weight",
                    "Exercise 30 minutes daily",
                    "Eat balanced diet (more fiber, less sugar)",
                    "Limit processed foods and sugary drinks",
                    "Get regular blood sugar checkups",
                    "Avoid sedentary lifestyle"
                ],
                "basic_care": [
                    "Monitor blood sugar regularly",
                    "Take medications as prescribed",
                    "Follow diabetic diet plan",
                    "Exercise regularly",
                    "Check feet daily for sores",
                    "Keep vaccinations up to date"
                ],
                "when_to_see_doctor": "Emergency signs: Very high/low blood sugar symptoms, Fruity breath odor, Difficulty breathing, Confusion, Loss of consciousness"
            },
            
            "typhoid": {
                "name": "Typhoid Fever",
                "symptoms": [
                    "Prolonged fever (up to 104°F)",
                    "Headache",
                    "Stomach pain",
                    "Constipation or diarrhea",
                    "Loss of appetite",
                    "Rose-colored spots on chest"
                ],
                "prevention": [
                    "Get typhoid vaccine",
                    "Drink boiled/bottled water",
                    "Avoid raw fruits/vegetables",
                    "Wash hands frequently",
                    "Practice food safety",
                    "Avoid street food in endemic areas"
                ],
                "basic_care": [
                    "Take prescribed antibiotics",
                    "Get bed rest",
                    "Stay hydrated",
                    "Eat soft, digestible foods",
                    "Monitor temperature regularly"
                ],
                "when_to_see_doctor": "See doctor immediately if fever persists >3 days or if you have severe abdominal pain, bloody stools, or signs of dehydration"
            }
        }
    
    def get_all_diseases(self):
        """Return list of all available diseases"""
        return list(self.diseases.keys())
    
    def get_disease_info(self, disease_key):
        """Get complete information for a specific disease"""
        return self.diseases.get(disease_key.lower(), None)
    
    def search_diseases(self, query):
        """Search diseases by name or symptoms"""
        query = query.lower()
        results = []
        
        for key, disease in self.diseases.items():
            if (query in disease['name'].lower() or 
                any(query in symptom.lower() for symptom in disease['symptoms']) or
                any(query in prevention.lower() for prevention in disease['prevention'])):
                results.append({
                    'key': key,
                    'name': disease['name'],
                    'symptoms': disease['symptoms'][:3]  # Top 3 symptoms
                })
        
        return results
    
    def get_preventive_tips(self, disease_key):
        """Get only prevention tips for a disease"""
        disease = self.diseases.get(disease_key.lower())
        return disease['prevention'] if disease else[]
     
    def get_symptoms_checklist(self, disease_key):
        """Get symptoms checklist for awareness"""
        disease = self.diseases.get(disease_key.lower())
        return disease['symptoms'] if disease else []


# Create a singleton instance
disease_db = DiseaseData()