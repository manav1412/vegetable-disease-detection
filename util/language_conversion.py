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
                return "અપ્રસ્તુત"
        else:
            if text == "Tomato Anthrocnose":
                return "टमाटर एन्थ्रेक्नोज"
            elif text == "Tomato Early blight ":
                return "टमाटर का शीघ्र झुलसा रोग"
            elif text == "Tomato-Powdery Mildew":
                return "पाउडरी मिल्ड्यू"
            else:
                return "अप्रासंगिक"
    except Exception as e:
        return f"Translation failed: {e}"