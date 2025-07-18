import os
import json
import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
import matplotlib.pyplot as plt
from PIL import Image

# ── Config ──────────────────────────────────────────────────────────
ML_READY = "ML_Ready"
FEATURES_FN = "resnet50_features.joblib"
FILE_MAP_FN = "file_map.json"
KNN_TEMPLATE = "knn_{category}.joblib"
CLASSIFIER_FN = "ML_Res/clothing_resnet50.keras"
CLASS_NAMES_FN = "ML_Res/class_names.json"
TOP_K = 5  # how many neighbors per category

# ── Helper: Parse filename metadata robustly ─────────────────────────
def parse_metadata(path):
    fname = os.path.basename(path)
    parts = fname.split("_")
    # expected format: color_gender_occasion_type_idx.ext
    if len(parts) < 4:
        return {"color": None, "gender": None, "occasion": None}
    color = parts[0]
    gender = parts[1]
    occasion = parts[2]
    return {"color": color, "gender": gender, "occasion": occasion}

# ── Load Classifier & Class Names ───────────────────────────────────
classifier = load_model(CLASSIFIER_FN)
with open(CLASS_NAMES_FN, "r") as f:
    class_to_idx = json.load(f)               # e.g. {"Overcoat":0, ...}
idx_to_class = {v: k for k, v in class_to_idx.items()}

# ── Load Feature Extractor ──────────────────────────────────────────
base = ResNet50(weights="imagenet", include_top=False, pooling="avg")
feature_extractor = Model(inputs=base.input, outputs=base.output)

# ── Load Precomputed Data ───────────────────────────────────────────
features = joblib.load(os.path.join(ML_READY, FEATURES_FN))  # dict: cat → ndarray
with open(os.path.join(ML_READY, FILE_MAP_FN), "r") as f:
    file_map = json.load(f)                                 # dict: cat → [paths]

# build metadata_map: category → list of metadata dicts
metadata_map = {}
for cat, paths in file_map.items():
    metadata_map[cat] = [parse_metadata(p) for p in paths]

# ── Lazy‑load KNN models ────────────────────────────────────────────
_knn_cache = {}
def get_knn(category):
    if category not in _knn_cache:
        path = os.path.join(ML_READY, KNN_TEMPLATE.format(category=category))
        _knn_cache[category] = joblib.load(path)
    return _knn_cache[category]

# ── Predict category ────────────────────────────────────────────────
def predict_category(img_path):
    img = image.load_img(img_path, target_size=(224,224))
    x = np.expand_dims(image.img_to_array(img), 0) / 255.0
    probs = classifier.predict(x, verbose=0)[0]
    idx = np.argmax(probs)
    return idx_to_class[idx]

# ── Extract feature ─────────────────────────────────────────────────
def extract_feature(img_path):
    img = image.load_img(img_path, target_size=(224,224))
    x = np.expand_dims(image.img_to_array(img), 0)
    x = preprocess_input(x)
    f = feature_extractor.predict(x, verbose=0).flatten()
    return f / np.linalg.norm(f)

# ── Outfit Recommendation with metadata filtering ───────────────────
def recommend_outfit(img_path, top_k=TOP_K):
    query_cat = predict_category(img_path)
    query_meta = parse_metadata(img_path)
    query_feat = extract_feature(img_path)

    recs_all = {}
    for cat, feat_matrix in features.items():
        if cat == query_cat:
            continue
        knn = get_knn(cat)
        dists, idxs = knn.kneighbors([query_feat], n_neighbors=top_k * 3)

        candidates = [(idx, dist, metadata_map[cat][idx])
                      for idx, dist in zip(idxs[0], dists[0])]

        # filter by same occasion & gender when possible
        filtered = [c for c in candidates
                    if query_meta["occasion"] and query_meta["gender"]
                    and c[2]["occasion"] == query_meta["occasion"]
                    and c[2]["gender"]   == query_meta["gender"]]

        chosen = filtered[:top_k]
        if len(chosen) < top_k:
            used = {c[0] for c in chosen}
            for c in candidates:
                if c[0] not in used:
                    chosen.append(c)
                if len(chosen) == top_k:
                    break

        recs_all[cat] = [file_map[cat][c[0]] for c in chosen]

    return {"query_category": query_cat, "recommendations": recs_all}

# ── Display recommendations ─────────────────────────────────────────
def display_recommendations(img_path, recommendation_dict):
    query_arr = np.array(Image.open(img_path))
    categories = list(recommendation_dict.keys())
    n_rows = len(categories) + 1
    n_cols = len(recommendation_dict[categories[0]])

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*3, n_rows*3))
    fig.tight_layout(pad=2.0)

    for col in range(n_cols):
        ax = axes[0, col]
        ax.imshow(query_arr)
        ax.set_title(f"Query ({os.path.basename(img_path)})")
        ax.axis("off")

    for i, cat in enumerate(categories, start=1):
        for j, rec_path in enumerate(recommendation_dict[cat]):
            ax = axes[i, j]
            try:
                rec_arr = np.array(Image.open(rec_path))
                ax.imshow(rec_arr)
                ax.set_title(cat)
            except Exception:
                ax.text(0.5, 0.5, "Load error", ha='center')
            ax.axis("off")

    plt.show()

# ── Demo ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_img = "train/coats/black_girl_party_coat_003.jpg"
    result = recommend_outfit(test_img)
    print(json.dumps(result, indent=2))
    display_recommendations(test_img, result["recommendations"])
