import os
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.applications.resnet50 import decode_predictions  # Optional

# === CONFIG ===
MODEL_PATH = "ML_Res/clothing_resnet50.keras"
CLASS_NAMES_PATH = "ML_Res/class_names.json"
IMG_PATH = "train/croptop/black_girl_party_croptop_8.jpg"  # Replace with your image path
IMG_SIZE = (224, 224)

# === LOAD MODEL ===
model = load_model(MODEL_PATH)

# === LOAD CLASS LABELS ===
with open(CLASS_NAMES_PATH, 'r') as f:
    class_indices = json.load(f)

# Reverse dict: index → class name
idx_to_class = {v: k for k, v in class_indices.items()}

# === LOAD & PREPROCESS IMAGE ===
img = image.load_img(IMG_PATH, target_size=IMG_SIZE)
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

# === PREDICT ===
pred = model.predict(x)
pred_class = np.argmax(pred, axis=1)[0]
confidence = np.max(pred)

print(f"Predicted class: {idx_to_class[pred_class]}")
print(f"Confidence: {confidence:.4f}")
