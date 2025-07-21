import os
import io
import boto3

from fastapi import FastAPI, File, UploadFile, Path
from dotenv import load_dotenv
from PIL import Image
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
        "English": "model is not running",
        "Hindi": "मॉडल नहीं चल रहा है",
        "Gujarati": "મોડેલ ચાલી રહ્યું નથી",
    }
}

def compress_image(raw_image_bytes):
    image = Image.open(io.BytesIO(raw_image_bytes))

    max_dimension = 4096
    if image.width > max_dimension or image.height > max_dimension:
        image.thumbnail((max_dimension, max_dimension))  # Keeps aspect ratio

    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=85)

    print("Image dimension:", image.size)
    return buffer.getvalue()


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

        raw_image_bytes = await file.read()
        image = Image.open(io.BytesIO(raw_image_bytes))
        print("Received image of size:", len(raw_image_bytes))
        print("Recieved image dimensions:", image.size)

        if len(raw_image_bytes) > 4_000_000 or image.width > 4096 or image.height > 4096:
            image_bytes = compress_image(raw_image_bytes)
        else:
            image_bytes = raw_image_bytes

        response = rekognition.detect_custom_labels(
            ProjectVersionArn=MODEL_ARN,
            Image={'Bytes': image_bytes}
        )

        print("response:", response)

        final_response = response.get("CustomLabels", [])
        label = final_response[0]["Name"]

        if not final_response or label == "Irrelevant":
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
            # "message": MESSAGES["invalid_image"].get(language.lower(), "Image size is too large or model is not running"),
            "message": MESSAGES["invalid_image"].get(language, "model is not running"),
            "status": 422
        }

# response = rekognition.describe_project_versions(ProjectArn="arn:aws:rekognition:ap-south-1:070290473916:project/vegetable-disease-detection/1752564867963")
# for version in response['ProjectVersionDescriptions']:
#     print(version['ProjectVersionArn'], version['Status'])
