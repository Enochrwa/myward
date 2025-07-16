# predict.py
import tensorflow as tf
import numpy as np

def load_labels(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]

def preprocess(img_path):
    img = tf.io.read_file(img_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, [224,224])
    img = img / 255.0
    return tf.expand_dims(img, 0)  # add batch dim

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python predict.py /path/to/image.jpg")
        sys.exit(1)

    img_path = sys.argv[1]
    labels   = load_labels('data/categories.txt')
    model     = tf.keras.models.load_model('models/resnet50_clf')

    img_tensor = preprocess(img_path)
    logits = model(img_tensor, training=False).numpy()[0]
    idx   = np.argmax(logits)
    score = logits[idx]

    print(f"Predicted: {labels[idx]}  (confidence: {score:.3f})")
