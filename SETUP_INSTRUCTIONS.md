# Setup Instructions

## Prerequisites

Before starting, ensure you have the following installed:

1. **Node.js** (v16 or higher)
   - Download from: https://nodejs.org/
   - Verify: `node --version`

2. **Python** (v3.8 or higher)
   - Download from: https://www.python.org/
   - Verify: `python --version` or `python3 --version`

3. **MongoDB**
   - Download from: https://www.mongodb.com/try/download/community
   - Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas
   - Verify: `mongod --version`

4. **Git** (optional, for version control)
   - Download from: https://git-scm.com/

## Step-by-Step Installation

### 1. Install All Dependencies

Run this command from the root directory:

```bash
npm run install-all
```

This will install:
- Root dependencies (concurrently)
- Client dependencies (React, axios, etc.)
- Server dependencies (Express, mongoose, etc.)
- Python dependencies (Flask, transformers, etc.)

### 2. Configure Environment Variables

#### Server Configuration

Create `server/.env` file:

```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/fakenews_db
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production
AI_API_URL=http://localhost:5001
NODE_ENV=development
```

**Important:** Change `JWT_SECRET` to a random secure string in production!

#### Client Configuration

Create `client/.env` file:

```env
REACT_APP_API_URL=http://localhost:5000
```

#### AI Model Configuration

Create `ai_model/.env` file:

```env
FLASK_PORT=5001
MODEL_PATH=./models
FLASK_ENV=development
```

### 3. Start MongoDB

#### Option A: Local MongoDB

```bash
# Windows
mongod

# macOS/Linux
sudo systemctl start mongod
# or
mongod --dbpath /path/to/data/directory
```

#### Option B: MongoDB Atlas (Cloud)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get connection string
4. Update `MONGODB_URI` in `server/.env`

### 4. Download NLTK Data (First Time Only)

```bash
cd ai_model
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 5. Run the Application

From the root directory:

```bash
npm run dev
```

This will start all three services:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **AI API**: http://localhost:5001

### 6. Create Admin Account

1. Open http://localhost:3000
2. Register a new account
3. Open MongoDB and manually change the user's role to 'admin':

```javascript
// In MongoDB shell or Compass
db.users.updateOne(
  { email: "your-email@example.com" },
  { $set: { role: "admin" } }
)
```

## Running Services Individually

If you prefer to run services separately:

### Backend Server
```bash
cd server
npm run dev
```

### Frontend Client
```bash
cd client
npm start
```

### AI API
```bash
cd ai_model
python app.py
```

## Testing the Application

### 1. Test Authentication
- Register a new user
- Login with credentials
- Verify JWT token is stored

### 2. Test Text Detection
- Navigate to "Text Detection"
- Enter sample news text
- Click "Analyze Text"
- View results with confidence score

### 3. Test Image Detection
- Navigate to "Image Detection"
- Upload an image
- Click "Analyze Image"
- View deepfake detection results

### 4. Test Emotion Analysis
- Navigate to "Emotion Analysis"
- Enter text with emotional content
- View emotion breakdown and manipulation score

### 5. Test Dashboard
- View analysis history
- Download PDF reports
- Check analytics graphs

### 6. Test Admin Panel (Admin only)
- View all users
- View analysis logs
- Check system statistics
- Block/unblock users

## Troubleshooting

### MongoDB Connection Error
```
Error: connect ECONNREFUSED 127.0.0.1:27017
```
**Solution:** Make sure MongoDB is running (`mongod` command)

### Port Already in Use
```
Error: listen EADDRINUSE: address already in use :::5000
```
**Solution:** Change port in `.env` file or kill the process using that port

### Python Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Run `pip install -r ai_model/requirements.txt`

### CORS Error in Browser
```
Access to XMLHttpRequest has been blocked by CORS policy
```
**Solution:** Verify `REACT_APP_API_URL` in `client/.env` matches backend URL

### AI Model Predictions Not Working
**Solution:** The demo uses simplified models. For production:
1. Train models with real datasets
2. Use pre-trained BERT for text classification
3. Use pre-trained CNN (EfficientNet/Xception) for deepfake detection

## Production Deployment

### Environment Variables
- Set `NODE_ENV=production`
- Use strong `JWT_SECRET`
- Use MongoDB Atlas or production database
- Enable HTTPS

### Build Frontend
```bash
cd client
npm run build
```

### Deploy Options
- **Frontend**: Vercel, Netlify, AWS S3
- **Backend**: Heroku, AWS EC2, DigitalOcean
- **AI API**: AWS Lambda, Google Cloud Run
- **Database**: MongoDB Atlas

## Model Training (Advanced)

To train real models:

### Fake News Detection
1. Get dataset: Kaggle Fake News Dataset
2. Train BERT model using `transformers` library
3. Save model to `ai_model/models/`
4. Update `text_classifier.py` to load trained model

### Deepfake Detection
1. Get dataset: FaceForensics++, DFDC
2. Train CNN (EfficientNet-B4 or XceptionNet)
3. Save model to `ai_model/models/`
4. Update `image_detector.py` to load trained model

## Support

For issues or questions:
1. Check troubleshooting section
2. Review error logs in terminal
3. Check MongoDB logs
4. Verify all environment variables are set correctly

## License

MIT License - Feel free to use and modify for your projects!
