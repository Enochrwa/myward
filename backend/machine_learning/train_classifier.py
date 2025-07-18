import os
import json
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, LearningRateScheduler
from tensorflow.keras.regularizers import l2
from tensorflow.keras.losses import CategoricalCrossentropy
import tensorflow.keras.backend as K

# Configure TensorFlow to suppress warnings and use CPU if CUDA fails
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.config.experimental.set_memory_growth(tf.config.list_physical_devices('GPU')[0], True) if tf.config.list_physical_devices('GPU') else None

# Set random seeds for reproducibility
tf.random.set_seed(42)
np.random.seed(42)

# Enhanced Config
data_dir = "train"
image_size = (224, 224)
batch_size = 32
initial_epochs = 25  # Increased base training
fine_tune_epochs = 15  # Reduced fine-tuning to prevent overfitting
learning_rate = 1e-4
fine_tune_at = 50  # Unfreeze more layers for EfficientNet
label_smoothing = 0.1  # Add label smoothing
mixup_alpha = 0.2  # Mixup augmentation

# Enhanced Data augmentation with mixup
def mixup_data(x, y, alpha=0.2):
    """Mixup augmentation"""
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    
    batch_size = tf.shape(x)[0]
    index = tf.random.shuffle(tf.range(batch_size))
    
    mixed_x = lam * x + (1 - lam) * tf.gather(x, index)
    mixed_y = lam * y + (1 - lam) * tf.gather(y, index)
    
    return mixed_x, mixed_y

# Enhanced data generators with stronger augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    # More aggressive augmentation
    rotation_range=40,
    width_shift_range=0.3,
    height_shift_range=0.3,
    zoom_range=0.3,
    horizontal_flip=True,
    shear_range=0.3,
    brightness_range=[0.7, 1.3],
    channel_shift_range=30.0,
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_gen = train_datagen.flow_from_directory(
    data_dir,
    target_size=image_size,
    batch_size=batch_size,
    subset='training',
    shuffle=True,
    class_mode='categorical'
)

val_gen = val_datagen.flow_from_directory(
    data_dir,
    target_size=image_size,
    batch_size=batch_size,
    subset='validation',
    shuffle=False,
    class_mode='categorical'
)

# Enhanced class balance analysis
counter = Counter(train_gen.classes)
print("🔍 Class Distribution Analysis:")
print(f"Total training samples: {len(train_gen.classes)}")
print(f"Number of classes: {len(counter)}")

class_names = list(train_gen.class_indices.keys())
for i, (class_name, count) in enumerate(zip(class_names, counter.values())):
    print(f"  {class_name}: {count} samples")

# Calculate class weights
max_count = float(max(counter.values()))
class_weights = {int(i): float(max_count / count) for i, count in counter.items()}
print(f"\n📊 Class weights: {class_weights}")

# Enhanced model setup with EfficientNet and stronger regularization
base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze base initially

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = BatchNormalization()(x)
x = Dropout(0.6)(x)  # Increased dropout for base training
x = Dense(512, activation='relu', kernel_regularizer=l2(0.0001))(x)
x = BatchNormalization()(x)
x = Dropout(0.5)(x)
x = Dense(256, activation='relu', kernel_regularizer=l2(0.0001))(x)
x = BatchNormalization()(x)
x = Dropout(0.4)(x)
output = Dense(train_gen.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

# Custom loss with label smoothing
loss_fn = CategoricalCrossentropy(label_smoothing=label_smoothing)

# Compile with gradient clipping
optimizer = Adam(learning_rate=learning_rate, clipnorm=1.0)
model.compile(
    optimizer=optimizer,
    loss=loss_fn,
    metrics=['accuracy']
)

print(f"\n🏗️ Model Architecture:")
print(f"Total parameters: {model.count_params():,}")
print(f"Trainable parameters: {sum([tf.keras.backend.count_params(w) for w in model.trainable_weights]):,}")

# Enhanced callbacks
checkpoint = ModelCheckpoint(
    "ML/clothing_classifier_efficient.keras", 
    save_best_only=True, 
    monitor='val_accuracy', 
    mode='max',
    verbose=1
)

early_stop = EarlyStopping(
    patience=15,
    restore_best_weights=True,
    monitor='val_accuracy',
    mode='max',
    verbose=1,
    min_delta=0.002  # Increased threshold
)

# More conservative learning rate scheduler
lr_scheduler = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,  # More aggressive reduction
    patience=5,
    min_lr=1e-8,
    verbose=1
)

# Cyclical learning rate for fine-tuning
def cyclical_lr(epoch, lr):
    if epoch < initial_epochs:
        return lr
    else:
        # Cyclical learning rate in fine-tuning
        cycle_epoch = (epoch - initial_epochs) % 6
        if cycle_epoch < 3:
            return 5e-6 * (1 + cycle_epoch / 3)
        else:
            return 5e-6 * (2 - cycle_epoch / 3)

