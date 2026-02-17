# ✅ How to Access the AI-NutriCare Server

## ⚠️ IMPORTANT: Use `localhost` NOT `0.0.0.0`

The server binds to `0.0.0.0` (all network interfaces), but you must access it using:
- ✅ **localhost** or
- ✅ **127.0.0.1**

**DO NOT USE:** `http://0.0.0.0:8000` ❌  
**USE INSTEAD:** `http://localhost:8000` ✅

---

## 🚀 Quick Access URLs

### Port 8000 (Primary):
- **API Root:** http://localhost:8000
- **Health Check:** http://localhost:8000/health ✅ (Working)
- **API Documentation (Swagger UI):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc

### Port 8001 (If port 8000 is busy):
- **API Root:** http://localhost:8001
- **Health Check:** http://localhost:8001/health
- **API Documentation:** http://localhost:8001/docs

---

## ✅ Correct URLs to Use:

### ✅ CORRECT:
```
http://localhost:8000
http://127.0.0.1:8000
http://localhost:8000/health
http://localhost:8000/docs
```

### ❌ WRONG (Won't Work):
```
http://0.0.0.0:8000      ❌ ERR_ADDRESS_INVALID
http://0.0.0.0:8001      ❌ ERR_ADDRESS_INVALID
```

---

## 🔍 Check Which Port is Running

### Method 1: Check in Browser
Try both ports:
1. http://localhost:8000/health
2. http://localhost:8001/health

Whichever one shows `{"status": "healthy", "service": "AI-NutriCare"}` is the correct one.

### Method 2: Check in Terminal
```powershell
netstat -ano | findstr :8000
netstat -ano | findstr :8001
```

If you see `LISTENING`, that port is active.

---

## 🧪 Quick Test

### Test Port 8000:
Open your browser and go to:
```
http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "AI-NutriCare"
}
```

### Test Port 8001 (if 8000 doesn't work):
```
http://localhost:8001/health
```

---

## 📖 Access API Documentation

### Swagger UI (Interactive):
```
http://localhost:8000/docs
```

This opens an interactive API documentation where you can:
- See all endpoints
- Test API calls directly
- Upload files
- View responses

### ReDoc (Alternative):
```
http://localhost:8000/redoc
```

---

## 🔧 If Server is Not Running

### Start the Server:
```bash
cd backend
python run_server.py
```

The server will show:
```
============================================================
AI-NutriCare API Server
============================================================

Starting server on port 8000...

✅ Server URLs (USE THESE IN YOUR BROWSER):
   API Root:         http://localhost:8000
   Health Check:     http://localhost:8000/health
   API Docs (Swagger): http://localhost:8000/docs
   API Docs (ReDoc):   http://localhost:8000/redoc

⚠️  IMPORTANT: Use 'localhost' or '127.0.0.1', NOT '0.0.0.0'
```

### Or use the batch file:
Double-click: `backend/start.bat`

---

## 📝 Common Issues & Solutions

### Issue: ERR_ADDRESS_INVALID

**Problem:** Trying to access `http://0.0.0.0:8000`  
**Solution:** Use `http://localhost:8000` instead

### Issue: Connection Refused

**Problem:** Server is not running  
**Solution:** Start the server first:
```bash
cd backend
python run_server.py
```

### Issue: Page Won't Load

**Possible Causes:**
1. Server is not running - Start it first
2. Wrong port - Check which port is active (8000 or 8001)
3. Firewall blocking - Check Windows Firewall settings
4. Wrong URL - Make sure you're using `localhost`, not `0.0.0.0`

---

## ✅ Verification

**Current Status:**
- ✅ Port 8000: **RUNNING** and responding
- ✅ Health check: **WORKING** (Status 200)
- ✅ Server is accessible at `http://localhost:8000`

**Test it now:**
1. Open your browser
2. Go to: **http://localhost:8000/health**
3. You should see: `{"status": "healthy", "service": "AI-NutriCare"}`

---

## 🎯 Summary

**Use these URLs in your browser:**
- ✅ http://localhost:8000
- ✅ http://localhost:8000/docs
- ✅ http://localhost:8000/health

**Don't use:**
- ❌ http://0.0.0.0:8000 (won't work in browser)

**Why?**
- `0.0.0.0` is a bind address for the server (means "listen on all interfaces")
- Browsers need a specific address like `localhost` or `127.0.0.1` to connect

---

**Your server is running! Just use the correct URL: `http://localhost:8000`** ✅
