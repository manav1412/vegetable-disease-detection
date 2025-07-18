import os
from fastapi import FastAPI, File, UploadFile, Path
from dotenv import load_dotenv
import boto3

from util.language_conversion import translate_text

load_dotenv()

app = FastAPI()

rekognition = boto3.client('rekognition',
    region_name='ap-south-1',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

MODEL_ARN = os.getenv("MODEL_ARN")

MESSAGES = {
    "unsupported_format": {
        "English": "Unsupported file format. Please upload a JPG or PNG image.",
        "Hindi": "असमर्थित फ़ाइल प्रारूप। कृपया JPG या PNG फोटो अपलोड करें।",
        "Gujarati": "અસમર્થિત ફાઇલ ફોર્મેટ. કૃપા કરીને JPG અથવા PNG છબી અપલોડ કરો."
    },
    "no_disease": {
        "English": "No disease detected. Please upload a clearer vegetable image.",
        "Hindi": "कोई बीमारी नहीं पाई गई। कृपया एक स्पष्ट सब्ज़ी की छवि अपलोड करें।",
        "Gujarati": "કોઈ રોગ મળ્યો નથી. કૃપા કરીને વધુ સ્પષ્ટ શાકભાજીની છબી અપલોડ કરો."
    },
    "success": {
        "English": "Disease(s) classified successfully",
        "Hindi": "बीमारी(यों) को सफलतापूर्वक वर्गीकृत किया गया",
        "Gujarati": "રોગ(ઓ)ની સફળતાપૂર્વક વર્ગીકરણ થયું છે",
    },
    "invalid_image": {
        "English": "Invalid Image format",
        "Hindi": "अमान्य फोटो प्रारूप",
        "Gujarati": "અમાન્ય ફોટો ફોર્મેટ",
    }
}

# response = rekognition.describe_project_versions(ProjectArn="arn:aws:rekognition:ap-south-1:070290473916:project/vegetable-disease-detection/1752564867963")
# for version in response['ProjectVersionDescriptions']:
#     print(version['ProjectVersionArn'], version['Status'])


@app.post("/predict/{language}")
async def predict_image(
    language: str = Path(..., regex="^(English|Hindi|Gujarati)$"),
    file: UploadFile = File(...)
):
    try:
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return {
                "message": MESSAGES["unsupported_format"][language],
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
                "message": MESSAGES["no_disease"][language],
                "status": 404
            }

        valid_labels = [
            {
                "label": translate_text(label["Name"],language), 
                "confidence": label["Confidence"]
            }
            for label in final_response
        ]

        return {
            "message": MESSAGES["success"][language],
            "status": 200,
            "data": valid_labels
        }

    except Exception as e:
        print("Exception error:", str(e))
        return {
            "message": MESSAGES["invalid_image"].get(language.lower(), "Invalid Image format"),
            "status": 422
        }



@app.post("/predict/")
async def predict_image_without_lang(
    file: UploadFile = File(...)
):
    try:
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return {
                "message": "Unsupported file format. Please upload a JPG or PNG image.",
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
                "message": "No disease detected. Please upload a clearer vegetable image.",
                "status": 404
            }

        valid_labels = [
            {
                "label": label["Name"], 
                "confidence": label["Confidence"]
            }
            for label in final_response
        ]

        return {
            "message": "Disease(s) classified successfully",
            "status": 200,
            "data": valid_labels
        }

    except Exception as e:
        print("Exception error:", str(e))
        return {
            "message": "Invalid Image format",
            "status": 422
        }
    

@app.get("/test")
def test_api():
    return {
        "message":"Hello world"
        }