from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import json

model = load_model("ML_Res/clothing_resnet50.keras")


with open("ML_Res/class_names.json", "r") as f:
    class_indices = json.load(f)
class_names = list(class_indices.keys())

def predict_class(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img) / 255.0
    x = np.expand_dims(x, axis=0)
    pred = model.predict(x, verbose=0)
    return class_names[np.argmax(pred)]

def parse_filename(filename):
    parts = filename.split("_")
    return {
        "color": parts[0],
        "gender": parts[1],
        "occasion": parts[2],
        "type": parts[3]  # may include extension, strip it with .split(".")[0]
    }



results = predict_class("train/tshirt/white_man_party_tshirt_26.jpg")
# metadata = parse_filename("train/dress/black_girl_defense_dress_1.jpg")
print(f"predicted class: {results}")


