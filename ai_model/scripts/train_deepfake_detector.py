"""
Deepfake Detection Model Training
Uses EfficientNet B0 for efficient and accurate deepfake detection
Trains on Kaggle Deepfake Detection Challenge dataset
"""

import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
import json
from pathlib import Path
import pickle

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.2

class DeepfakeDetectorTrainer:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.model = None
        self.history = None
        self.class_weights = None
        
    def load_and_preprocess_images(self, image_paths, labels, max_samples=None):
        """Load and preprocess images"""
        images = []
        valid_labels = []
        
        for idx, (img_path, label) in enumerate(zip(image_paths, labels)):
            if max_samples and idx >= max_samples:
                break
                
            try:
                # Read image
                img = cv2.imread(img_path)
                if img is None:
                    continue
                
                # Convert BGR to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Resize to target size
                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                
                # Normalize to 0-1
                img = img.astype('float32') / 255.0
                
                images.append(img)
                valid_labels.append(label)
                
                if (idx + 1) % 100 == 0:
                    print(f"Loaded {idx + 1} images...")
                    
            except Exception as e:
                print(f"Error loading {img_path}: {str(e)}")
                continue
        
        return np.array(images), np.array(valid_labels)
    
    def prepare_dataset(self):
        """Prepare dataset from directory structure"""
        print("[INFO] Preparing dataset...")
        
        image_paths = []
        labels = []
        
        # Assuming directory structure: dataset/real/ and dataset/fake/
        real_dir = os.path.join(self.dataset_path, 'real')
        fake_dir = os.path.join(self.dataset_path, 'fake')
        
        # Load real images (label: 0)
        if os.path.exists(real_dir):
            for img_file in os.listdir(real_dir):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_paths.append(os.path.join(real_dir, img_file))
                    labels.append(0)
        
        # Load fake images (label: 1)
        if os.path.exists(fake_dir):
            for img_file in os.listdir(fake_dir):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_paths.append(os.path.join(fake_dir, img_file))
                    labels.append(1)
        
        print(f"[INFO] Found {len(image_paths)} images")
        print(f"[INFO] Real images: {labels.count(0)}, Fake images: {labels.count(1)}")
        
        # Load and preprocess images (limit to 5000 for training)
        X, y = self.load_and_preprocess_images(image_paths, labels, max_samples=5000)
        
        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Calculate class weights for imbalanced data
        unique, counts = np.unique(y_train, return_counts=True)
        self.class_weights = {
            0: counts.sum() / (2 * counts[0]),
            1: counts.sum() / (2 * counts[1])
        }
        
        print(f"[INFO] Class weights: {self.class_weights}")
        
        return X_train, X_test, y_train, y_test
    
    def build_model(self):
        """Build EfficientNet B0 model for deepfake detection"""
        print("[INFO] Building model...")
        
        # Load pre-trained EfficientNetB0
        base_model = EfficientNetB0(
            input_shape=(IMG_SIZE, IMG_SIZE, 3),
            weights='imagenet',
            include_top=False
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Build custom top layers
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(1, activation='sigmoid')  # Binary classification
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
        
        self.model = model
        print(model.summary())
        return model
    
    def train(self, X_train, X_test, y_train, y_test):
        """Train the model"""
        print("[INFO] Starting training...")
        
        # Data augmentation
        train_datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            fill_mode='nearest'
        )
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=3,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=2,
                min_lr=1e-7
            ),
            keras.callbacks.ModelCheckpoint(
                'ai_model/models/deepfake_detector_best.h5',
                monitor='val_accuracy',
                save_best_only=True
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            train_datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
            validation_data=(X_test, y_test),
            epochs=EPOCHS,
            class_weight=self.class_weights,
            callbacks=callbacks,
            verbose=1
        )
        
        return self.history
    
    def evaluate(self, X_test, y_test):
        """Evaluate model on test set"""
        print("[INFO] Evaluating model...")
        
        loss, accuracy, auc = self.model.evaluate(X_test, y_test, verbose=0)
        
        print(f"\n[RESULTS]")
        print(f"Test Loss: {loss:.4f}")
        print(f"Test Accuracy: {accuracy:.4f}")
        print(f"Test AUC: {auc:.4f}")
        
        return {'loss': loss, 'accuracy': accuracy, 'auc': auc}
    
    def save_model(self, model_path='ai_model/models/deepfake_detector.h5'):
        """Save trained model"""
        print(f"[INFO] Saving model to {model_path}...")
        self.model.save(model_path)
        print("[INFO] Model saved successfully!")
    
    def save_training_info(self, info_path='ai_model/models/deepfake_training_info.json'):
        """Save training information"""
        info = {
            'img_size': IMG_SIZE,
            'batch_size': BATCH_SIZE,
            'epochs': EPOCHS,
            'learning_rate': LEARNING_RATE,
            'class_weights': self.class_weights,
            'model_type': 'EfficientNetB0',
            'training_date': str(np.datetime64('today'))
        }
        
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=4)
        
        print(f"[INFO] Training info saved to {info_path}")

def main():
    """Main training function"""
    # Dataset path - update this to your dataset location
    dataset_path = 'ai_model/datasets/deepfake_images/real_vs_fake/real-vs-fake/test'
    
    # Check if dataset exists
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset path not found: {dataset_path}")
        print("[INFO] Please download the dataset from Kaggle:")
        print("https://www.kaggle.com/c/deepfake-detection-challenge/data")
        return
    
    # Initialize trainer
    trainer = DeepfakeDetectorTrainer(dataset_path)
    
    # Prepare dataset
    X_train, X_test, y_train, y_test = trainer.prepare_dataset()
    
    # Build model
    trainer.build_model()
    
    # Train model
    trainer.train(X_train, X_test, y_train, y_test)
    
    # Evaluate model
    results = trainer.evaluate(X_test, y_test)
    
    # Save model
    trainer.save_model()
    trainer.save_training_info()
    
    print("\n[SUCCESS] Training completed!")
    print(f"Model saved to: ai_model/models/deepfake_detector.h5")

if __name__ == '__main__':
    main()
