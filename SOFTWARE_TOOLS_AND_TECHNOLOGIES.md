# 🛠️ Software Tools and Technologies Used

## Complete Technology Stack

### 1. Frontend Technologies

#### Core Framework
- **React.js** (v18.2.0) - JavaScript library for building user interfaces
- **React DOM** (v18.2.0) - React package for working with the DOM
- **React Scripts** (v5.0.1) - Configuration and scripts for Create React App

#### Routing & Navigation
- **React Router DOM** (v6.18.0) - Declarative routing for React applications

#### HTTP Client
- **Axios** (v1.6.0) - Promise-based HTTP client for API requests

#### UI Components & Visualization
- **Recharts** (v2.10.0) - Composable charting library for React
- **React Toastify** (v9.1.3) - Toast notifications for React

#### Styling
- **CSS3** - Custom styling with animations
- **CSS Grid & Flexbox** - Modern layout systems

---

### 2. Backend Technologies

#### Runtime & Framework
- **Node.js** - JavaScript runtime environment
- **Express.js** - Fast, minimalist web framework for Node.js

#### Database
- **MongoDB** - NoSQL document database
- **Mongoose** - MongoDB object modeling for Node.js

#### Authentication & Security
- **JSON Web Tokens (JWT)** - Token-based authentication
- **jsonwebtoken** - JWT implementation for Node.js
- **bcryptjs** - Password hashing library

#### File Upload
- **Multer** - Middleware for handling multipart/form-data (file uploads)

#### Environment Variables
- **dotenv** - Loads environment variables from .env file

#### Cross-Origin Resource Sharing
- **CORS** - Enable CORS with various options

---

### 3. AI/ML Technologies (Python)

#### Web Framework
- **Flask** - Lightweight WSGI web application framework
- **Flask-CORS** - Handle Cross-Origin Resource Sharing

#### Machine Learning Libraries
- **scikit-learn** - Machine learning library
  - TF-IDF Vectorizer (text feature extraction)
  - Logistic Regression (classification)
  - Train-test split utilities
  - Accuracy metrics

#### Natural Language Processing
- **NLTK** (Natural Language Toolkit) - NLP library
  - Tokenization
  - Punkt tokenizer
- **TextBlob** - Simplified text processing
  - Sentiment analysis
  - Polarity detection
  - Subjectivity analysis

#### Data Processing
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing library

#### Image Processing
- **OpenCV (cv2)** - Computer vision library
- **Pillow (PIL)** - Python Imaging Library

#### OCR (Optical Character Recognition)
- **Tesseract OCR** - Open-source OCR engine
- **pytesseract** - Python wrapper for Tesseract

#### Web Scraping & RSS
- **feedparser** - Parse RSS and Atom feeds
- **requests** - HTTP library for Python

---

### 4. Development Tools

#### Package Managers
- **npm** (Node Package Manager) - JavaScript package manager
- **pip** - Python package installer

#### Version Control
- **Git** - Distributed version control system
- **GitHub** - Code hosting platform

#### Code Editor/IDE
- **Visual Studio Code** (recommended)
- **Any text editor** with JavaScript/Python support

---

### 5. Database Tools

#### Database Management
- **MongoDB Community Server** - Database server
- **MongoDB Compass** (optional) - GUI for MongoDB

---

### 6. External APIs & Services

#### Data Sources
- **Kaggle API** - Download datasets
  - Fake news text dataset (44,889 articles)
  - Deepfake images dataset (140,000 images)

#### RSS Feeds
- **Times of India RSS** - Trusted news source
- **Dina Thanthi RSS** - Tamil news source

---

### 7. Testing & Debugging Tools

#### Browser DevTools
- **Chrome DevTools** - Debugging, network inspection
- **Firefox Developer Tools** - Alternative debugging

#### API Testing
- **Postman** (optional) - API development and testing
- **cURL** - Command-line HTTP client

---

## Detailed Breakdown by Component

### Frontend (React App)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.18.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "recharts": "^2.10.0",
    "react-toastify": "^9.1.3"
  }
}
```

**Purpose**: User interface, routing, API communication, data visualization

---

### Backend (Node.js/Express)

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "mongoose": "^7.6.3",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "dotenv": "^16.3.1",
    "cors": "^2.8.5",
    "multer": "^1.4.5-lts.1",
    "axios": "^1.6.0"
  }
}
```

**Purpose**: API server, authentication, database operations, file handling

---

### AI Model (Python/Flask)

```txt
Flask==2.3.3
flask-cors==4.0.0
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
nltk==3.8.1
textblob==0.17.1
opencv-python==4.8.0.76
Pillow==10.0.0
pytesseract==0.3.10
feedparser==6.0.10
requests==2.31.0
python-dotenv==1.0.0
```

**Purpose**: Machine learning models, text analysis, image processing, OCR

---

## Installation Commands

### Frontend Setup
```bash
cd client
npm install
```

### Backend Setup
```bash
cd server
npm install
```

### AI Model Setup
```bash
cd ai_model
pip install -r requirements.txt
```

