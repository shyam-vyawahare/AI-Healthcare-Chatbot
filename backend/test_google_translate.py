from google_translate_service import google_translate_service

# Main function for language translations
def test_translations():
    print("=" * 60)
    print("Testing Google Cloud Translate API")
    print("=" * 60)
    
    # Test 1: Detect language
    print("\n1. Language Detection:")
    hindi_text = "मुझे बुखार और सिरदर्द है"
    detected = google_translate_service.detect_language(hindi_text)
    print(f"Text: {hindi_text}")
    print(f"Detected: {detected}")
    
    # Test 2: Translate to English
    print("\n2. Hindi to English:")
    english = google_translate_service.translate_to_english(hindi_text)
    print(f"Hindi: {hindi_text}")
    print(f"English: {english}")
    
    # Test 3: English to Hindi
    print("\n3. English to Hindi:")
    hindi = google_translate_service.translate_from_english(english, 'hi')
    print(f"English: {english}")
    print(f"Hindi: {hindi}")
    
    # Test 4: English to Marathi
    print("\n4. English to Marathi:")
    marathi = google_translate_service.translate_from_english(english, 'mr')
    print(f"Marathi: {marathi}")
    
    # Test 5: Round trip
    print("\n5. Round Trip Test:")
    original = "I have a fever and headache"
    translated = google_translate_service.translate_from_english(original, 'hi')
    back = google_translate_service.translate_to_english(translated)
    print(f"Original: {original}")
    print(f"To Hindi: {translated}")
    print(f"Back to English: {back}")

if __name__ == "__main__":
    test_translations()
