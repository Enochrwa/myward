#!/usr/bin/env python3
import os
import re
import pandas as pd

# ── Configuration ────────────────────────────────────────────────────────────
ROOT       = 'images'                           # top‐level images folder
IMG_ROOT   = os.path.join(ROOT, 'img')                  # where all category subfolders live
ANNO_ROOT  = os.path.join(ROOT, 'benchmarks/Anno_coarse')
EVAL_FILE  = os.path.join(ROOT, 'benchmarks/Eval/list_eval_partition.txt')
OUT_DIR    = 'data'                             # where to write train/val/test CSVs
os.makedirs(OUT_DIR, exist_ok=True)
# ────────────────────────────────────────────────────────────────────────────

# 1) Load the train/val/test split
split_df = (
    pd.read_csv(
        EVAL_FILE,
        sep=r'\s+',
        names=['image','split'],
        header=1
    )
    .assign(image_path=lambda df: df['image'])
)

# 2) Load category mappings
cat_cloth = (
    pd.read_csv(
        os.path.join(ANNO_ROOT, 'list_category_cloth.txt'),
        sep=r'\s+',
        names=['category_name','category_type'],
        header=1
    )
    .reset_index()
    .rename(columns={'index':'category_id'})
)
cat_img = pd.read_csv(
    os.path.join(ANNO_ROOT, 'list_category_img.txt'),
    sep=r'\s+',
    names=['image','category_id'],
    header=1
)

# 3) Load attribute definitions with regex‐based parser
attr_pattern = re.compile(r'^(?P<name>.+?)\s+(?P<type>\d+)$')
attr_cloth_rows = []
bad_lines = []
with open(os.path.join(ANNO_ROOT, 'list_attr_cloth.txt'), 'r', encoding='utf-8') as f:
    for idx, ln in enumerate(f.read().splitlines()[2:], start=3):
        ln = ln.rstrip()
        if not ln:
            continue
        m = attr_pattern.match(ln)
        if not m:
            bad_lines.append((idx, ln))
            continue
        name = m.group('name')
        typ  = int(m.group('type'))
        attr_cloth_rows.append((name, typ))

if bad_lines:
    print(f"Warning: skipped {len(bad_lines)} malformed lines in list_attr_cloth.txt:")
    for lineno, text in bad_lines[:5]:
        print(f"  line {lineno}: '{text}'")
    if len(bad_lines) > 5:
        print("  ...")

attr_cloth = (
    pd.DataFrame(attr_cloth_rows, columns=['attr_name','attr_type'])
    .reset_index()
    .rename(columns={'index':'attr_id'})
)

# 4) Load per‑image attributes
attr_img = pd.read_csv(
    os.path.join(ANNO_ROOT, 'list_attr_img.txt'),
    sep=r'\s+',
    header=1,
    names=['image'] + [f'a{i}' for i in range(len(attr_cloth))]
)

# 5) Load bounding boxes
bbox = pd.read_csv(
    os.path.join(ANNO_ROOT, 'list_bbox.txt'),
    sep=r'\s+',
    names=['image','x1','y1','x2','y2'],
    header=1
)

# 6) Load landmarks
land_cols = (
    ['image','cloth_type','variation'] +
    [f'vis_{i}' for i in range(1,9)] +
    [f'x_{i}'   for i in range(1,9)] +
    [f'y_{i}'   for i in range(1,9)]
)
landmarks = pd.read_csv(
    os.path.join(ANNO_ROOT, 'list_landmarks.txt'),
    sep=r'\s+',
    names=land_cols,
    header=1
)

# 7) Merge everything
meta = (
    split_df
    .merge(cat_img,    on='image', how='left')
    .merge(attr_img,   on='image', how='left')
    .merge(bbox,       on='image', how='left')
    .merge(landmarks,  on='image', how='left')
)
meta['image_path'] = meta['image']

# 8) Write out train/val/test CSVs
for part in ('train','val','test'):
    df_part = meta[meta['split']==part].reset_index(drop=True)
    out_csv = os.path.join(OUT_DIR, f'{part}.csv')
    df_part.to_csv(out_csv, index=False)
    print(f'→ Wrote {len(df_part)} rows to {out_csv}')
