from translation_service import translation_service

# Test English to Hindi
english_text = "I have fever and headache. Please rest and stay hydrated."
hindi_text = translation_service.translate_from_english(english_text, 'hi')
print(f"English: {english_text}")
print(f"Hindi: {hindi_text}")
print("-" * 50)

# Test English to Marathi
marathi_text = translation_service.translate_from_english(english_text, 'mr')
print(f"Marathi: {marathi_text}")
print("-" * 50)

# Test Hindi detection
hindi_input = "मुझे बुखार और सिरदर्द है"
detected = translation_service.detect_language(hindi_input)
english = translation_service.translate_to_english(hindi_input)
print(f"Hindi detected: {detected}")
print(f"Translated to English: {english}")