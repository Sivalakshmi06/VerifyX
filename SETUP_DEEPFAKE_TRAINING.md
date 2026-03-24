# Deepfake Model Training - Step by Step

## Prerequisites Check

Before training, you need:
- ✅ Python 3.8+
- ✅ 8GB+ RAM (16GB recommended)
- ✅ GPU (optional but recommended for faster training)
- ✅ Kaggle account and API key

## Step 1: Setup Kaggle API (One-time)

### 1.1 Create Kaggle Account
- Go to: https://www.kaggle.com/settings/account
- Click "Create New API Token"
- This downloads `kaggle.json`

### 1.2 Place API Key
```bash
# Windows
mkdir %USERPROFILE%\.kaggle
copy kaggle.json %USERPROFILE%\.kaggle\

# Mac/Linux
mkdir ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 1.3 Install Kaggle CLI
```bash
pip install kaggle
```

## Step 2: Download Dataset

### Option A: Using Kaggle CLI (Recommended)
```bash
# Navigate to project root
cd D:\ISTI Project1

# Create dataset directory
mkdir -p ai_model/datasets/deepfake_images

# Download dataset
kaggle competitions download -c deepfake-detection-challenge -p ai_model/datasets/deepfake_images/

# Extract (this will take a while)
cd ai_model/datasets/deepfake_images
unzip -q "*.zip"
```

### Option B: Manual Download
1. Go to: https://www.kaggle.com/c/deepfake-detection-challenge/data
2. Click "Download All"
3. Extract to: `ai_model/datasets/deepfake_images/`

## Step 3: Verify Dataset Structure

After extraction, verify the structure:
```
ai_model/datasets/deepfake_images/
├── real_vs_fake/
│   └── real-vs-fake/
│       └── test/
│           ├── real/
│           │   ├── 00001.jpg
│           │   ├── 00004.jpg
│           │   └── ... (8000+ images)
│           └── fake/
│               ├── 00276TOPP4.jpg
│               ├── 008BYSE725.jpg
│               └── ... (10000+ images)
```

## Step 4: Install Dependencies

```bash
# Install TensorFlow
pip install tensorflow>=2.10.0

# Install other required packages
pip install opencv-python pillow scikit-learn numpy

# Verify installation
python -c "import tensorflow as tf; print(f'TensorFlow version: {tf.__version__}')"
```

## Step 5: Run Training

```bash
# Navigate to project root
cd D:\ISTI Project1

# Run training script
python ai_model/scripts/train_deepfake_detector.py
```

### Expected Output:
```
[INFO] Preparing dataset...
[INFO] Found 18000 images
[INFO] Real images: 8000, Fake images: 10000
[INFO] Loading images...
Loaded 100 images...
Loaded 200 images...
...
[INFO] Building model...
[INFO] Starting training...
Epoch 1/20
...
[RESULTS]
Test Loss: 0.1234
Test Accuracy: 0.9234
Test AUC: 0.9567
[INFO] Model saved to ai_model/models/deepfake_detector.h5
```

## Step 6: Restart AI Model Service

After training completes:

```bash
# The AI model will automatically detect and load the trained model
# Just restart it:
python ai_model/app.py
```

## Troubleshooting

### Kaggle API Issues
```bash
# Test Kaggle setup
kaggle competitions list

# If error, check:
# 1. kaggle.json exists in ~/.kaggle/
# 2. File permissions are correct (chmod 600)
# 3. API key is valid
```

### Download Issues
- **Slow download**: Normal, dataset is ~50GB
- **Connection timeout**: Resume with: `kaggle competitions download -c deepfake-detection-challenge -p ai_model/datasets/deepfake_images/ --resume`
- **Disk space**: Ensure 100GB free space

### Training Issues
- **Out of memory**: Reduce `BATCH_SIZE` in training script (32 → 16 or 8)
- **GPU not detected**: Install CUDA and cuDNN
- **TensorFlow errors**: Reinstall: `pip install --upgrade tensorflow`

## Training Time Estimates

| Hardware | Time |
|----------|------|
| GPU (RTX 3080) | 2-3 hours |
| GPU (RTX 2080) | 4-6 hours |
| GPU (GTX 1080) | 6-8 hours |
| CPU (i7) | 12-24 hours |

## After Training

1. ✅ Model saved to: `ai_model/models/deepfake_detector.h5`
2. ✅ Training info saved to: `ai_model/models/deepfake_training_info.json`
3. ✅ Restart AI model service
4. ✅ Test at: http://localhost:3000/deepfake-detection

## Quick Commands Reference

```bash
# Full process
cd D:\ISTI Project1
mkdir -p ai_model/datasets/deepfake_images
kaggle competitions download -c deepfake-detection-challenge -p ai_model/datasets/deepfake_images/
cd ai_model/datasets/deepfake_images && unzip -q "*.zip"
cd D:\ISTI Project1
pip install tensorflow opencv-python pillow scikit-learn
python ai_model/scripts/train_deepfake_detector.py
```

## Support

For detailed information, see:
- `DEEPFAKE_TRAINING_GUIDE.md` - Complete guide
- `DEEPFAKE_MODEL_SETUP.md` - Setup overview
