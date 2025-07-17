import os
from fastapi import FastAPI, File, UploadFile
from dotenv import load_dotenv
import boto3
load_dotenv()

app = FastAPI()
rekognition = boto3.client('rekognition',
                           region_name = 'ap-south-1',
                            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")   
                        )
MODEL_ARN = os.getenv("MODEL_ARN")

# @app.post("/predict/")
# async def predict_image(file: UploadFile = File(...)):
#     try:
#         image_bytes = await file.read()
#         print("Received image of size:", len(image_bytes))

#         response = rekognition.detect_custom_labels(
#             ProjectVersionArn=MODEL_ARN,
#             Image={'Bytes': image_bytes}
#         )

#         final_response = response["CustomLabels"]
        
#         for label in final_response:
#             if label["Confidence"]<80:
#                 return {
#                     "message":"Please upload a valid vegetable image",
#                     "status":200,    
#                 }
            
#             return {
#                 "message":"Classifies Disease",
#                 "status":200,
#                 "data":{
#                     "label":label["Name"],
#                     "confidence":label["Confidence"]
#                 }
#             }

#         return {"error": "Something went wrong... please try again"}

#     except Exception as e:
#         return {"error": str(e)}

@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return {
                "message": "Unsupported file format. Please upload a JPG or PNG image.",
                "status":415
                }

        image_bytes = await file.read()
        print("Received image of size:", len(image_bytes))

        response = rekognition.detect_custom_labels(
            ProjectVersionArn=MODEL_ARN,
            Image={'Bytes': image_bytes}
        )

        print("response:",response)
        
        final_response = response.get("CustomLabels", [])
        
        if not final_response:
            return {
                "message": "No disease detected. Please upload a clearer vegetable image.",
                "status": 404
            }

        valid_labels = [
            {"label": label["Name"], "confidence": label["Confidence"]}
            for label in final_response if label["Confidence"] >= 80
        ]

        if not valid_labels:
            return {
                "message": "All detected labels have low confidence. Please try again.",
                "status": 404
            }

        return {
            "message": "Disease(s) classified successfully",
            "status": 200,
            "data": valid_labels
        }

    except Exception as e:
        print("Exception error:",str(e))
        return {
            "message": "Invalid Image format",
            "status": 422
            }