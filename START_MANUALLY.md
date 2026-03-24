# 🚀 Manual Start Guide - WORKING METHOD

## ✅ Issue Fixed

Added configuration to `client/.env` to fix the React dev server error.

## 🎯 Start Services Manually (Recommended)

Open **3 separate terminals** and run these commands:

### Terminal 1: AI API
```bash
cd ai_model
python app.py
```
✅ Wait for: `[OK] Model loaded successfully (99.11% accuracy)`

---

### Terminal 2: Backend
```bash
cd server
node server.js
```
✅ Wait for: `Server running on port 5000`

---

### Terminal 3: Frontend
```bash
cd client
npm start
```
✅ Wait for: `Compiled successfully!`

---

## 🌐 Open Browser

Once all 3 are running, open:
```
http://localhost:3000
```

## 🎨 What You'll See

Your beautiful newspaper-themed landing page with:
- Vintage beige newspaper background
- Dark blue presentation box
- "FAKE NEWS DETECTION" title
- "AI based Multilingual Fake news detection" subtitle
- Newspaper-style quote cards
- Orange and beige buttons

## ⚠️ Important Notes

1. **Start in order**: AI API → Backend → Frontend
2. **Wait for each** to fully start before starting the next
3. **Don't use** `npm run dev` - it has issues with the concurrent setup
4. **Use 3 separate terminals** instead

## 🔧 If Frontend Still Won't Start

Try this:

```bash
cd client
npm install
set DANGEROUSLY_DISABLE_HOST_CHECK=true
npm start
```

Or on PowerShell:
```powershell
cd client
npm install
$env:DANGEROUSLY_DISABLE_HOST_CHECK="true"
npm start
```

## ✅ Success Checklist

- [ ] Terminal 1 shows: `Running on http://127.0.0.1:5001`
- [ ] Terminal 2 shows: `Server running on port 5000`
- [ ] Terminal 3 shows: `Compiled successfully!`
- [ ] Browser opens to `http://localhost:3000`
- [ ] You see the newspaper-themed landing page

## 🎉 Ready!

All services should now be running properly!
