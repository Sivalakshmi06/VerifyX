# MongoDB Setup Guide

You have two options for MongoDB: Local Installation or Cloud (MongoDB Atlas)

## Option 1: Install MongoDB Locally (Recommended for Development)

### Windows Installation

1. **Download MongoDB Community Server**
   - Go to: https://www.mongodb.com/try/download/community
   - Select: Windows, MSI package
   - Click "Download"

2. **Install MongoDB**
   - Run the downloaded `.msi` file
   - Choose "Complete" installation
   - Install as a Windows Service (recommended)
   - Install MongoDB Compass (GUI tool) - check the box

3. **Verify Installation**
   Open PowerShell and run:
   ```powershell
   mongod --version
   ```

4. **Start MongoDB Service**
   MongoDB should start automatically as a Windows service. If not:
   ```powershell
   net start MongoDB
   ```

5. **Test Connection**
   ```powershell
   mongosh
   ```
   You should see the MongoDB shell prompt.

### Alternative: Using Chocolatey (Windows Package Manager)

If you have Chocolatey installed:
```powershell
choco install mongodb
```

## Option 2: Use MongoDB Atlas (Cloud - No Installation Required)

This is the easiest option if you don't want to install MongoDB locally.

### Steps:

1. **Create Free Account**
   - Go to: https://www.mongodb.com/cloud/atlas/register
   - Sign up for free (no credit card required)

2. **Create a Cluster**
   - Click "Build a Database"
   - Choose "FREE" tier (M0 Sandbox)
   - Select a cloud provider and region (choose closest to you)
   - Click "Create Cluster" (takes 3-5 minutes)

3. **Create Database User**
   - Go to "Database Access" in left menu
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Username: `admin`
   - Password: Create a strong password (save it!)
   - Database User Privileges: "Atlas admin"
   - Click "Add User"

4. **Whitelist Your IP**
   - Go to "Network Access" in left menu
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (for development)
   - Click "Confirm"

5. **Get Connection String**
   - Go to "Database" in left menu
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string (looks like):
   ```
   mongodb+srv://admin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

6. **Update Your .env File**
   Open `server/.env` and replace the MONGODB_URI:
   ```env
   MONGODB_URI=mongodb+srv://admin:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/fakenews_db?retryWrites=true&w=majority
   ```
   
   Replace:
   - `YOUR_PASSWORD` with your actual password
   - `cluster0.xxxxx` with your actual cluster address

## Verify MongoDB Connection

### Test with Node.js

Create a test file `server/test-db.js`:

```javascript
const mongoose = require('mongoose');
require('dotenv').config();

mongoose.connect(process.env.MONGODB_URI)
  .then(() => {
    console.log('✅ MongoDB connected successfully!');
    process.exit(0);
  })
  .catch((err) => {
    console.error('❌ MongoDB connection error:', err.message);
    process.exit(1);
  });
```

Run it:
```bash
cd server
node test-db.js
```

## MongoDB Compass (GUI Tool)

If you installed MongoDB Compass:

1. Open MongoDB Compass
2. Connection string:
   - Local: `mongodb://localhost:27017`
   - Atlas: Use the connection string from Atlas
3. Click "Connect"
4. You can now browse your databases visually

## Common Issues

### Issue: "mongod is not recognized"
**Solution:** MongoDB is not in your PATH. Either:
- Reinstall MongoDB and check "Add to PATH"
- Or manually add to PATH: `C:\Program Files\MongoDB\Server\7.0\bin`

### Issue: "Connection refused"
**Solution:** 
- Make sure MongoDB service is running: `net start MongoDB`
- Check if port 27017 is available

### Issue: "Authentication failed" (Atlas)
**Solution:**
- Double-check username and password
- Make sure you URL-encoded special characters in password
- Verify IP is whitelisted

### Issue: "Network timeout" (Atlas)
**Solution:**
- Check your internet connection
- Verify IP whitelist includes your current IP
- Try "Allow Access from Anywhere" temporarily

## Recommended: Use MongoDB Atlas for This Project

For this project, I recommend using MongoDB Atlas because:
- ✅ No installation required
- ✅ Free tier available
- ✅ Automatic backups
- ✅ Easy to share with team
- ✅ Production-ready
- ✅ Works from anywhere

## Next Steps

After MongoDB is set up:

1. Make sure `server/.env` has correct MONGODB_URI
2. Start the application: `npm run dev`
3. The database and collections will be created automatically
4. Register your first user at http://localhost:3000

## Database Structure

The application will automatically create:
- Database: `fakenews_db`
- Collections:
  - `users` - User accounts
  - `analyses` - Analysis history

You can view these in MongoDB Compass or Atlas dashboard.
