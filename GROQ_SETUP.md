# Using Groq (FREE) Instead of OpenAI

Groq provides FREE, ultra-fast AI inference using their LPU (Language Processing Unit) technology. It's perfect for this project!

## Why Groq?

- ✅ **100% FREE** - No credit card required
- ✅ **Super Fast** - Up to 10x faster than OpenAI
- ✅ **High Quality** - Uses Llama 3.3 70B model
- ✅ **Generous Limits** - 30 requests/minute free tier
- ✅ **Easy Setup** - Just get an API key

## Quick Setup (3 Steps)

### Step 1: Get Your FREE Groq API Key

1. Go to: https://console.groq.com/keys
2. Sign up with Google/GitHub (takes 30 seconds)
3. Click "Create API Key"
4. Copy your key (starts with `gsk_`)

### Step 2: Install Groq Library

```powershell
pip install groq
```

### Step 3: Add Key to .env File

Open your `.env` file and add:

```env
GROQ_API_KEY=gsk_your-actual-key-here
NUTRICARE_NLP_MODEL=groq
```

That's it! You're done! 🎉

## Complete .env File Example

```env
# Use Groq (FREE)
GROQ_API_KEY=gsk_abc123xyz...
NUTRICARE_NLP_MODEL=groq

# USDA API Key (also FREE)
USDA_API_KEY=your-usda-key-here

# Encryption Key (generate with command below)
NUTRICARE_ENCRYPTION_KEY=a1b2c3d4e5f6...
```

### Generate Encryption Key:

```powershell
python -c "import secrets; print(secrets.token_hex(16))"
```

## Get USDA API Key (Also FREE)

1. Go to: https://fdc.nal.usda.gov/api-key-signup.html
2. Fill out the form
3. Check your email for the key
4. Add to `.env` file

## Test It Works

After setting up your keys, test the system:

```powershell
python -c "from ai_diet_planner.nlp import NLPTextInterpreter; print('Groq setup successful!')"
```

## Run the Application

```powershell
streamlit run ai_diet_planner\ui\app.py
```

## Groq vs OpenAI Comparison

| Feature | Groq (FREE) | OpenAI (PAID) |
|---------|-------------|---------------|
| Cost | $0 | ~$0.01-0.05 per report |
| Speed | Ultra-fast (10x) | Fast |
| Quality | Excellent (Llama 3.3 70B) | Excellent (GPT-4) |
| Rate Limit | 30 req/min | Depends on tier |
| Setup | Easy | Easy |

## Troubleshooting

### "groq module not found"

```powershell
pip install groq
```

### "Invalid API key"

- Make sure your key starts with `gsk_`
- Check for extra spaces in `.env` file
- Regenerate key at https://console.groq.com/keys

### "Rate limit exceeded"

Groq free tier: 30 requests/minute. Wait a minute and try again.

## Advanced: Switch Between Models

You can easily switch between different models by changing the `.env` file:

```env
# Use Groq (FREE and FAST)
NUTRICARE_NLP_MODEL=groq
GROQ_API_KEY=gsk_...

# Or use OpenAI GPT-4 (PAID)
# NUTRICARE_NLP_MODEL=gpt-4
# OPENAI_API_KEY=sk-...

# Or use OpenAI GPT-3.5 (CHEAPER)
# NUTRICARE_NLP_MODEL=gpt-3.5-turbo
# OPENAI_API_KEY=sk-...

# Or use BERT (FREE, OFFLINE, but less accurate)
# NUTRICARE_NLP_MODEL=bert
```

## Need Help?

- Groq Documentation: https://console.groq.com/docs
- Groq Discord: https://discord.gg/groq
- This Project: See TROUBLESHOOTING.md

---

**Recommendation:** Start with Groq! It's free, fast, and works great for this medical report analysis use case.
