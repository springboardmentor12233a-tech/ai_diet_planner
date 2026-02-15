# Quick Fix: "No module named 'ai_diet_planner'" Error

## The Problem

You're seeing this error when uploading a file:
```
An error occurred: No module named 'ai_diet_planner'
```

## The Solution (3 Easy Steps)

### Step 1: Stop the Streamlit App

Press `Ctrl+C` in the terminal where Streamlit is running.

### Step 2: Install the Package

**Windows:**
```cmd
install_package.bat
```

**Linux/Mac:**
```bash
chmod +x install_package.sh
./install_package.sh
```

**Or manually:**
```bash
pip install -e .
```

### Step 3: Restart the App

**Windows:**
```cmd
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

**Or manually:**
```bash
streamlit run ai_diet_planner/ui/app.py
```

## Verify It Worked

After restarting, try uploading a file again. The error should be gone!

## Still Not Working?

See `TROUBLESHOOTING.md` for more detailed help.

---

**Why did this happen?**

The `ai_diet_planner` package needs to be installed in "development mode" so Python can find all the modules. The command `pip install -e .` does this by creating a link to your code directory.
