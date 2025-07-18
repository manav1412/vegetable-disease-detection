from deep_translator import GoogleTranslator

def translate_text(text: str, target_language: str) -> str:
    try:
        if target_language == "English":
            return text
        elif target_language == "Gujarati":
            if text == "Tomato Anthrocnose":
                return "ટામેટા એન્થ્રેકનોઝ રોગ"
            elif text == "Tomato Early blight ":
                return "ટમેટામાં વહેલું ટપકું"
            elif text == "Tomato-Powdery Mildew":
                return "ટામેટામાં ભૂકીછારો"
        else:
            if text == "Tomato Anthrocnose":
                return "टमाटर एन्थ्रेक्नोज"
            elif text == "Tomato Early blight ":
                return "टमाटर का शीघ्र झुलसा रोग"
            elif text == "Tomato-Powdery Mildew":
                return "पाउडरी मिल्ड्यू"
    except Exception as e:
        return f"Translation failed: {e}"







# import requests

# def transliterate_aksharamukha(text, target_script):
#     url = "https://aksharamukha.appspot.com/api/public"
#     params = {
#         "source": "ISO",       # ISO = English letters
#         "target": target_script,  # e.g., "Gujarati", "Devanagari"
#         "text": text
#     }

#     response = requests.get(url, params=params)
#     return response.text if response.ok else "Error"

# Examples:
# print("Hindi (Devanagari):", transliterate_aksharamukha("Tomato-anthracnose", "English"))
# print("Gujarati:", transliterate_aksharamukha("Tomato-anthracnose", "Gujarati"))

# print("Hindi (Devanagari):", transliterate_aksharamukha("Tomato-early blight", "Devanagari"))
# print("Gujarati:", transliterate_aksharamukha("Tomato-early blight", "Gujarati"))

# print("Hindi (Devanagari):", transliterate_aksharamukha("Tomato-Powdery mildew", "Devanagari"))
# print("Gujarati:", transliterate_aksharamukha("Tomato-Powdery mildew", "Gujarati"))








# from deep_translator import GoogleTranslator

# def change_langauge(text, language):
#     new_text = ""

#     if language == "hindi":
#         new_text = GoogleTranslator(source='en', target='hi').translate(text)   # Hindi
#     elif language == "gujrati":
#         new_text = GoogleTranslator(source='en', target='gu').translate(text)   # Gujarati
#     elif language == "english":
#         return text
#     else:
#         return "Language is invalid"

#     print("Transliteration:", new_text)
#     return new_text


# result = change_langauge("Tomato-powdery mildew", "hindi")
# print(result)
