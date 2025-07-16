# DeepFashion Dataset Organization and Training Pipeline
import os
import pandas as pd
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import json
import shutil
from pathlib import Path
import os

os.makedirs("AI")

class DeepFashionDataset:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.images_path = self.base_path / "images" / "img"
        self.anno_path = self.base_path / "Anno_coarse"
        self.anno_fine_path = self.base_path / "Anno_fine"
        self.eval_path = self.base_path / "Eval"
        
        # Load category mappings
        self.category_cloth_df = self._load_category_cloth()
        self.category_img_df = self._load_category_img()
        
        # Create organized directory structure
        self.organized_path = self.base_path / "organized_dataset"
        
    def _load_category_cloth(self):
        """Load category cloth mapping"""
        file_path = self.anno_path / "list_category_cloth.txt"
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Skip first line (number of categories) and second line (headers)
        data = []
        for line in lines[2:]:
            parts = line.strip().split()
            category_name = parts[0]
            category_type = int(parts[1])
            data.append([category_name, category_type])
            
        return pd.DataFrame(data, columns=['category_name', 'category_type'])
    
    def _load_category_img(self):
        """Load image category mapping"""
        file_path = self.anno_path / "list_category_img.txt"
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Skip first line (number of images) and second line (headers)
        data = []
        for line in lines[2:]:
            parts = line.strip().split()
            image_name = parts[0]
            category_label = int(parts[1])
            data.append([image_name, category_label])
            
        return pd.DataFrame(data, columns=['image_name', 'category_label'])
    
    def analyze_dataset(self):
        """Analyze dataset distribution"""
        print("=== Dataset Analysis ===")
        print(f"Total images: {len(self.category_img_df)}")
        print(f"Total categories: {len(self.category_cloth_df)}")
        
        # Category distribution
        category_counts = self.category_img_df['category_label'].value_counts().sort_index()
        
        # Map category labels to names
        category_mapping = dict(zip(range(1, len(self.category_cloth_df) + 1), 
                                  self.category_cloth_df['category_name']))
        
        print("\n=== Category Distribution ===")
        for cat_id, count in category_counts.items():
            cat_name = category_mapping.get(cat_id, f"Unknown_{cat_id}")
            print(f"{cat_name}: {count} images")
        
        # Category type distribution
        type_distribution = self.category_cloth_df['category_type'].value_counts()
        print("\n=== Category Type Distribution ===")
        type_names = {1: "Upper-body", 2: "Lower-body", 3: "Full-body"}
        for type_id, count in type_distribution.items():
            print(f"{type_names[type_id]}: {count} categories")
        
        return category_counts, category_mapping
    
    def organize_dataset(self):
        """Organize dataset into train/val/test splits"""
        print("=== Organizing Dataset ===")
        
        # Create organized directory structure
        splits = ['train', 'val', 'test']
        for split in splits:
            split_path = self.organized_path / split
            split_path.mkdir(parents=True, exist_ok=True)
            
            # Create category directories
            for _, row in self.category_cloth_df.iterrows():
                category_dir = split_path / row['category_name']
                category_dir.mkdir(exist_ok=True)
        
        # Load evaluation partition if available
        eval_partition_file = self.eval_path / "list_eval_partition.txt"
        if eval_partition_file.exists():
            eval_df = self._load_eval_partition()
            return self._organize_with_splits(eval_df)
        else:
            return self._organize_with_random_splits()
    
    def _load_eval_partition(self):
        """Load evaluation partition file"""
        file_path = self.eval_path / "list_eval_partition.txt"
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        data = []
        for line in lines[2:]:  # Skip header lines
            parts = line.strip().split()
            image_name = parts[0]
            split = parts[1]
            data.append([image_name, split])
            
        return pd.DataFrame(data, columns=['image_name', 'split'])
    
    def _organize_with_splits(self, eval_df):
        """Organize dataset using provided splits"""
        # Merge with category information
        merged_df = pd.merge(self.category_img_df, eval_df, on='image_name', how='inner')
        
        # Create category mapping
        category_mapping = dict(zip(range(1, len(self.category_cloth_df) + 1), 
                                  self.category_cloth_df['category_name']))
        
        organized_count = 0
        for _, row in merged_df.iterrows():
            src_path = self.images_path / row['image_name']
            
            if src_path.exists():
                category_name = category_mapping[row['category_label']]
                dest_path = self.organized_path / row['split'] / category_name / src_path.name
                
                # Copy file to organized structure
                shutil.copy2(src_path, dest_path)
                organized_count += 1
        
        print(f"Organized {organized_count} images into train/val/test splits")
        return merged_df
    
    def _organize_with_random_splits(self):
        """Organize dataset with random splits (80/10/10)"""
        category_mapping = dict(zip(range(1, len(self.category_cloth_df) + 1), 
                                  self.category_cloth_df['category_name']))
        
        organized_count = 0
        split_data = []
        
        # Process each category separately to ensure balanced splits
        for cat_id, cat_name in category_mapping.items():
            cat_images = self.category_img_df[self.category_img_df['category_label'] == cat_id]
            
            # Create random splits
            train_imgs, temp_imgs = train_test_split(cat_images, test_size=0.2, random_state=42)
            val_imgs, test_imgs = train_test_split(temp_imgs, test_size=0.5, random_state=42)
            
            # Assign splits
            for _, row in train_imgs.iterrows():
                split_data.append([row['image_name'], row['category_label'], 'train'])
            for _, row in val_imgs.iterrows():
                split_data.append([row['image_name'], row['category_label'], 'val'])
            for _, row in test_imgs.iterrows():
                split_data.append([row['image_name'], row['category_label'], 'test'])
            
            # Copy files
            for split_name, imgs in [('train', train_imgs), ('val', val_imgs), ('test', test_imgs)]:
                for _, row in imgs.iterrows():
                    src_path = self.images_path / row['image_name']
                    if src_path.exists():
                        dest_path = self.organized_path / split_name / cat_name / src_path.name
                        shutil.copy2(src_path, dest_path)
                        organized_count += 1
        
        print(f"Organized {organized_count} images into random train/val/test splits")
        
        # Create DataFrame for tracking
        split_df = pd.DataFrame(split_data, columns=['image_name', 'category_label', 'split'])
        return split_df

