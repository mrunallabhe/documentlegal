# Quick Start - Essential Steps

Follow these steps in order to get your AI Crime Evidence Organizer running:

## ✅ Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Expected time:** 5-10 minutes (depends on internet speed)

## ✅ Step 2: Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

**Expected time:** 1-2 minutes

## ✅ Step 3: Configure Environment Variables

1. Open `backend/.env` file in a text editor
2. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
3. Make sure `EVIDENCE_ENABLE_REAL_AI=true` is set
4. Save the file

**Get API key:** https://platform.openai.com/api-keys

## ✅ Step 4: Install System Dependencies (Required for OCR)

### Windows:

**Tesseract OCR:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (default location: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or note the installation path

**Poppler (for PDF OCR):**
1. Download from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\poppler` (or any location)
3. Add `C:\poppler\Library\bin` to your system PATH

**python-magic (for file type detection):**
```bash
pip install python-magic-bin
```

### Linux:
```bash
sudo apt-get install tesseract-ocr poppler-utils libmagic1
```

### macOS:
```bash
brew install tesseract poppler libmagic
```

## ✅ Step 5: Verify Installation

Test that everything is installed:

```bash
# Test Python packages
python -c "import torch, transformers, spacy; print('✅ Python packages OK')"

# Test spaCy model
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ spaCy model OK')"

# Test Tesseract
python -c "import pytesseract; print('✅ Tesseract:', pytesseract.get_tesseract_version())"
```

## ✅ Step 6: Run the Server

```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## ✅ Step 7: Test the System

1. Open `frontend/index.html` in your browser
2. Upload a test file (image or PDF)
3. Click "Process Evidence"
4. Check the report

## 🎯 What Happens on First Run

When you process your first evidence file:
- **CLIP model** downloads (~150MB) - for image classification
- **BERT model** downloads (~440MB) - for document classification
- **YOLO model** downloads (~6MB) - for object detection
- Total: ~600MB download (one-time)

## ⚠️ Troubleshooting

### "Tesseract not found"
- Install Tesseract (see Step 4)
- On Windows, you may need to set path in code or environment variable

### "CUDA out of memory"
- Set `EVIDENCE_DEVICE=cpu` in `.env` file
- Restart server

### "OpenAI API error"
- Check your API key in `.env`
- Verify you have credits in your OpenAI account
- Check internet connection

### "spaCy model not found"
- Run: `python -m spacy download en_core_web_sm`
- Make sure you're using the same Python environment

### "Module not found"
- Make sure you're in the `backend` directory
- Activate virtual environment if using one
- Run: `pip install -r requirements.txt`

## 🚀 Next Steps After Setup

1. **Test with sample evidence:**
   - Upload a crime scene photo
   - Upload a witness statement PDF
   - Check the generated timeline and inconsistencies

2. **Customize models:**
   - Fine-tune on your specific case types
   - Adjust confidence thresholds
   - Add custom entity types

3. **Deploy to production:**
   - Set up proper database (PostgreSQL)
   - Configure object storage (S3/Azure Blob)
   - Add authentication and security
   - Set up monitoring

## 📚 Documentation

- **Full Setup Guide:** `SETUP.md`
- **Implementation Guide:** `../docs/IMPLEMENTATION_GUIDE.md`
- **Model Details:** `../docs/MODEL_IMPLEMENTATION_SUMMARY.md`
- **Architecture:** `../docs/architecture.md`

