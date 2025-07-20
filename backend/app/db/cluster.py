import numpy as np
import json
from sklearn.cluster import KMeans
from database import get_database_connection

# ------------------ Settings ----------------------
DEFAULT_N_CLUSTERS = 5
MIN_SAMPLES_FOR_CLUSTERING = 10  # skip if too few items
# ---------------------------------------------------

# Define clothing parts and categories
CLOTHING_PARTS = {
    "top": ["shirt", "tshirt", "blouse", "sweater", "hoodie", "croptop"],
    "bottom": ["jeans", "trousers", "shorts", "skirt"],
    "outerwear": ["jacket", "coat", "overcoat", "blazers"],
    "full_body": ["dress", "suit"],
    "accessory": ["bag", "shoes", "sunglasses", "hat"]
}


def cluster_part(cursor, categories, part_name):
    placeholders = ",".join(["%s"] * len(categories))
    cursor.execute(f"""
        SELECT id, resnet_features FROM images 
        WHERE category IN ({placeholders})
    """, tuple(categories))
    
    rows = cursor.fetchall()
    if not rows:
        print(f"No data for part: {part_name}")
        return

    features = []
    ids = []

    for row in rows:
        try:
            vec = np.array(json.loads(row["resnet_features"]), dtype=np.float32)
            features.append(vec)
            ids.append(row["id"])
        except Exception as e:
            continue

    if len(features) < MIN_SAMPLES_FOR_CLUSTERING:
        print(f"Skipping {part_name} due to too few samples ({len(features)})")
        return

    features = np.vstack(features)
    n_clusters = min(DEFAULT_N_CLUSTERS, len(features))

    print(f"Clustering {len(features)} items in '{part_name}' into {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(features)

    for idx, cluster_id in zip(ids, clusters):
        cursor.execute(
            "UPDATE images SET cluster_id = %s WHERE id = %s", 
            (int(cluster_id), idx)
        )


def main():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    for part, categories in CLOTHING_PARTS.items():
        cluster_part(cursor, categories, part)

    connection.commit()
    cursor.close()
    connection.close()
    print("✅ Clustering done for all clothing parts.")


if __name__ == "__main__":
    main()
