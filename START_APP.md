# Quick Start Guide

## ✅ Installation Complete!

All dependencies have been installed successfully. Follow these steps to run the application:

## Step 1: Start MongoDB

Open a new terminal and run:

```bash
mongod
```

**Note:** If you don't have MongoDB installed locally, you can:
1. Download from: https://www.mongodb.com/try/download/community
2. Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas
   - Update `MONGODB_URI` in `server/.env` with your Atlas connection string

## Step 2: Start the Application

### Option A: Run All Services Together (Recommended)

From the root directory, run:

```bash
npm run dev
```

This will start:
- ✅ Frontend (React): http://localhost:3000
- ✅ Backend (Express): http://localhost:5000
- ✅ AI API (Flask): http://localhost:5001

### Option B: Run Services Separately

**Terminal 1 - Backend Server:**
```bash
cd server
npm run dev
```

**Terminal 2 - Frontend Client:**
```bash
cd client
npm start
```

**Terminal 3 - AI API:**
```bash
cd ai_model
python app.py
```

## Step 3: Access the Application

1. Open your browser and go to: **http://localhost:3000**
2. Register a new account
3. Start analyzing content!

## Step 4: Create Admin Account (Optional)

To access the Admin Panel:

1. Register a normal user account first
2. Open MongoDB Compass or MongoDB Shell
3. Connect to: `mongodb://localhost:27017/fakenews_db`
4. Run this command to make your user an admin:

```javascript
db.users.updateOne(
  { email: "your-email@example.com" },
  { $set: { role: "admin" } }
)
```

5. Refresh the page and you'll see the "Admin Panel" link in the navbar

## Features to Test

### 1. Text Detection
- Navigate to "Text Detection"
- Enter sample news text
- Select language (English or Tamil)
- Click "Analyze Text"
- View fake/real prediction with confidence score

### 2. Image Detection
- Navigate to "Image Detection"
- Upload an image (JPG, PNG)
- Click "Analyze Image"
- View deepfake detection results with heatmap

### 3. Emotion Analysis
- Navigate to "Emotion Analysis"
- Enter text with emotional content
- View emotion breakdown (Fear, Anger, Political Bias, Religious Trigger)
- Check manipulation score

### 4. Dashboard
- View your analysis history
- See analytics graphs
- Download PDF reports

### 5. Admin Panel (Admin only)
- View all users
- View analysis logs
- Check system statistics
- Block/unblock users

## Sample Test Data

### Fake News Example:
```
BREAKING: Shocking conspiracy exposed! Secret government plan revealed! 
You won't believe what they're hiding from us. Share this urgent message 
immediately before it's deleted!
```

### Real News Example:
```
According to a recent study published in the Journal of Science, 
researchers have found evidence supporting the effectiveness of 
renewable energy sources in reducing carbon emissions.
```

### Emotional Manipulation Example:
```
This is a dangerous threat to our religious values! The government is 
trying to destroy our faith and beliefs. We must act now to protect 
our sacred traditions from this terrible attack!
```

## Troubleshooting

### MongoDB Connection Error
```
MongooseServerSelectionError: connect ECONNREFUSED 127.0.0.1:27017
```
**Solution:** Make sure MongoDB is running with `mongod` command

### Port Already in Use
```
Error: listen EADDRINUSE: address already in use :::5000
```
**Solution:** 
- Kill the process using that port
- Or change the port in `.env` files

### Python Module Errors
**Solution:** Reinstall Python dependencies:
```bash
cd ai_model
pip install -r requirements.txt
```

### React Build Errors
**Solution:** Clear cache and reinstall:
```bash
cd client
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. **Customize Models**: Replace demo models with trained models
2. **Add More Languages**: Extend language support
3. **Deploy**: Follow deployment guide in ARCHITECTURE.md
4. **Secure**: Change JWT_SECRET in production

## Support

For detailed documentation:
- Setup: See `SETUP_INSTRUCTIONS.md`
- Architecture: See `ARCHITECTURE.md`
- Main README: See `README.md`

Enjoy using the Fake News Detection System! 🛡️
