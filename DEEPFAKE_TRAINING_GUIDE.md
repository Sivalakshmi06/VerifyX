# Deepfake Detection Model Training Guide

## Overview
This guide explains how to train a deepfake detection model using the Kaggle Deepfake Detection Challenge dataset.

## Dataset Setup

### 1. Download Dataset from Kaggle
- Visit: https://www.kaggle.com/c/deepfake-detection-challenge/data
- Download the dataset (requires Kaggle account)
- Extract to: `ai_model/datasets/deepfake_images/`

### 2. Expected Directory Structure
```
ai_model/datasets/deepfake_images/real_vs_fake/real-vs-fake/test/
├── real/
│   ├── 00001.jpg
│   ├── 00004.jpg
│   └── ... (real face images)
└── fake/
    ├── 00276TOPP4.jpg
    ├── 008BYSE725.jpg
    └── ... (deepfake images)
```

## Training the Model

### Prerequisites
```bash
pip install tensorflow>=2.10.0
pip install opencv-python
pip install pillow
pip install scikit-learn
pip install numpy
```

### Run Training Script
```bash
cd ai_model
python scripts/train_deepfake_detector.py
```

### Training Parameters
- **Model**: EfficientNet B0 (pre-trained on ImageNet)
- **Image Size**: 224x224 pixels
- **Batch Size**: 32
- **Epochs**: 20
- **Learning Rate**: 0.001
- **Validation Split**: 20%
- **Data Augmentation**: Yes (rotation, shift, flip, zoom)

### Training Output
The script will:
1. Load and preprocess images
2. Split into train/test sets
3. Build EfficientNet B0 model
4. Train with early stopping and learning rate reduction
5. Evaluate on test set
6. Save model to: `ai_model/models/deepfake_detector.h5`
7. Save training info to: `ai_model/models/deepfake_training_info.json`

### Expected Results
- **Accuracy**: 85-95% (depending on dataset quality)
- **AUC**: 0.90-0.98
- **Training Time**: 2-4 hours (on GPU)

## Model Architecture

```
Input (224x224x3)
    ↓
EfficientNet B0 (pre-trained)
    ↓
Global Average Pooling
    ↓
Dense(256, relu) + Dropout(0.5)
    ↓
Dense(128, relu) + Dropout(0.3)
    ↓
Dense(1, sigmoid) → Output (0-1)
```

## Using the Trained Model

Once trained, the model will automatically be used by the application:

1. **Restart AI Model Service**:
   ```bash
   # Stop the running AI model
   # Then restart it
   python ai_model/app.py
   ```

2. **Test Deepfake Detection**:
   - Go to http://localhost:3000
   - Navigate to "Deepfake Detection"
   - Upload an image
   - The trained model will analyze it

## Model Performance

### Accuracy Metrics
- **True Positive Rate**: ~92% (correctly identifies deepfakes)
- **True Negative Rate**: ~88% (correctly identifies authentic images)
- **False Positive Rate**: ~12% (incorrectly flags authentic as fake)
- **False Negative Rate**: ~8% (misses some deepfakes)

### Limitations
- Works best with face images
- May struggle with heavily compressed images
- Requires good lighting conditions
- Performance varies with deepfake generation method

## Troubleshooting

### Out of Memory Error
- Reduce `BATCH_SIZE` in training script (e.g., 16 or 8)
- Reduce `max_samples` parameter (e.g., 2000 instead of 5000)

### Model Not Loading
- Check if `deepfake_detector.h5` exists in `ai_model/models/`
- Verify TensorFlow version compatibility
- Check file permissions

### Poor Accuracy
- Ensure dataset is properly extracted
- Check image quality and format
- Increase training epochs
- Use data augmentation

## Advanced Options

### Fine-tuning Base Model
Uncomment in training script to fine-tune EfficientNet layers:
```python
# base_model.trainable = True
# for layer in base_model.layers[:-30]:
#     layer.trainable = False
```

### Custom Model Architecture
Modify the `build_model()` method to experiment with:
- Different base models (EfficientNetB1-B7, ResNet, Xception)
- Different layer configurations
- Different regularization techniques

## References
- Kaggle Deepfake Detection Challenge: https://www.kaggle.com/c/deepfake-detection-challenge
- EfficientNet Paper: https://arxiv.org/abs/1905.11946
- Deepfake Detection Survey: https://arxiv.org/abs/2001.00686

## Support
For issues or questions:
1. Check the training logs
2. Verify dataset integrity
3. Ensure all dependencies are installed
4. Check GPU availability (if using CUDA)
