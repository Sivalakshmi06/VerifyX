# System Architecture

## Overview

This is a full-stack web application for detecting fake news, deepfakes, and emotional manipulation using AI/ML techniques.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT (React)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │   Text   │  │  Image   │  │ Emotion  │   │
│  │  Pages   │  │ Detection│  │Detection │  │ Analysis │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐                                │
│  │Dashboard │  │  Admin   │                                │
│  └──────────┘  └──────────┘                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVER (Node.js/Express)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │  Detect  │  │Dashboard │  │  Admin   │   │
│  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐                                │
│  │   JWT    │  │  Multer  │                                │
│  │   Auth   │  │  Upload  │                                │
│  └──────────┘  └──────────┘                                │
└─────────────────────────────────────────────────────────────┘
                │                           │
                │                           │ HTTP API Calls
                ▼                           ▼
┌─────────────────────────┐   ┌─────────────────────────────┐
│   MongoDB Database      │   │   AI API (Python/Flask)     │
│  ┌──────────────────┐   │   │  ┌────────────────────┐    │
│  │  Users           │   │   │  │ Text Classifier    │    │
│  │  - name          │   │   │  │ (BERT/LogReg)      │    │
│  │  - email         │   │   │  └────────────────────┘    │
│  │  - password      │   │   │  ┌────────────────────┐    │
│  │  - role          │   │   │  │ Image Detector     │    │
│  └──────────────────┘   │   │  │ (CNN/EfficientNet) │    │
│  ┌──────────────────┐   │   │  └────────────────────┘    │
│  │  Analyses        │   │   │  ┌────────────────────┐    │
│  │  - userId        │   │   │  │ Emotion Analyzer   │    │
│  │  - type          │   │   │  │ (NLP/TextBlob)     │    │
│  │  - content       │   │   │  └────────────────────┘    │
│  │  - result        │   │   └─────────────────────────────┘
│  └──────────────────┘   │
└─────────────────────────┘
```

## Technology Stack

### Frontend (Client)
- **Framework**: React 18
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Notifications**: React Toastify
- **Styling**: Custom CSS

### Backend (Server)
- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: MongoDB with Mongoose ODM
- **Authentication**: JWT (jsonwebtoken)
- **Password Hashing**: bcryptjs
- **File Upload**: Multer
- **PDF Generation**: PDFKit
- **Validation**: express-validator

### AI/ML (Python)
- **Framework**: Flask
- **Text Processing**: 
  - transformers (BERT)
  - scikit-learn (Logistic Regression)
  - langdetect (Language detection)
  - NLTK (Natural Language Toolkit)
  - TextBlob (Sentiment analysis)
- **Image Processing**:
  - OpenCV (cv2)
  - Pillow (PIL)
  - NumPy
- **Deep Learning**: PyTorch

## Data Flow

### 1. User Authentication Flow
```
User → Register/Login → Server validates → JWT token generated → 
Token stored in localStorage → Token sent with each request
```

### 2. Text Detection Flow
```
User enters text → Client sends to /api/detect/text → 
Server forwards to AI API → Text Classifier analyzes → 
Results saved to MongoDB → Response sent to client
```

### 3. Image Detection Flow
```
User uploads image → Multer processes file → 
Server sends to AI API → Image Detector analyzes → 
Heatmap generated → Results saved → Response with base64 image
```

### 4. Emotion Analysis Flow
```
User enters text → Client sends to /api/detect/emotion → 
Server forwards to AI API → Emotion Analyzer processes → 
Emotion scores calculated → Results saved → Response sent
```

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  name: String,
  email: String (unique),
  password: String (hashed),
  role: String (enum: ['user', 'admin']),
  isBlocked: Boolean,
  createdAt: Date
}
```

### Analyses Collection
```javascript
{
  _id: ObjectId,
  userId: ObjectId (ref: User),
  type: String (enum: ['text', 'image', 'emotion']),
  content: String,
  result: {
    prediction: String,
    confidence: Number,
    details: Mixed
  },
  language: String,
  createdAt: Date
}
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Detection
- `POST /api/detect/text` - Analyze text for fake news
- `POST /api/detect/image` - Detect deepfake in image
- `POST /api/detect/emotion` - Analyze emotional manipulation

### Dashboard
- `GET /api/dashboard/history` - Get user's analysis history
- `GET /api/dashboard/analytics` - Get analytics data
- `GET /api/dashboard/report/:id` - Download PDF report

### Admin
- `GET /api/admin/users` - Get all users
- `GET /api/admin/logs` - Get all analysis logs
- `GET /api/admin/stats` - Get system statistics
- `POST /api/admin/block/:userId` - Block/unblock user

### AI API
- `POST /api/analyze/text` - Text classification
- `POST /api/analyze/image` - Image deepfake detection
- `POST /api/analyze/emotion` - Emotion analysis

## Security Features

1. **Password Security**: bcrypt hashing with salt
2. **JWT Authentication**: Secure token-based auth
3. **Role-Based Access**: Admin vs User permissions
4. **Input Validation**: express-validator for all inputs
5. **CORS Protection**: Configured CORS middleware
6. **File Upload Limits**: 5MB max file size
7. **Blocked User Check**: Middleware prevents blocked users

## Scalability Considerations

1. **Database Indexing**: Indexes on userId and createdAt
2. **Pagination**: All list endpoints support pagination
3. **Stateless API**: JWT enables horizontal scaling
4. **Microservices**: AI API separated for independent scaling
5. **Caching**: Can add Redis for session/result caching

## Future Enhancements

1. **Real-time Detection**: WebSocket for live analysis
2. **Batch Processing**: Analyze multiple files at once
3. **Advanced Models**: Fine-tuned BERT, GPT for text
4. **Video Analysis**: Deepfake detection in videos
5. **Multi-language**: Support for more languages
6. **API Rate Limiting**: Prevent abuse
7. **Email Notifications**: Alert users of analysis results
8. **Social Media Integration**: Analyze posts from Twitter, Facebook
9. **Browser Extension**: Detect fake news while browsing
10. **Mobile App**: React Native mobile version

## Performance Optimization

1. **Frontend**: Code splitting, lazy loading
2. **Backend**: Connection pooling, query optimization
3. **AI Models**: Model quantization, TensorRT optimization
4. **Caching**: Redis for frequently accessed data
5. **CDN**: Static assets served via CDN
6. **Load Balancing**: Multiple server instances

## Monitoring & Logging

1. **Application Logs**: Winston for structured logging
2. **Error Tracking**: Sentry for error monitoring
3. **Performance**: New Relic or DataDog
4. **Database**: MongoDB Atlas monitoring
5. **API Analytics**: Track usage patterns

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                         │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Server 1   │    │   Server 2   │    │   Server N   │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                ┌───────────────────────┐
                │   MongoDB Cluster     │
                └───────────────────────┘
```

## License

MIT License
