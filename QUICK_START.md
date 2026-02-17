# 🚀 Quick Start Guide - AI-NutriCare Server

## ✅ Server is Running!

### Access Your Server NOW:

**Copy and paste this URL into your browser:**
```
http://localhost:8000/docs
```

This will open the **interactive API documentation** where you can test everything!

---

## 📋 Quick Reference

### Main URLs:
- **API Docs:** http://localhost:8000/docs ⭐ (Start here!)
- **Health Check:** http://localhost:8000/health
- **API Root:** http://localhost:8000

### If Port 8000 Doesn't Work, Try:
- http://localhost:8001/docs
- http://localhost:8001/health

---

## ⚠️ IMPORTANT: Use `localhost`, NOT `0.0.0.0`

**❌ WRONG:** `http://0.0.0.0:8000`  
**✅ CORRECT:** `http://localhost:8000`

---

## 🧪 Test the Server (30 seconds)

1. **Open your browser**
2. **Go to:** http://localhost:8000/health
3. **You should see:**
   ```json
   {
     "status": "healthy",
     "service": "AI-NutriCare"
   }
   ```

If you see this, **your server is working perfectly!** ✅

---

## 📚 Explore the API

1. Go to: **http://localhost:8000/docs**
2. You'll see all available endpoints
3. Click on any endpoint to expand it
4. Click "Try it out" to test it
5. Click "Execute" to send a request

### Try This:
1. Find `POST /api/upload-report`
2. Click "Try it out"
3. Click "Choose File"
4. Select `tests/test_data/sample_medical_report.txt`
5. Click "Execute"
6. See the extracted medical data!

---

## 🔄 If Server is Not Running

### Start It:
```bash
cd backend
python run_server.py
```

Then go to: **http://localhost:8000/docs**

---

**That's it! Your server is ready to use!** 🎉
