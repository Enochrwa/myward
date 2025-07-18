import os
import json
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (Conv2D, MaxPooling2D, Flatten,
                                     Dense, Dropout, BatchNormalization)
from tensorflow.keras.optimizers import Adam

# === CONFIGURATION ===
DATA_DIR = "train"  # path to your image folder
IMG_SIZE = (128, 128)  # smaller size for CPU training
BATCH_SIZE = 32
EPOCHS = 60
LEARNING_RATE = 1e-4
MODEL_SAVE_PATH = "Custom_ML/custom_cnn_model.keras"
CLASS_NAMES_PATH = "Custom_ML/custom_cnn_classes.json"
PLOT_PATH = "Custom_ML/training_plot.png"

# === DATA PREPROCESSING ===
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    zoom_range=0.1,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest'
)

train_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

# === MODEL DEFINITION ===
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(*IMG_SIZE, 3)),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    Conv2D(64, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    Conv2D(128, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(train_gen.num_classes, activation='softmax')
])

model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# === TRAINING ===
history = model.fit(
    train_gen,
    epochs=EPOCHS,
    verbose=1
)

# === SAVE MODEL AND CLASSES ===
os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
model.save(MODEL_SAVE_PATH)

with open(CLASS_NAMES_PATH, "w") as f:
    json.dump(train_gen.class_indices, f)

# === PLOT TRAINING CURVES ===
plt.figure(figsize=(8, 4))
plt.plot(history.history["accuracy"], label="Accuracy")
plt.plot(history.history["loss"], label="Loss")
plt.title("Training Accuracy and Loss")
plt.xlabel("Epoch")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(PLOT_PATH)
plt.show()