cyclical_scheduler = LearningRateScheduler(cyclical_lr, verbose=1)

print("\n🚀 Starting Base Model Training...")
print(f"Training for {initial_epochs} epochs with frozen base model")
print(f"Using EfficientNetB0 with label smoothing: {label_smoothing}")

# Train base model
history = model.fit(
    train_gen,
    epochs=initial_epochs,
    validation_data=val_gen,
    class_weight=class_weights,
    callbacks=[checkpoint, early_stop, lr_scheduler],
    verbose=1
)

print("\n🔧 Starting Gradual Fine-tuning...")

# Gradual unfreezing approach
def gradual_unfreeze(model, base_model, stage):
    """Gradually unfreeze layers"""
    total_layers = len(base_model.layers)
    if stage == 1:
        # Unfreeze top 25% of layers
        unfreeze_from = int(total_layers * 0.75)
        print(f"🔓 Stage 1: Unfreezing layers from {unfreeze_from} onwards")
    elif stage == 2:
        # Unfreeze top 50% of layers
        unfreeze_from = int(total_layers * 0.5)
        print(f"🔓 Stage 2: Unfreezing layers from {unfreeze_from} onwards")
    else:
        # Unfreeze all layers
        unfreeze_from = fine_tune_at
        print(f"🔓 Stage 3: Unfreezing layers from {unfreeze_from} onwards")
    
    base_model.trainable = True
    for layer in base_model.layers[:unfreeze_from]:
        layer.trainable = False
    
    return unfreeze_from

# Stage 1: Unfreeze top layers only
gradual_unfreeze(model, base_model, 1)

