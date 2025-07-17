import joblib
import numpy as np
import pickle
import gzip
import shutil

# Paths for saving and loading
model_path = "AI/knn_model.joblib"
compressed_model_path = "AI/knn_model_compressed.joblib.gz"
features_path = "AI/features.npy"
filenames_path = "AI/filenames.pkl"

# Load the trained KNN model (joblib or pickle, depending on what you have saved earlier)
knn = joblib.load(model_path)  # If you're using joblib
# knn = pickle.load(open(model_path, "rb"))  # If you're using pickle

# Save the KNN model using pickle (no compression during saving)
pickle_model_path = "AI/knn_model_no_compression.pkl"
with open(pickle_model_path, 'wb') as f:
    pickle.dump(knn, f, protocol=pickle.HIGHEST_PROTOCOL)

print(f"KNN model saved without compression at {pickle_model_path}")

# Compress the saved pickle model using gzip
with open(pickle_model_path, 'rb') as f_in:
    with gzip.open(compressed_model_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

print(f"KNN model compressed using gzip at {compressed_model_path}")

# Now for the features (16GB)
features = np.load(features_path)

# Save the features in HDF5 format with compression (gzip)
import h5py

features_compressed_path = "AI/features_compressed.h5"
with h5py.File(features_compressed_path, "w") as f:
    f.create_dataset("features", data=features, compression="gzip", compression_opts=4)  # compression_opts is the level

print(f"Features saved and compressed at {features_compressed_path}")

# Optional: Save filenames (if needed for reference)
with open(filenames_path, "rb") as f:
    filenames = pickle.load(f)

print("Filenames loaded and ready for future use.")

# Example usage (Optional):
# For querying nearest neighbors, feature extraction, etc.
# Your querying code goes here...