### Additional Requirements
```bash
# MongoDB (Windows)
Download from: https://www.mongodb.com/try/download/community

# Tesseract OCR (Windows)
Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Kaggle API
pip install kaggle
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│  - React Router, Axios, Recharts, React Toastify       │
│  - Port: 3000                                           │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP Requests
                      ↓
┌─────────────────────────────────────────────────────────┐
│                BACKEND (Node.js/Express)                │
│  - JWT Auth, MongoDB, Multer, CORS                     │
│  - Port: 5000                                           │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP Requests
                      ↓
┌─────────────────────────────────────────────────────────┐
│                  AI API (Python/Flask)                  │
│  - scikit-learn, NLTK, TextBlob, OpenCV                │
│  - Port: 5001                                           │
└─────────────────────────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│                   DATABASE (MongoDB)                    │
│  - Users Collection, Analysis Collection               │
│  - Port: 27017                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Key Features by Technology

### Text Classification (99.11% Accuracy)
- **scikit-learn**: TF-IDF + Logistic Regression
- **Trained on**: 44,889 news articles
- **Dataset**: Kaggle fake news dataset

### Emotional Manipulation Analysis
- **NLTK**: Text tokenization
- **TextBlob**: Sentiment analysis
- **Custom algorithms**: Keyword detection, manipulation scoring

### Deepfake Detection
- **OpenCV**: Image processing
- **Pillow**: Image manipulation
- **Custom model**: Deepfake classification

### OCR Text Extraction
- **Tesseract**: Text recognition from images
- **pytesseract**: Python integration
- **Supports**: English and Tamil

### News Verification
- **feedparser**: RSS feed parsing
- **requests**: HTTP requests to news sources
- **Sources**: Times of India, Dina Thanthi

---

## Development Environment

### Required Software
1. **Node.js** (v14 or higher)
2. **Python** (v3.8 or higher)
3. **MongoDB** (Community Edition)
4. **Git** (for version control)
5. **Tesseract OCR** (for text extraction)

### Recommended Tools
1. **Visual Studio Code** - Code editor
2. **MongoDB Compass** - Database GUI
3. **Postman** - API testing
4. **Chrome DevTools** - Frontend debugging

---

## Browser Compatibility

### Supported Browsers
- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Edge
- ✅ Safari
- ✅ Opera

### Required Features
- ES6+ JavaScript support
- CSS Grid & Flexbox
- Fetch API / XMLHttpRequest
- LocalStorage

---

## Operating System Support

### Development
- ✅ Windows 10/11
- ✅ macOS
- ✅ Linux (Ubuntu, Debian, etc.)

### Production
- ✅ Any OS supporting Node.js, Python, MongoDB

---

## Cloud Services (Optional)

### Deployment Options
- **Frontend**: Vercel, Netlify, AWS S3
- **Backend**: Heroku, AWS EC2, DigitalOcean
- **Database**: MongoDB Atlas (cloud)
- **AI Model**: AWS Lambda, Google Cloud Functions

---

## Security Tools

### Authentication
- **JWT** - Stateless authentication
- **bcryptjs** - Password hashing (10 rounds)

### Data Protection
- **CORS** - Cross-origin security
- **Environment variables** - Sensitive data protection
- **Input validation** - XSS prevention

---

## Performance Optimization

### Frontend
- **React.lazy** - Code splitting (potential)
- **Memoization** - Component optimization
- **CSS animations** - Hardware acceleration

### Backend
- **Connection pooling** - MongoDB optimization
- **Caching** - Response caching (potential)
- **Compression** - Response compression (potential)

### AI Model
- **Model persistence** - Pre-trained models loaded once
- **Batch processing** - Efficient predictions
- **Vectorization** - NumPy optimizations

---

## Total Technologies Count

- **Frontend Libraries**: 6
- **Backend Libraries**: 8
- **AI/ML Libraries**: 13
- **Development Tools**: 10+
- **External Services**: 3

**Total**: 40+ software tools and technologies

---

## License Information

### Open Source
- All major libraries are open-source
- MIT, Apache 2.0, BSD licenses
- Free for commercial use

### Proprietary
- MongoDB (SSPL for Community Edition)
- Tesseract (Apache 2.0)

---

## System Requirements

### Minimum
- **RAM**: 4GB
- **Storage**: 10GB free space
- **CPU**: Dual-core processor
- **Internet**: Required for initial setup

### Recommended
- **RAM**: 8GB+
- **Storage**: 20GB+ free space
- **CPU**: Quad-core processor
- **Internet**: Stable connection

---

## Summary

This Fake News Detection System uses a modern, full-stack architecture combining:
- **Frontend**: React ecosystem for responsive UI
- **Backend**: Node.js/Express for robust API
- **AI/ML**: Python/Flask with scikit-learn for intelligent detection
- **Database**: MongoDB for flexible data storage
- **External APIs**: Kaggle datasets and RSS feeds for real data

All tools are industry-standard, well-documented, and actively maintained.
