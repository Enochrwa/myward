import os
import numpy as np
import pickle
from sklearn.neighbors import NearestNeighbors
import joblib  # You can also use joblib to save the model

# 📁 Path to the saved features and filenames
features_path = "AI/features.npy"
filenames_path = "AI/filenames.pkl"

# 💾 Load the saved features and filenames
features = np.load(features_path)
with open(filenames_path, "rb") as f:
    filenames = pickle.load(f)

# 🤖 Train Nearest Neighbors model on the loaded features
knn = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='euclidean')
knn.fit(features)

# 💾 Save the newly trained KNN model using joblib (or pickle)
model_save_path = "AI/knn_model.joblib"  # Or you can use pickle instead of joblib
joblib.dump(knn, model_save_path)

print("✅ KNN model retrained and saved successfully!")
