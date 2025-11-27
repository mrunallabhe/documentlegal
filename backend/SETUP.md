# Quick Setup Guide

## 1. Install Dependencies

### Python Packages
```bash
cd backend
pip install -r requirements.txt
```

### System Dependencies

**Tesseract OCR:**
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`

**Poppler (for PDF OCR):**
- Windows: https://github.com/oschwartz10612/poppler-windows/releases
- Linux: `sudo apt-get install poppler-utils`
- macOS: `brew install poppler`

**spaCy Model:**
```bash
python -m spacy download en_core_web_sm
```

## 2. Configure Environment

Copy `env.example` to `.env`:
```bash
cp env.example .env
```

Edit `.env` and set your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
EVIDENCE_ENABLE_REAL_AI=true
```

## 3. Run the Server

```bash
uvicorn app.main:app --reload
```

## 4. Test the API

Open `frontend/index.html` in your browser and upload a test file.

## Models

Models download automatically on first use:
- CLIP: ~150MB
- BERT: ~440MB  
- YOLO: ~6MB

Total: ~600MB download on first run.

## Troubleshooting

**CUDA out of memory?** Set `EVIDENCE_DEVICE=cpu` in `.env`

**Tesseract not found?** Install Tesseract (see above)

**OpenAI errors?** Check your API key in `.env`

For detailed implementation guide, see `docs/IMPLEMENTATION_GUIDE.md`

