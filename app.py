import os
from fastapi import FastAPI, File, UploadFile, Path
from dotenv import load_dotenv
import boto3

load_dotenv()

app = FastAPI()

rekognition = boto3.client('rekognition',
    region_name='ap-south-1',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

MODEL_ARN = os.getenv("MODEL_ARN")

# Multilingual messages
MESSAGES = {
    "unsupported_format": {
        "english": "Unsupported file format. Please upload a JPG or PNG image.",
        "hindi": "असमर्थित फ़ाइल प्रारूप। कृपया JPG या PNG छवि अपलोड करें।",
        "gujrati": "અસમર્થિત ફાઇલ ફોર્મેટ. કૃપા કરીને JPG અથવા PNG છબી અપલોડ કરો.",
        "marathi": "असमर्थित फाईल फॉरमॅट. कृपया JPG किंवा PNG इमेज अपलोड करा."
    },
    "no_disease": {
        "english": "No disease detected. Please upload a clearer vegetable image.",
        "hindi": "कोई बीमारी नहीं पाई गई। कृपया एक स्पष्ट सब्ज़ी की छवि अपलोड करें।",
        "gujrati": "કોઈ રોગ મળ્યો નથી. કૃપા કરીને વધુ સ્પષ્ટ શાકભાજીની છબી અપલોડ કરો.",
        "marathi": "कोणताही आजार आढळला नाही. कृपया अधिक स्पष्ट भाजीपाला प्रतिमा अपलोड करा."
    },
    "low_confidence": {
        "english": "All detected labels have low confidence. Please try again.",
        "hindi": "सभी पाए गए लेबल में आत्मविश्वास कम है। कृपया पुनः प्रयास करें।",
        "gujrati": "બધા શોધાયેલા લેબલ્સમાં નબળું વિશ્વાસ છે. કૃપા કરીને ફરી પ્રયાસ કરો.",
        "marathi": "सर्व सापडलेल्या लेबल्समध्ये कमी खात्री आहे. कृपया पुन्हा प्रयत्न करा."
    },
    "success": {
        "english": "Disease(s) classified successfully",
        "hindi": "बीमारी(यों) को सफलतापूर्वक वर्गीकृत किया गया",
        "gujrati": "રોગ(ઓ)ની સફળતાપૂર્વક વર્ગીકરણ થયું છે",
        "marathi": "आजारांचे यशस्वी वर्गीकरण झाले आहे"
    },
    "invalid_image": {
        "english": "Invalid Image format",
        "hindi": "अमान्य छवि प्रारूप",
        "gujrati": "અમાન્ય છબી ફોર્મેટ",
        "marathi": "अवैध प्रतिमा स्वरूप"
    }
}

@app.post("/predict/{language}/")
async def predict_image(
    language: str = Path(..., regex="^(english|hindi|gujrati|marathi)$"),
    file: UploadFile = File(...)
):
    try:
        lang = language.lower()

        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return {
                "message": MESSAGES["unsupported_format"][lang],
                "status": 415
            }

        image_bytes = await file.read()
        print("Received image of size:", len(image_bytes))

        response = rekognition.detect_custom_labels(
            ProjectVersionArn=MODEL_ARN,
            Image={'Bytes': image_bytes}
        )

        print("response:", response)

        final_response = response.get("CustomLabels", [])

        if not final_response:
            return {
                "message": MESSAGES["no_disease"][lang],
                "status": 404
            }

        valid_labels = [
            {"label": label["Name"], "confidence": label["Confidence"]}
            for label in final_response if label["Confidence"] >= 80
        ]

        if not valid_labels:
            return {
                "message": MESSAGES["low_confidence"][lang],
                "status": 404
            }

        return {
            "message": MESSAGES["success"][lang],
            "status": 200,
            "data": valid_labels
        }

    except Exception as e:
        print("Exception error:", str(e))
        return {
            "message": MESSAGES["invalid_image"].get(language.lower(), "Invalid Image format"),
            "status": 422
        }
