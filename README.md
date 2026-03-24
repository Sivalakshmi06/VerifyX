# Multilingual AI-Based Fake News & Deepfake Detection System

A comprehensive full-stack application for detecting fake news, deepfakes, and emotional manipulation in content.

## Features

- 🔐 User Authentication (JWT-based)
- 📰 Fake News Text Detection (English + Tamil)
- 🖼️ Deepfake Image Detection
- 😡 Emotional Manipulation Analysis
- 📊 Analytics Dashboard
- 👨‍💼 Admin Panel
- 📄 PDF Report Generation

## Tech Stack

- **Frontend**: React.js
- **Backend**: Node.js + Express
- **Database**: MongoDB
- **AI/ML**: Python Flask API (BERT, CNN, NLP)

## Installation

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- MongoDB (running instance)

### Setup Steps

1. **Clone and Install Dependencies**
```bash
npm run install-all
```

2. **Configure Environment Variables**

Create `.env` files in respective directories:

**server/.env**
```
PORT=5000
MONGODB_URI=mongodb://localhost:27017/fakenews_db
JWT_SECRET=your_jwt_secret_key_here
AI_API_URL=http://localhost:5001
```

**client/.env**
```
REACT_APP_API_URL=http://localhost:5000
```

**ai_model/.env**
```
FLASK_PORT=5001
MODEL_PATH=./models
```

3. **Start MongoDB**
```bash
mongod
```

4. **Run the Application**
```bash
npm run dev
```

This will start:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- AI API: http://localhost:5001

## Project Structure

```
├── client/          # React frontend
├── server/          # Node.js backend
├── ai_model/        # Python Flask AI API
└── README.md
```

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register user
- POST `/api/auth/login` - Login user

### Detection
- POST `/api/detect/text` - Analyze text for fake news
- POST `/api/detect/image` - Detect deepfake in image
- POST `/api/detect/emotion` - Analyze emotional manipulation

### Dashboard
- GET `/api/dashboard/history` - Get user analysis history
- GET `/api/dashboard/analytics` - Get analytics data
- GET `/api/dashboard/report/:id` - Download PDF report

### Admin
- GET `/api/admin/users` - Get all users
- GET `/api/admin/logs` - Get analysis logs
- POST `/api/admin/block/:userId` - Block user

## Models Used

1. **Fake News Detection**: BERT-based text classification
2. **Deepfake Detection**: CNN-based image analysis
3. **Emotion Analysis**: NLP sentiment analysis with bias detection

## License

MIT
