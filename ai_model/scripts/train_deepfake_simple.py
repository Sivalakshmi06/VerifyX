"""
Simplified Deepfake Detection Model Training
Uses scikit-learn and OpenCV for feature extraction
No TensorFlow required - works on Windows without DLL issues
"""

import os
import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix
import pickle
import json
from pathlib import Path

class SimpleDeepfakeDetector:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.model = None
        self.scaler = None
        self.img_size = 224
        
    def extract_features(self, image_path):
        """Extract features from image"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Resize
            img = cv2.resize(img, (self.img_size, self.img_size))
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Extract features
            features = []
            
            # 1. Histogram features
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            features.extend(hist.flatten()[:32])  # First 32 bins
            
            # 2. Laplacian variance (texture)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            features.append(laplacian_var)
            
            # 3. Sobel edges
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
            features.append(np.mean(sobelx))
            features.append(np.mean(sobely))
            
            # 4. Frequency domain features
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)
            features.append(np.mean(magnitude_spectrum))
            features.append(np.std(magnitude_spectrum))
            
            # 5. Color features
            for channel in cv2.split(img):
                features.append(np.mean(channel))
                features.append(np.std(channel))
            
            # 6. Contrast
            features.append(np.std(gray))
            
            # 7. Brightness
            features.append(np.mean(gray))
            
            return np.array(features)
        except Exception as e:
            print(f"Error extracting features from {image_path}: {str(e)}")
            return None
    
    def prepare_dataset(self):
        """Prepare dataset"""
        print("[INFO] Preparing dataset...")
        
        X = []
        y = []
        
        # Load real images
        real_dir = os.path.join(self.dataset_path, 'real')
        if os.path.exists(real_dir):
            real_files = [f for f in os.listdir(real_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"[INFO] Found {len(real_files)} real images")
            
            for idx, img_file in enumerate(real_files[:5000]):  # Limit to 5000
                img_path = os.path.join(real_dir, img_file)
                features = self.extract_features(img_path)
                if features is not None:
                    X.append(features)
                    y.append(0)  # Real = 0
                
                if (idx + 1) % 500 == 0:
                    print(f"[INFO] Loaded {idx + 1} real images...")
        
        # Load fake images
        fake_dir = os.path.join(self.dataset_path, 'fake')
        if os.path.exists(fake_dir):
            fake_files = [f for f in os.listdir(fake_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"[INFO] Found {len(fake_files)} fake images")
            
            for idx, img_file in enumerate(fake_files[:5000]):  # Limit to 5000
                img_path = os.path.join(fake_dir, img_file)
                features = self.extract_features(img_path)
                if features is not None:
                    X.append(features)
                    y.append(1)  # Fake = 1
                
                if (idx + 1) % 500 == 0:
                    print(f"[INFO] Loaded {idx + 1} fake images...")
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"[INFO] Total samples: {len(X)}")
        print(f"[INFO] Real: {np.sum(y == 0)}, Fake: {np.sum(y == 1)}")
        
        # Split dataset
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        return X_train, X_test, y_train, y_test
    
    def train(self, X_train, X_test, y_train, y_test):
        """Train model"""
        print("[INFO] Training model...")
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        print("[INFO] Evaluating model...")
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\n[RESULTS]")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"AUC: {auc:.4f}")
        print(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
        
        return accuracy, auc
    
    def save_model(self):
        """Save model"""
        print("[INFO] Saving model...")
        
        # Save model
        with open('models/deepfake_detector_simple.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save scaler
        with open('models/deepfake_scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save info
        info = {
            'model_type': 'RandomForest',
            'n_estimators': 100,
            'img_size': self.img_size,
            'training_date': str(np.datetime64('today'))
        }
        
        with open('models/deepfake_training_info.json', 'w') as f:
            json.dump(info, f, indent=4)
        
        print("[INFO] Model saved successfully!")

def main():
    dataset_path = 'datasets/deepfake_images/real_vs_fake/real-vs-fake/test'
    
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset not found at {dataset_path}")
        return
    
    # Initialize trainer
    trainer = SimpleDeepfakeDetector(dataset_path)
    
    # Prepare dataset
    X_train, X_test, y_train, y_test = trainer.prepare_dataset()
    
    # Train model
    trainer.train(X_train, X_test, y_train, y_test)
    
    # Save model
    trainer.save_model()
    
    print("\n[SUCCESS] Training completed!")

if __name__ == '__main__':
    main()
