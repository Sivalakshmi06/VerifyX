# 🚀 How to Start Your Application

## ⚠️ CRITICAL FIX APPLIED - RESTART REQUIRED

**A proxy configuration was just added to fix the "Analysis Failed" error.**
**You MUST restart the frontend for this to take effect!**

## Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- MongoDB (running on localhost:27017)

## IMPORTANT: Start Services in Correct Order

### Step 1: Start MongoDB
Make sure MongoDB is running on your system:
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### Step 2: Start AI API (Port 5001) - START FIRST
```bash
cd ai_model
python app.py
```
✅ Wait until you see: "Running on http://0.0.0.0:5001"

### Step 3: Start Backend Server (Port 5000) - START SECOND
Open a NEW terminal:
```bash
cd server
node server.js
```
✅ Wait until you see: "Server running on port 5000"

### Step 4: Start Frontend (Port 3000) - START LAST & RESTART NOW
Open a NEW terminal:
```bash
cd client
npm start
```
✅ Wait until browser opens automatically at http://localhost:3000

**IF FRONTEND IS ALREADY RUNNING:**
1. Stop it (Ctrl+C in the terminal)
2. Run `npm start` again
3. This loads the new proxy configuration

## 🔧 What Was Fixed

✅ Added proxy configuration to `client/package.json`
- Frontend now correctly routes `/api/*` calls to backend (port 5000)
- Backend correctly routes AI calls to AI API (port 5001)
- This fixes the "Analysis Failed" and "Not Found" errors

## Access the Application
Open your browser and go to: **http://localhost:3000**

## Testing Emotional Analysis (FIXED!)

1. **Register/Login first** (authentication required)
2. Go to "Emotional Manipulation Analysis" page
3. Paste this test text:
```
i jest i feel grumpy tired and pre menstrual which i probably am but then again its only been a week and im about as fit as a walrus on vacation for the summer
```
4. Click "Analyze Emotions"
5. View results with:
   - ✅ Manipulation Type
   - ✅ Confidence Score
   - ✅ Triggering Words
   - ✅ Detailed Explanation
   - ✅ Manipulation Techniques
   - ✅ Emotion Breakdown

## Features Available

### 1. News Detection 📰
- Trained model with 99.11% accuracy
- Real-time fake news detection
- Source reliability analysis
- News verification against Times of India & Dina Thanthi

### 2. Emotional Manipulation Analysis 😡
- **ENHANCED VERSION WITH ALL NEW FIELDS!**
- Manipulation Type identification
- Triggering Words detection
- Detailed Explanation
- Confidence Score (0-100%)
- 7 manipulation techniques detection
- Emotion breakdown (Fear, Anger, Political, Religious)
- Sentiment analysis

### 3. Deepfake Detection 🖼️
- Image deepfake detection
- Video analysis support (up to 50MB)
- Heatmap visualization

## Troubleshooting

### "Analysis Failed" Error
- ✅ **FIXED**: Proxy added, restart frontend
- Make sure you're logged in first
- Check all 3 services are running

### "Not Found" Error
- ✅ **FIXED**: Proxy configuration added
- Restart frontend (Ctrl+C then npm start)

### Port Already in Use
- Port 5000 busy: Change PORT in `server/.env`
- Port 5001 busy: Change FLASK_PORT in `ai_model/.env`
- Port 3000 busy: App will prompt to use another port

### MongoDB Connection Error
```bash
# Check if MongoDB is running
net start MongoDB
```

### 401 Unauthorized
- Token expired, logout and login again
- Make sure you registered/logged in

## Verify Services Are Running

```bash
# Check all ports (Windows)
netstat -ano | findstr "3000 5000 5001"

# Check all ports (Linux/Mac)
lsof -i :3000,5000,5001
```

## Access Points

- **Frontend (Main App)**: http://localhost:3000
- **Backend API**: http://localhost:5000/health
- **AI API**: http://localhost:5001/health

## Current Status

✅ Proxy configuration added to client/package.json
✅ All field mappings verified and connected
✅ Enhanced emotional analysis fully implemented
✅ Trained model loaded (99.11% accuracy)
✅ MongoDB schemas updated

## 🎯 Next Steps

1. **RESTART FRONTEND** (if already running)
2. Open http://localhost:3000
3. Login/Register
4. Test Emotional Analysis with sample text
5. Enjoy the enhanced features!
