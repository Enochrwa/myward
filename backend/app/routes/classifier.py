from fastapi import FastAPI, File, UploadFile, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from io import BytesIO
from PIL import Image
import numpy as np
import json
import tensorflow as tf




router = APIRouter(prefix="/ml")

# 1. Load classifier + class names once at startup
model = tf.keras.models.load_model("ML_Res/clothing_resnet50.keras")
with open("ML_Res/class_names.json", "r") as f:
    class_indices = json.load(f)
class_names = list(class_indices.keys())

def predict_class_from_pil(img: Image.Image) -> str:
    img = img.resize((224, 224))
    arr = np.array(img) / 255.0
    x = np.expand_dims(arr, axis=0)
    preds = model.predict(x, verbose=0)
    return class_names[int(np.argmax(preds))]

@router.post("/predict-multiple/")
async def predict_multiple(
    files: List[UploadFile] = File(...),
):
    """
    Accepts multiple image files, returns a list of
    { filename, predicted_class } objects.
    """
    results = []
    for file in files:
        contents = await file.read()
        img = Image.open(BytesIO(contents)).convert("RGB")
        cat = predict_class_from_pil(img)
        results.append({"filename": file.filename, "category": cat})
    return {"predictions": results}


