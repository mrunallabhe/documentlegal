# How to Verify OpenAI is Actually Being Used

## Quick Check

1. **Check your `.env` file:**
   ```bash
   cd backend
   # Make sure you have a .env file (copy from env.example if needed)
   # Check that it contains:
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Check server logs when processing:**
   When you upload a file, you should see:
   ```
   [Reasoning] Using OpenAI LLM for inconsistency detection...
   🤖 Calling OpenAI API with model: gpt-4o-mini
   ✅ OpenAI API response received (XXX chars)
   ```

3. **If you see warnings instead:**
   ```
   ⚠️ LLM reasoning unavailable: OPENAI_API_KEY not set in .env file.
   [Reasoning] ⚠️ OpenAI LLM not available - using rule-based only
   ```
   This means OpenAI is NOT being used - you're getting rule-based results only.

## How to Set Up OpenAI

1. **Get an API key:**
   - Go to: https://platform.openai.com/api-keys
   - Create a new API key
   - Copy it (starts with `sk-`)

2. **Add to `.env` file:**
   ```bash
   cd backend
   # Create .env file if it doesn't exist
   # Add this line:
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. **Restart the server:**
   ```bash
   # Stop server (Ctrl+C)
   # Restart:
   cd backend
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

## What Each Model Does

### ✅ CLIP (Image Classification)
- **Status:** Always used if `enable_real_ai=true`
- **What it does:** Classifies images (crime_scene, CCTV, injury, weapon, environment)
- **No API key needed** - downloads from Hugging Face

### ✅ BERT (Document Classification & NER)
- **Status:** Always used if `enable_real_ai=true`
- **What it does:** 
  - Classifies documents (witness_statement, medical_report, fir, police_memo, general_document)
  - Extracts entities (names, locations, dates, organizations)
- **No API key needed** - downloads from Hugging Face

### ✅ YOLO (Object Detection)
- **Status:** Always used if `enable_real_ai=true`
- **What it does:** Detects objects in images (person, car, weapon, etc.)
- **No API key needed** - downloads from Ultralytics

### ⚠️ OpenAI GPT (LLM Reasoning)
- **Status:** Only used if `OPENAI_API_KEY` is set
- **What it does:**
  - Advanced inconsistency detection (beyond simple rules)
  - Missing evidence suggestions (context-aware)
- **Requires API key** - costs money (pay-per-use)

## Current Status Check

Run this to check your setup:
```python
from app.config import settings
print(f"enable_real_ai: {settings.enable_real_ai}")
print(f"openai_api_key set: {bool(settings.openai_api_key and settings.openai_api_key != '' and settings.openai_api_key != 'your_openai_api_key_here')}")
print(f"openai_model: {settings.openai_model}")
```

## What You're Getting Without OpenAI

If OpenAI is not configured, you still get:
- ✅ CLIP image classification
- ✅ BERT document classification
- ✅ BERT entity extraction
- ✅ YOLO object detection
- ✅ Rule-based inconsistency detection (time conflicts, location conflicts)
- ❌ **NO** advanced LLM-based inconsistency detection
- ❌ **NO** context-aware missing evidence suggestions

## Testing OpenAI Integration

1. **Upload a file**
2. **Check server logs** - you should see:
   ```
   [Reasoning] Using OpenAI LLM for inconsistency detection...
   🤖 Calling OpenAI API with model: gpt-4o-mini
   ✅ OpenAI API response received
   ```
3. **Check the report** - inconsistencies and missing evidence should be more detailed and context-aware

## Troubleshooting

### "OPENAI_API_KEY not set"
- Check `.env` file exists in `backend/` directory
- Check the key is on one line: `OPENAI_API_KEY=sk-...`
- Restart server after changing `.env`

### "LLM reasoning error: ..."
- Check your API key is valid
- Check you have credits in your OpenAI account
- Check internet connection
- Check the error message for details

### Still seeing same results for all files?
- Check server logs for the 🤖 emoji (means OpenAI is being called)
- If you don't see it, OpenAI is not being used
- Verify `.env` file is in the correct location (`backend/.env`)

