# Kaggle Datasets for Training

This document lists all the datasets needed to train the AI models for fake news detection.

## Setup Kaggle API

### 1. Install Kaggle CLI
```bash
pip install kaggle
```

### 2. Get API Credentials
1. Go to https://www.kaggle.com/settings
2. Scroll to "API" section
3. Click "Create New API Token"
4. Download `kaggle.json`

### 3. Configure Credentials

**Windows:**
```bash
mkdir %USERPROFILE%\.kaggle
move kaggle.json %USERPROFILE%\.kaggle\
```

**Linux/Mac:**
```bash
mkdir ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

## Required Datasets

### 1. Fake News Text Detection

#### Dataset 1: Fake and Real News Dataset
- **URL**: https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset
- **Size**: ~50MB
- **Files**: Fake.csv, True.csv
- **Articles**: 44,898 articles

**Download:**
```bash
kaggle datasets download -d clmentbisaillon/fake-and-real-news-dataset
unzip fake-and-real-news-dataset.zip -d datasets/fake_news_text/
```

#### Dataset 2: LIAR Dataset (Alternative)
- **URL**: https://www.kaggle.com/datasets/mrisdal/fake-news
- **Size**: ~10MB

**Download:**
```bash
kaggle datasets download -d mrisdal/fake-news
unzip fake-news.zip -d datasets/fake_news_liar/
```

### 2. Deepfake Image Detection

#### Dataset 1: 140k Real and Fake Faces
- **URL**: https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces
- **Size**: ~2.5GB
- **Images**: 140,000 images

**Download:**
```bash
kaggle datasets download -d xhlulu/140k-real-and-fake-faces
unzip 140k-real-and-fake-faces.zip -d datasets/deepfake_images/
```

#### Dataset 2: Deepfake Detection Challenge (Alternative)
- **URL**: https://www.kaggle.com/c/deepfake-detection-challenge/data
- **Size**: ~470GB (Large!)

**Download:**
```bash
kaggle competitions download -c deepfake-detection-challenge
```

### 3. Sentiment & Emotion Analysis

#### Dataset 1: Sentiment140
- **URL**: https://www.kaggle.com/datasets/kazanova/sentiment140
- **Size**: ~80MB
- **Tweets**: 1.6 million tweets

**Download:**
```bash
kaggle datasets download -d kazanova/sentiment140
unzip sentiment140.zip -d datasets/sentiment/
```

#### Dataset 2: Emotion Detection from Text
- **URL**: https://www.kaggle.com/datasets/praveengovi/emotions-dataset-for-nlp
- **Size**: ~5MB

**Download:**
```bash
kaggle datasets download -d praveengovi/emotions-dataset-for-nlp
unzip emotions-dataset-for-nlp.zip -d datasets/emotions/
```

### 4. Tamil Language Support

#### Dataset 1: Tamil News Classification
- **URL**: https://www.kaggle.com/datasets/sudalairajkumar/tamil-nlp
- **Size**: ~20MB

**Download:**
```bash
kaggle datasets download -d sudalairajkumar/tamil-nlp
unzip tamil-nlp.zip -d datasets/tamil_news/
```

#### Dataset 2: Tamil Sentiment Analysis
- **URL**: https://www.kaggle.com/datasets/bharathkumar/tamil-sentiment-analysis
- **Size**: ~5MB

**Download:**
```bash
kaggle datasets download -d bharathkumar/tamil-sentiment-analysis
unzip tamil-sentiment-analysis.zip -d datasets/tamil_sentiment/
```

## Quick Download Script

Create `download_all.sh` (Linux/Mac) or `download_all.bat` (Windows):

```bash
#!/bin/bash

# Create directories
mkdir -p datasets/{fake_news_text,deepfake_images,sentiment,emotions,tamil_news}

# Download datasets
echo "Downloading Fake News Dataset..."
kaggle datasets download -d clmentbisaillon/fake-and-real-news-dataset
unzip -q fake-and-real-news-dataset.zip -d datasets/fake_news_text/
rm fake-and-real-news-dataset.zip

echo "Downloading Deepfake Images..."
kaggle datasets download -d xhlulu/140k-real-and-fake-faces
unzip -q 140k-real-and-fake-faces.zip -d datasets/deepfake_images/
rm 140k-real-and-fake-faces.zip

echo "Downloading Sentiment Dataset..."
kaggle datasets download -d kazanova/sentiment140
unzip -q sentiment140.zip -d datasets/sentiment/
rm sentiment140.zip

echo "Downloading Emotions Dataset..."
kaggle datasets download -d praveengovi/emotions-dataset-for-nlp
unzip -q emotions-dataset-for-nlp.zip -d datasets/emotions/
rm emotions-dataset-for-nlp.zip

echo "Downloading Tamil Dataset..."
kaggle datasets download -d sudalairajkumar/tamil-nlp
unzip -q tamil-nlp.zip -d datasets/tamil_news/
rm tamil-nlp.zip

echo "✅ All datasets downloaded!"
```

Make executable and run:
```bash
chmod +x download_all.sh
./download_all.sh
```

## Dataset Structure

After downloading, your directory should look like:

```
datasets/
├── fake_news_text/
│   ├── Fake.csv
│   └── True.csv
├── deepfake_images/
│   ├── real/
│   │   └── *.jpg
│   └── fake/
│       └── *.jpg
├── sentiment/
│   └── training.1600000.processed.noemoticon.csv
├── emotions/
│   ├── train.txt
│   └── test.txt
└── tamil_news/
    └── tamil_news.csv
```

## Dataset Sizes

| Dataset | Size | Download Time (10 Mbps) |
|---------|------|-------------------------|
| Fake News Text | 50 MB | ~1 minute |
| Deepfake Images | 2.5 GB | ~30 minutes |
| Sentiment140 | 80 MB | ~2 minutes |
| Emotions | 5 MB | ~30 seconds |
| Tamil NLP | 20 MB | ~1 minute |
| **Total** | **~2.7 GB** | **~35 minutes** |

## Alternative: Use Python Script

Use the provided script:
```bash
cd ai_model
python scripts/download_datasets.py
```

This will:
- Check Kaggle API configuration
- Download all required datasets
- Extract and organize files
- Verify downloads

## Troubleshooting

### Error: "401 - Unauthorized"
- Check if `kaggle.json` is in correct location
- Verify API credentials are valid
- Re-download API token from Kaggle

### Error: "403 - Forbidden"
- Accept dataset rules on Kaggle website
- Some datasets require competition acceptance

### Error: "Dataset not found"
- Check dataset URL is correct
- Dataset might be private or removed

### Slow Download
- Use faster internet connection
- Download during off-peak hours
- Consider downloading smaller datasets first

## Next Steps

After downloading datasets:

1. **Verify Data**
   ```bash
   python scripts/verify_datasets.py
   ```

2. **Train Models**
   ```bash
   python scripts/train_text_classifier.py
   python scripts/train_deepfake_detector.py
   python scripts/train_emotion_analyzer.py
   ```

3. **Test Models**
   ```bash
   python scripts/test_models.py
   ```

## Additional Resources

- **Kaggle API Docs**: https://github.com/Kaggle/kaggle-api
- **Dataset Search**: https://www.kaggle.com/datasets
- **Competitions**: https://www.kaggle.com/competitions

## License

Each dataset has its own license. Please check individual dataset pages for licensing information before using in production.
