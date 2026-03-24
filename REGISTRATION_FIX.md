# 🔧 Registration Error - Troubleshooting Guide

## Common Causes

1. **MongoDB not running**
2. **Network/connection issue**
3. **Validation error**
4. **Duplicate email**

## ✅ Quick Fixes

### Fix 1: Check MongoDB is Running

```bash
# Windows - Check if MongoDB service is running
net start | findstr MongoDB

# If not running, start it:
net start MongoDB
```

### Fix 2: Check Backend Terminal

Look at your backend terminal (Terminal 2) for error messages. You should see:
```
✅ MongoDB connected successfully
```

If you see connection errors, MongoDB isn't running.

### Fix 3: Check Browser Console

1. Open browser DevTools (F12)
2. Go to Console tab
3. Try registering again
4. Look for error messages

Common errors:
- `Network Error` - Backend not running
- `400 Bad Request` - Validation error (check password length, email format)
- `500 Internal Server Error` - MongoDB connection issue

### Fix 4: Test with Simple Data

Try registering with:
- **Name**: Test User
- **Email**: test@example.com
- **Password**: 123456 (minimum 6 characters)

### Fix 5: Check if Email Already Exists

If you've registered before with the same email, you'll get an error. Try a different email.

## 🔍 Detailed Troubleshooting

### Step 1: Verify All Services Running

```bash
# Check ports
netstat -ano | findstr "3000 5000 5001"
```

Should show all 3 ports.

### Step 2: Test Backend Directly

Open browser or Postman and test:
```
POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
  "name": "Test User",
  "email": "test@example.com",
  "password": "123456"
}
```

### Step 3: Check MongoDB Connection

In your backend terminal, you should see:
```
✅ MongoDB connected successfully
```

If you see:
```
❌ MongoDB connection error
```

Then MongoDB isn't running. Start it:
```bash
net start MongoDB
```

### Step 4: Restart Backend

If MongoDB was stopped and you just started it:

1. Stop backend (Ctrl+C in Terminal 2)
2. Start it again:
```bash
cd server
node server.js
```
3. Wait for "MongoDB connected successfully"
4. Try registering again

## 📝 Validation Rules

Make sure your registration data meets these requirements:

- **Name**: Not empty
- **Email**: Valid email format (user@domain.com)
- **Password**: At least 6 characters

## 🎯 Most Common Issue: MongoDB Not Running

**Solution:**
```bash
# Start MongoDB service
net start MongoDB

# Then restart your backend
cd server
node server.js
```

## ✅ Success Indicators

When registration works, you should see:
1. Toast notification: "Registration successful!"
2. Automatic redirect to dashboard/text-detection page
3. Your name appears in the navbar

## 🆘 Still Not Working?

### Check Backend Logs

In Terminal 2 (backend), look for:
```
Register error: [error details]
```

### Check Frontend Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Try registering
4. Click on the `/register` request
5. Check Response tab for error details

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "User already exists" | Email already registered | Use different email |
| "Password must be at least 6 characters" | Password too short | Use 6+ characters |
| "Valid email is required" | Invalid email format | Check email format |
| "Server error during registration" | MongoDB issue | Start MongoDB |
| "Network Error" | Backend not running | Start backend |

## 🚀 Quick Test

1. **Start MongoDB**: `net start MongoDB`
2. **Restart Backend**: 
   ```bash
   cd server
   node server.js
   ```
3. **Wait for**: "MongoDB connected successfully"
4. **Try registering** with:
   - Name: Test
   - Email: test123@test.com
   - Password: test123

If this works, your system is fine and the previous error was likely due to:
- MongoDB not running
- Duplicate email
- Validation error

## 📞 Need More Help?

Share the exact error message from:
1. Browser console (F12 → Console)
2. Backend terminal
3. Network tab (F12 → Network → /register request → Response)

This will help identify the exact issue!
