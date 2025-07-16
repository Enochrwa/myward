import os
import numpy as np
import pickle
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import Model
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

# 📁 Path to image directory
image_dir = "fashion/images"
filenames = [os.path.join(image_dir, file) for file in os.listdir(image_dir)]

# 🧠 Load pre-trained ResNet50 for feature extraction
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
model = Model(inputs=base_model.input, outputs=base_model.output)

# 🧹 Feature extraction function
def extract_features(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = model.predict(img_array)
    flattened = features.flatten()
    normalized = flattened / np.linalg.norm(flattened)
    return normalized

# 🔁 Extract and store features
feature_list = []
for file in tqdm(filenames, desc="Extracting features"):
    try:
        feature = extract_features(file)
        feature_list.append(feature)
    except:
        print(f"Error with {file}")

# 💾 Save features and filenames
np.save("AI/features.npy", feature_list)
with open("AI/filenames.pkl", "wb") as f:
    pickle.dump(filenames, f)

# 🤖 Train Nearest Neighbors model
knn = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='euclidean')
knn.fit(feature_list)

# 💾 Save trained model
with open("AI/knn_model.pkl", "wb") as f:
    pickle.dump(knn, f)

print("✅ Feature extraction & model training complete. Models saved.")