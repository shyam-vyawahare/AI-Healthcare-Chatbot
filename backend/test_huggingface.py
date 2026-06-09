from huggingface_translate_service import huggingface_translate_service

def test_translations():
    print("=" * 60)
    print("Testing HuggingFace Translation Service")
    print("=" * 60)
    
    # Test 1: Language Detection
    print("\n1. Language Detection:")
    hindi_text = "मुझे बुखार और सिरदर्द है"
    detected = huggingface_translate_service.detect_language(hindi_text)
    print(f"Text: {hindi_text}")
    print(f"Detected: {detected}")
    
    # Test 2: Hindi to English
    print("\n2. Hindi to English:")
    english = huggingface_translate_service.translate_to_english(hindi_text)
    print(f"Hindi: {hindi_text}")
    print(f"English: {english}")
    
    # Test 3: English to Hindi
    print("\n3. English to Hindi:")
    hindi = huggingface_translate_service.translate_from_english(english, 'hi')
    print(f"English: {english}")
    print(f"Hindi: {hindi}")

if __name__ == "__main__":
    test_translations()