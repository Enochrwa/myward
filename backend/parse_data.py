# build_label_map.py
import os

def load_label_map(path):
    # Skips first two header lines
    labels = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()[2:]
    for ln in lines:
        name, _ = ln.rsplit(None, 1)
        labels.append(name)
    return labels

if __name__ == "__main__":
    anno = "images/benchmarks/Anno_coarse/list_category_cloth.txt"
    category_names = load_label_map(anno)
    # Save to disk for later (or just import this file)
    with open("data/categories.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(category_names))
    print(f"Loaded {len(category_names)} categories.")
