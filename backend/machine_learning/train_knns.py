import os
import json
import numpy as np
import joblib
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from sklearn.neighbors import NearestNeighbors

# === Config ===
data_dir = "train"
ml_ready_dir = "ML_Ready"
feature_model_name = "resnet50_features.joblib"
file_map_name = "file_map.json"
knn_template = "knn_{category}.joblib"

# Create output directory
os.makedirs(ml_ready_dir, exist_ok=True)

# 1. Init ResNet50 feature extractor
base = ResNet50(weights="imagenet", include_top=False, pooling="avg")
feature_model = Model(base.input, base.output)

# 2. Walk directories & extract features
features = {}
file_map = {}
for category in os.listdir(data_dir):
    cat_path = os.path.join(data_dir, category)
    if not os.path.isdir(cat_path):
        continue
    feats, files = [], []
    print(f"Processing category: {category}")
    for fname in os.listdir(cat_path):
        img_path = os.path.join(cat_path, fname)
        try:
            img = image.load_img(img_path, target_size=(224, 224))
        except Exception as e:
            print(f"Skipping {img_path}: {e}")
            continue
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        f = feature_model.predict(x, verbose=0).flatten()
        f /= np.linalg.norm(f)
        feats.append(f)
        files.append(img_path)
    features[category] = np.vstack(feats)
    file_map[category] = files

# 3. Save compressed features and file map
feature_path = os.path.join(ml_ready_dir, feature_model_name)
joblib.dump(features, feature_path, compress=3)
print(f"Saved features to {feature_path}")

file_map_path = os.path.join(ml_ready_dir, file_map_name)
with open(file_map_path, 'w') as f:
    json.dump(file_map, f)
print(f"Saved file map to {file_map_path}")

# 4. Train and save a KNN per category
for category, feats in features.items():
    print(f"Training KNN for {category} ({feats.shape[0]} samples)")
    knn = NearestNeighbors(n_neighbors=5, metric="euclidean")
    knn.fit(feats)
    knn_path = os.path.join(ml_ready_dir, knn_template.format(category=category))
    joblib.dump(knn, knn_path, compress=3)
    print(f"Saved KNN model to {knn_path}")

print("All features and KNN models are ready in ML_Ready directory.")
