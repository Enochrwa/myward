# data_pipeline.py
import tensorflow as tf
import pandas as pd
import os

AUTOTUNE = tf.data.AUTOTUNE

def parse_csv_line(image_root):
    def _fn(image_path, label):
        # image_path is a tf.string tensor like "img/Blouse/…"
        # Join root + image_path into one full filepath tensor:
        full_path = tf.strings.join([image_root, image_path], separator=os.sep)
        # Read & decode
        image = tf.io.read_file(full_path)
        image = tf.image.decode_jpeg(image, channels=3)
        image = tf.image.resize(image, [224, 224])
        image = image / 255.0
        return image, label
    return _fn

def make_dataset(csv_path, image_root, batch_size=32, shuffle=False):
    # Load the CSV with pandas
    df = pd.read_csv(csv_path)
    paths = df['image_path'].values.astype(str)
    labels = df['category_id'].values.astype(int)

    # Build TF dataset
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(paths))
    # Map the parser, batch, prefetch
    ds = ds.map(parse_csv_line(image_root), num_parallel_calls=AUTOTUNE)
    ds = ds.batch(batch_size).prefetch(AUTOTUNE)
    return ds
