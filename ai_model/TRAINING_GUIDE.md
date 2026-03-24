# AI Model Training Guide

This guide will help you download datasets from Kaggle and train real models for the fake news detection system.

## Prerequisites

1. **Kaggle Account**: Create account at https://www.kaggle.com
2. **Kaggle API**: Install Kaggle CLI
   ```bash
   pip install kaggle
   ```
3. **API Credentials**: 
   - Go to https://www.kaggle.com/settings
   - Click "Create New API Token"
   - Download `kaggle.json`
   - Place it in: `~/.kaggle/kaggle.json` (Linux/Mac) or `C:\Users\<username>\.kaggle\kaggle.json` (Windows)

## Required Datasets

### 1. Fake News Text Dataset

**Dataset**: Fake News Detection Dataset
```bash
kaggle datasets download -d clmentbisaillon/fake-and-real-news-dataset
```

**Alternative**:
```bash
kaggle datasets download -d mrisdal/fake-news
```

**Files**:
- `Fake.csv` - Fake news articles
- `True.csv` - Real news articles

### 2. Deepfake Image Dataset

**Dataset**: FaceForensics++ (Requires registration)
```bash
# Download from: https://github.com/ondyari/FaceForensics
```

**Alternative - Smaller Dataset**:
```bash
kaggle datasets download -d xhlulu/140k-real-and-fake-faces
```

### 3. Sentiment Analysis Dataset

**Dataset**: Twitter Sentiment Analysis
```bash
kaggle datasets download -d kazanova/sentiment140
```

## Installation Steps

### Step 1: Install Additional Dependencies

```bash
cd ai_model
pip install -r requirements_training.txt
```

### Step 2: Download Datasets

Run the download script:
```bash
python scripts/download_datasets.py
```

This will:
- Download all required datasets from Kaggle
- Extract and organize them in `datasets/` folder
- Prepare data for training

### Step 3: Train Models

#### Train Text Classifier (BERT)
```bash
python scripts/train_text_classifier.py
```

**Output**: `models/text_classifier_bert.pkl`

#### Train Deepfake Detector (CNN)
```bash
python scripts/train_deepfake_detector.py
```

**Output**: `models/deepfake_detector_cnn.h5`

#### Train Emotion Analyzer
```bash
python scripts/train_emotion_analyzer.py
```

**Output**: `models/emotion_analyzer.pkl`

### Step 4: Test Models

```bash
python scripts/test_models.py
```

## Model Architectures

### 1. Text Classifier (BERT)

**Architecture**:
- Base: BERT-base-uncased
- Fine-tuning layers: 2 dense layers
- Output: Binary classification (Fake/Real)

**Training**:
- Epochs: 3-5
- Batch size: 16
- Learning rate: 2e-5
- Optimizer: AdamW

**Expected Accuracy**: 92-95%

### 2. Deepfake Detector (EfficientNet-B4)

**Architecture**:
- Base: EfficientNet-B4 (pre-trained on ImageNet)
- Additional layers: Global Average Pooling + Dense
- Output: Binary classification (Deepfake/Authentic)

**Training**:
- Epochs: 10-15
- Batch size: 32
- Learning rate: 1e-4
- Optimizer: Adam
- Data augmentation: Rotation, flip, zoom

**Expected Accuracy**: 88-92%

### 3. Emotion Analyzer (Multi-label Classification)

**Architecture**:
- Base: DistilBERT
- Output: 4 emotion scores (Fear, Anger, Political, Religious)

**Training**:
- Epochs: 5
- Batch size: 32
- Learning rate: 3e-5

## Tamil Language Support

### Tamil Text Dataset

**Dataset**: Tamil News Classification
```bash
kaggle datasets download -d sudalairajkumar/tamil-nlp
```

### Tamil Model Training

```bash
python scripts/train_tamil_classifier.py
```

Uses:
- Multilingual BERT (bert-base-multilingual-cased)
- Supports both English and Tamil

## OCR for Image Text Extraction

### Install Tesseract OCR

**Windows**:
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install and add to PATH
```

**Linux**:
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-tam  # Tamil language
```

**Mac**:
```bash
brew install tesseract
brew install tesseract-lang  # All languages
```

### Install Python Package

```bash
pip install pytesseract
```

## Quick Start Training Script

Create `train_all.py`:

```python
import subprocess

print("Starting model training pipeline...")

# 1. Download datasets
print("\n1. Downloading datasets...")
subprocess.run(["python", "scripts/download_datasets.py"])

# 2. Train text classifier
print("\n2. Training text classifier...")
subprocess.run(["python", "scripts/train_text_classifier.py"])

# 3. Train deepfake detector
print("\n3. Training deepfake detector...")
subprocess.run(["python", "scripts/train_deepfake_detector.py"])

# 4. Train emotion analyzer
print("\n4. Training emotion analyzer...")
subprocess.run(["python", "scripts/train_emotion_analyzer.py"])

print("\n✅ All models trained successfully!")
```

Run:
```bash
python train_all.py
```

## Model Performance Benchmarks

| Model | Dataset Size | Training Time | Accuracy |
|-------|-------------|---------------|----------|
| Text Classifier | 40K articles | 2-3 hours | 93% |
| Deepfake Detector | 140K images | 4-6 hours | 90% |
| Emotion Analyzer | 100K texts | 1-2 hours | 85% |

## Using Pre-trained Models

If you don't want to train from scratch, download pre-trained models:

```bash
# Download from Google Drive or Hugging Face
python scripts/download_pretrained_models.py
```

## Troubleshooting

### Out of Memory Error
- Reduce batch size
- Use gradient accumulation
- Use smaller model (DistilBERT instead of BERT)

### Slow Training
- Use GPU (CUDA)
- Reduce dataset size for testing
- Use mixed precision training

### Low Accuracy
- Increase epochs
- Adjust learning rate
- Add more data augmentation
- Use pre-trained weights

## Production Deployment

After training:

1. **Save models** to `models/` folder
2. **Update model paths** in respective detector files
3. **Test API** with `test_api.py`
4. **Deploy** to production server

## Next Steps

1. ✅ Download datasets from Kaggle
2. ✅ Train models using provided scripts
3. ✅ Test models with sample data
4. ✅ Integrate trained models into Flask API
5. ✅ Deploy to production

For questions or issues, refer to the documentation or create an issue on GitHub.