class FashionClassifier:
    def __init__(self, num_classes, input_shape=(224, 224, 3)):
        self.num_classes = num_classes
        self.input_shape = input_shape
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build ResNet50-based model"""
        # Load pre-trained ResNet50
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=self.input_shape)
        
        # Freeze base model layers initially
        base_model.trainable = False
        
        # Add custom classification head
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(1024, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(self.num_classes, activation='softmax')(x)
        
        self.model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compile model
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_3_accuracy']
        )
        
        print("Model built successfully!")
        return self.model
    
    def create_data_generators(self, organized_path, batch_size=32):
        """Create data generators for training"""
        from tensorflow.keras.preprocessing.image import ImageDataGenerator
        
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            fill_mode='nearest'
        )
        
        # Only rescaling for validation and test
        val_test_datagen = ImageDataGenerator(rescale=1./255)
        
        # Create generators
        train_generator = train_datagen.flow_from_directory(
            organized_path / 'train',
            target_size=self.input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical'
        )
        
        val_generator = val_test_datagen.flow_from_directory(
            organized_path / 'val',
            target_size=self.input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical'
        )
        
        test_generator = val_test_datagen.flow_from_directory(
            organized_path / 'test',
            target_size=self.input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        return train_generator, val_generator, test_generator
    
    def train_model(self, train_generator, val_generator, epochs=50):
        """Train the model"""
        # Callbacks
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7),
            ModelCheckpoint('best_fashion_model.h5', monitor='val_accuracy', 
                          save_best_only=True, mode='max')
        ]
        
        # Train model
        self.history = self.model.fit(
            train_generator,
            epochs=epochs,
            validation_data=val_generator,
            callbacks=callbacks
        )
        
        # Fine-tuning: unfreeze some layers
        print("Starting fine-tuning...")
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Freeze early layers, unfreeze later layers
        for layer in base_model.layers[:-20]:
            layer.trainable = False
        
        # Recompile with lower learning rate
        self.model.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_3_accuracy']
        )
        
        # Continue training
        fine_tune_history = self.model.fit(
            train_generator,
            epochs=epochs//2,
            validation_data=val_generator,
            callbacks=callbacks
        )
        
        # Combine histories
        for key in self.history.history.keys():
            self.history.history[key].extend(fine_tune_history.history[key])
        
        return self.history
    
    def evaluate_model(self, test_generator):
        """Evaluate model on test set"""
        # Evaluate
        test_loss, test_accuracy, test_top3_accuracy = self.model.evaluate(test_generator)
        
        print(f"Test Loss: {test_loss:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")
        print(f"Test Top-3 Accuracy: {test_top3_accuracy:.4f}")
        
        # Predictions for detailed analysis
        predictions = self.model.predict(test_generator)
        predicted_classes = np.argmax(predictions, axis=1)
        
        # Get class labels
        class_labels = list(test_generator.class_indices.keys())
        
        # Classification report
        report = classification_report(test_generator.classes, predicted_classes, 
                                     target_names=class_labels)
        print("\nClassification Report:")
        print(report)
        
        return test_loss, test_accuracy, test_top3_accuracy, predictions
    
    def plot_training_history(self):
        """Plot training history"""
        if self.history is None:
            print("No training history available")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy
        axes[0, 0].plot(self.history.history['accuracy'], label='Train Accuracy')
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Val Accuracy')
        axes[0, 0].set_title('Model Accuracy')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        
        # Loss
        axes[0, 1].plot(self.history.history['loss'], label='Train Loss')
        axes[0, 1].plot(self.history.history['val_loss'], label='Val Loss')
        axes[0, 1].set_title('Model Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        
        # Top-3 Accuracy
        axes[1, 0].plot(self.history.history['top_3_accuracy'], label='Train Top-3 Accuracy')
        axes[1, 0].plot(self.history.history['val_top_3_accuracy'], label='Val Top-3 Accuracy')
        axes[1, 0].set_title('Model Top-3 Accuracy')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Top-3 Accuracy')
        axes[1, 0].legend()
        
        # Learning rate (if available)
        if 'lr' in self.history.history:
            axes[1, 1].plot(self.history.history['lr'])
            axes[1, 1].set_title('Learning Rate')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Learning Rate')
        
        plt.tight_layout()
        plt.show()

def main():
    """Main training pipeline"""
    # Initialize dataset
    dataset = DeepFashionDataset("AI")  # Adjust path as needed
    
    # Analyze dataset
    category_counts, category_mapping = dataset.analyze_dataset()
    
    # Organize dataset
    split_df = dataset.organize_dataset()
    
    # Initialize classifier
    num_classes = len(dataset.category_cloth_df)
    classifier = FashionClassifier(num_classes)
    
    # Build model
    model = classifier.build_model()
    print(f"Model summary:")
    model.summary()
    
    # Create data generators
    train_gen, val_gen, test_gen = classifier.create_data_generators(
        dataset.organized_path, batch_size=32
    )
    
    # Train model
    print("Starting training...")
    history = classifier.train_model(train_gen, val_gen, epochs=50)
    
    # Evaluate model
    print("Evaluating model...")
    test_results = classifier.evaluate_model(test_gen)
    
    # Plot training history
    classifier.plot_training_history()
    
    # Save model
    if classifier.model:
        classifier.model.save('fashion_classifier_final.keras')
        print("Model saved successfully!")

if __name__ == "__main__":
    main()