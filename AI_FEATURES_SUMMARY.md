# AI Features Summary

## ✅ Implemented Features

### 1. Fake News Text Detection
- **Input**: Text (English + Tamil)
- **Model**: BERT-based multilingual classifier
- **Output**: Fake/Real prediction with confidence score
- **Features**:
  - Suspicious word highlighting
  - Language detection
  - Confidence scoring
  - Support for both English and Tamil

### 2. Fake News from Images (OCR + Classification)
- **Input**: Image with text
- **Process**: 
  1. Extract text using Tesseract OCR
  2. Classify extracted text as fake/real
- **Languages**: English + Tamil
- **Output**:
  - Extracted text
  - OCR confidence
  - Fake/Real classification
  - Word count

### 3. Deepfake Image Detection
- **Input**: Image file
- **Model**: CNN-based (EfficientNet-B4)
- **Output**: Deepfake/Authentic prediction
- **Features**:
  - Confidence score
  - Attention heatmap visualization
  - Face detection

### 4. Deepfake Video Detection
- **Input**: Video file (MP4, AVI, MOV)
- **Model**: Frame-based CNN analysis
- **Output**: Deepfake/Authentic prediction
- **Features**:
  - Multi-frame analysis
  - Confidence scoring

### 5. Emotional Manipulation Analysis
- **Input**: Text
- **Output**: Emotion scores for:
  - 😨 Fear (threat language)
  - 😠 Anger (hostile content)
  - 🏛️ Political Bias (political keywords)
  - 🕉️ Religious Triggers (religious content)
- **Features**:
  - Manipulation score (0-100%)
  - Dominant emotion detection
  - Visual emotion breakdown

## 📊 Model Training

### Datasets from Kaggle

1. **Fake News Text**
   - Dataset: Fake and Real News Dataset
   - Size: 44,898 articles
   - Download: `kaggle datasets download -d clmentbisaillon/fake-and-real-news-dataset`

2. **Deepfake Images**
   - Dataset: 140k Real and Fake Faces
   - Size: 140,000 images
   - Download: `kaggle datasets download -d xhlulu/140k-real-and-fake-faces`

3. **Sentiment Analysis**
   - Dataset: Sentiment140
   - Size: 1.6M tweets
   - Download: `kaggle datasets download -d kazanova/sentiment140`

4. **Tamil Language**
   - Dataset: Tamil NLP
   - Download: `kaggle datasets download -d sudalairajkumar/tamil-nlp`

### Training Scripts

Located in `ai_model/scripts/`:

1. `download_datasets.py` - Download all datasets from Kaggle
2. `train_text_classifier.py` - Train BERT text classifier
3. `train_deepfake_detector.py` - Train CNN deepfake detector
4. `train_emotion_analyzer.py` - Train emotion analyzer

### Quick Training

```bash
# 1. Setup Kaggle API
pip install kaggle
# Place kaggle.json in ~/.kaggle/

# 2. Download datasets
cd ai_model
python scripts/download_datasets.py

# 3. Install training dependencies
pip install -r requirements_training.txt

# 4. Train all models
python scripts/train_text_classifier.py
python scripts/train_deepfake_detector.py
python scripts/train_emotion_analyzer.py
```

## 🔧 Technical Stack

### Frontend
- React.js 18
- Axios for API calls
- Modern UI with dark blue & orange theme

### Backend
- Node.js + Express
- MongoDB for data storage
- JWT authentication
- Multer for file uploads (50MB limit)

### AI/ML
- **Framework**: Python Flask
- **Text Analysis**: 
  - BERT (bert-base-multilingual-cased)
  - Logistic Regression (fallback)
  - NLTK, TextBlob
- **Image Analysis**:
  - EfficientNet-B4 (CNN)
  - OpenCV for preprocessing
  - Tesseract OCR for text extraction
- **Languages**: English + Tamil

## 📁 Project Structure