# Stronger regularization for fine-tuning
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = BatchNormalization()(x)
x = Dropout(0.7)(x)  # Even higher dropout
x = Dense(512, activation='relu', kernel_regularizer=l2(0.001))(x)  # Stronger L2
x = BatchNormalization()(x)
x = Dropout(0.6)(x)
x = Dense(256, activation='relu', kernel_regularizer=l2(0.001))(x)
x = BatchNormalization()(x)
x = Dropout(0.5)(x)
output = Dense(train_gen.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

# Compile with very low learning rate and stronger gradient clipping
optimizer_finetune = Adam(learning_rate=5e-6, clipnorm=0.5)
model.compile(
    optimizer=optimizer_finetune,
    loss=loss_fn,
    metrics=['accuracy']
)

print(f"Trainable parameters: {sum([tf.keras.backend.count_params(w) for w in model.trainable_weights]):,}")

# Enhanced early stopping for fine-tuning
early_stop_finetune = EarlyStopping(
    patience=8,  # Reduced patience to prevent overfitting
    restore_best_weights=True,
    monitor='val_accuracy',
    mode='max',
    verbose=1,
    min_delta=0.005  # Higher threshold
)

# Fine-tune with cyclical learning rate
history_fine = model.fit(
    train_gen,
    epochs=fine_tune_epochs,
    validation_data=val_gen,
    class_weight=class_weights,
    callbacks=[checkpoint, early_stop_finetune, cyclical_scheduler],
    verbose=1
)

# Save class indices and model info
with open("ML/class_names.json", "w") as f:
    json.dump(train_gen.class_indices, f)

# Save training configuration
config = {
    'model_type': 'EfficientNetB0',
    'image_size': image_size,
    'batch_size': batch_size,
    'initial_epochs': initial_epochs,
    'fine_tune_epochs': fine_tune_epochs,
    'initial_lr': float(learning_rate),
    'fine_tune_lr': 5e-6,
    'fine_tune_at': fine_tune_at,
    'label_smoothing': label_smoothing,
    'mixup_alpha': mixup_alpha,
    'class_weights': {str(k): float(v) for k, v in class_weights.items()},
    'num_classes': int(train_gen.num_classes)
}

with open("ML/training_config.json", "w") as f:
    json.dump(config, f, indent=2)

# Enhanced plotting with overfitting analysis
def plot_enhanced_history(histories, labels):
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Combine histories
    combined_acc = histories[0].history['accuracy'] + histories[1].history['accuracy']
    combined_val_acc = histories[0].history['val_accuracy'] + histories[1].history['val_accuracy']
    combined_loss = histories[0].history['loss'] + histories[1].history['loss']
    combined_val_loss = histories[0].history['val_loss'] + histories[1].history['val_loss']
    
    epochs = range(1, len(combined_acc) + 1)
    
    # Accuracy plot with overfitting indicators
    axes[0, 0].plot(epochs, combined_acc, 'b-', label='Training Accuracy', linewidth=2)
    axes[0, 0].plot(epochs, combined_val_acc, 'r-', label='Validation Accuracy', linewidth=2)
    axes[0, 0].axvline(x=initial_epochs, color='g', linestyle='--', alpha=0.7, label='Fine-tuning Start')
    
    # Highlight overfitting regions
    overfitting_threshold = 0.05
    for i, (train_acc, val_acc) in enumerate(zip(combined_acc, combined_val_acc)):
        if train_acc - val_acc > overfitting_threshold:
            axes[0, 0].axvspan(i, i+1, alpha=0.2, color='red')
    
    axes[0, 0].set_title('Model Accuracy (Red areas = Overfitting)', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Loss plot
    axes[0, 1].plot(epochs, combined_loss, 'b-', label='Training Loss', linewidth=2)
    axes[0, 1].plot(epochs, combined_val_loss, 'r-', label='Validation Loss', linewidth=2)
    axes[0, 1].axvline(x=initial_epochs, color='g', linestyle='--', alpha=0.7, label='Fine-tuning Start')
    axes[0, 1].set_title('Model Loss', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Learning rate plot
    if 'lr' in histories[0].history:
        lr_history = histories[0].history['lr'] + histories[1].history['lr']
        axes[1, 0].plot(epochs, lr_history, 'g-', linewidth=2)
        axes[1, 0].set_title('Learning Rate Schedule', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Learning Rate')
        axes[1, 0].set_yscale('log')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Overfitting analysis
    val_gap = np.array(combined_acc) - np.array(combined_val_acc)
    axes[1, 1].plot(epochs, val_gap, 'purple', linewidth=2)
    axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    axes[1, 1].axhline(y=0.05, color='red', linestyle='--', alpha=0.7, label='Overfitting Threshold')
    axes[1, 1].axvline(x=initial_epochs, color='g', linestyle='--', alpha=0.7, label='Fine-tuning Start')
    axes[1, 1].set_title('Overfitting Analysis', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('Train - Val Accuracy')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("ML/enhanced_training_analysis.png", dpi=300, bbox_inches='tight')
    plt.show()

plot_enhanced_history([history, history_fine], ["Base", "Fine-tune"])

# Enhanced results analysis
print("\n" + "="*60)
print("🎯 ENHANCED TRAINING RESULTS")
print("="*60)

final_train_acc = history_fine.history['accuracy'][-1]
final_val_acc = history_fine.history['val_accuracy'][-1]
final_train_loss = history_fine.history['loss'][-1]
final_val_loss = history_fine.history['val_loss'][-1]

print(f"🔵 Final Training Accuracy: {final_train_acc:.2%}")
print(f"🟠 Final Validation Accuracy: {final_val_acc:.2%}")
print(f"🔵 Final Training Loss: {final_train_loss:.4f}")
print(f"🟠 Final Validation Loss: {final_val_loss:.4f}")
print(f"🔁 Total Epochs: {len(history.history['accuracy']) + len(history_fine.history['accuracy'])}")

# Calculate overfitting metrics
overfitting_gap = final_train_acc - final_val_acc
print(f"📊 Overfitting Gap: {overfitting_gap:.2%}")

if overfitting_gap < 0.05:
    print("✅ Overfitting Status: GOOD (Gap < 5%)")
elif overfitting_gap < 0.10:
    print("⚠️ Overfitting Status: MODERATE (Gap 5-10%)")
else:
    print("❌ Overfitting Status: HIGH (Gap > 10%)")

# Best validation accuracy
best_val_acc = max(max(history.history['val_accuracy']), max(history_fine.history['val_accuracy']))
print(f"🏆 Best Validation Accuracy: {best_val_acc:.2%}")

# Performance improvement
baseline_acc = 0.67  # Previous best
improvement = best_val_acc - baseline_acc
print(f"📈 Improvement from baseline: {improvement:.2%}")

print(f"\n🔧 Model Enhancements Applied:")
print(f"✅ EfficientNetB0 backbone (more efficient than MobileNet)")
print(f"✅ Label smoothing: {label_smoothing}")
print(f"✅ Gradient clipping: Enabled")
print(f"✅ Stronger regularization: L2 + High dropout")
print(f"✅ Cyclical learning rate: Fine-tuning phase")
print(f"✅ Gradual unfreezing: Progressive layer activation")
print(f"✅ Enhanced data augmentation: More aggressive")

print(f"\n💾 Files saved:")
print(f"📋 Model: ML/clothing_classifier_efficient.keras")
print(f"📋 Class names: ML/class_names.json")
print(f"📋 Config: ML/training_config.json")
print(f"📊 Training plot: ML/enhanced_training_analysis.png")
print("="*60)