```
├── client/                    # React Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── TextDetection.js
│   │   │   ├── EmotionAnalysis.js
│   │   │   └── ImageDetection.js (Image + Video)
│   │   └── components/
│   └── package.json
│
├── server/                    # Node.js Backend
│   ├── routes/
│   │   ├── auth.js
│   │   └── detect.js
│   ├── models/
│   │   ├── User.js
│   │   └── Analysis.js
│   └── server.js
│
├── ai_model/                  # Python AI API
│   ├── models/
│   │   ├── text_classifier.py
│   │   ├── image_detector.py
│   │   ├── emotion_analyzer.py
│   │   └── ocr_extractor.py
│   ├── scripts/
│   │   ├── download_datasets.py
│   │   ├── train_text_classifier.py
│   │   ├── train_deepfake_detector.py
│   │   └── train_emotion_analyzer.py
│   ├── app.py
│   └── requirements.txt
│
└── Documentation/
    ├── TRAINING_GUIDE.md
    ├── KAGGLE_DATASETS.md
    └── AI_FEATURES_SUMMARY.md
```

## 🚀 API Endpoints

### Text Analysis
```
POST /api/analyze/text
Body: { text, language }
Response: { prediction, confidence, suspicious_words, detected_language }
```

### Image Text Analysis (OCR)
```
POST /api/analyze/image-text
Body: FormData with image file
Response: { extracted_text, ocr_confidence, classification }
```

### Image/Video Deepfake Detection
```
POST /api/analyze/image
Body: FormData with image/video file
Response: { prediction, confidence, is_deepfake, heatmap_url }
```

### Emotion Analysis
```
POST /api/analyze/emotion
Body: { text }
Response: { emotions, manipulation_score, dominant_emotion }
```

## 🎯 Model Performance (Expected)

| Model | Accuracy | Training Time | Dataset Size |
|-------|----------|---------------|--------------|
| Text Classifier (BERT) | 93-95% | 2-3 hours | 44K articles |
| Deepfake Detector (CNN) | 88-92% | 4-6 hours | 140K images |
| Emotion Analyzer | 85-88% | 1-2 hours | 100K texts |
| OCR Extraction | 85-90% | N/A | Pre-trained |

## 📦 Installation

### 1. Install Tesseract OCR

**Windows:**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH
- Install Tamil language: Download `tam.traineddata`

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-tam
```

**Mac:**
```bash
brew install tesseract
brew install tesseract-lang
```

### 2. Install Python Dependencies

```bash
cd ai_model
pip install -r requirements.txt
pip install pytesseract
```

### 3. Verify Installation

```bash
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

## 🧪 Testing

### Test OCR
```python
from models.ocr_extractor import OCRExtractor

ocr = OCRExtractor()
with open('test_image.jpg', 'rb') as f:
    result = ocr.extract_text(f)
    print(result['text'])
```

### Test Text Classification
```python
from models.text_classifier import TextClassifier

classifier = TextClassifier()
result = classifier.predict("Breaking news: shocking revelation!", "en")
print(result)
```

### Test Deepfake Detection
```python
from models.image_detector import ImageDetector

detector = ImageDetector()
with open('test_image.jpg', 'rb') as f:
    result = detector.predict(f, 'image')
    print(result)
```

## 🔄 Workflow

1. **User uploads content** (text, image, or video)
2. **Frontend sends to backend** (Node.js API)
3. **Backend forwards to AI API** (Python Flask)
4. **AI processes and returns results**
5. **Results saved to MongoDB**
6. **Frontend displays results** with visualizations

## 🌐 Language Support

### English
- Full support for all features
- BERT multilingual model
- Tesseract OCR

### Tamil (தமிழ்)
- Text detection
- OCR extraction
- Emotion analysis
- Uses multilingual BERT
- Tesseract Tamil language pack

## 📝 Next Steps

1. ✅ Download datasets from Kaggle
2. ✅ Train models using provided scripts
3. ✅ Install Tesseract OCR
4. ✅ Test all features
5. ✅ Deploy to production

## 🎓 Resources

- **Training Guide**: `ai_model/TRAINING_GUIDE.md`
- **Dataset Guide**: `KAGGLE_DATASETS.md`
- **Setup Instructions**: `SETUP_INSTRUCTIONS.md`
- **Architecture**: `ARCHITECTURE.md`

## 📄 License

MIT License - Free to use and modify
