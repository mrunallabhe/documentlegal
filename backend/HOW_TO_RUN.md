# How to Run the AI Crime Evidence Organizer

## Prerequisites Check

Before running, make sure you have:

✅ Python packages installed: `pip install -r requirements.txt`  
✅ spaCy model downloaded: `python -m spacy download en_core_web_sm`  
✅ OpenAI API key added to `backend/.env`  
✅ Tesseract OCR installed (for text extraction)

## Step-by-Step: Running the Server

### Step 1: Navigate to Backend Directory

```bash
cd C:\Users\HP\OneDrive\Desktop\Project7Sem\backend
```

### Step 2: Activate Virtual Environment (if using one)

**If you created a virtual environment:**
```bash
.venv\Scripts\activate
```

**If not using virtual environment, skip this step.**

### Step 3: Start the FastAPI Server

```bash
uvicorn app.main:app --reload
```

**What you should see:**
```
INFO:     Will watch for changes
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 4: Verify Server is Running

Open your browser and go to:
- **API Documentation:** http://127.0.0.1:8000/docs
- **Alternative docs:** http://127.0.0.1:8000/redoc
- **Health check:** http://127.0.0.1:8000/ (if root endpoint exists)

You should see the FastAPI interactive documentation.

## Using the System

### Option 1: Using the Web Frontend

1. **Open the frontend:**
   - Navigate to: `C:\Users\HP\OneDrive\Desktop\Project7Sem\frontend\`
   - Open `index.html` in your web browser

2. **Upload Evidence:**
   - Click "Choose File" or drag and drop
   - Select an evidence file (image or PDF)
   - Click "Upload Evidence"

3. **Process Evidence:**
   - Copy the `case_id` from the upload response
   - Copy the `stored_path` 
   - Click "Process Evidence" button
   - Enter the `case_id` and `artifact_path` in the form
   - Click "Process"

4. **View Report:**
   - Click "Get Report" button
   - Enter the `case_id`
   - View the analysis results

### Option 2: Using API Directly (cURL/Postman)

#### Upload Evidence
```bash
curl -X POST "http://127.0.0.1:8000/evidence/upload" \
  -F "file=@path/to/your/evidence.pdf"
```

#### Process Evidence
```bash
curl -X POST "http://127.0.0.1:8000/evidence/process" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "your_case_id_here",
    "artifact_path": "storage/uploads/your_case_id_evidence.pdf"
  }'
```

#### Get Report
```bash
curl "http://127.0.0.1:8000/reports/your_case_id_here"
```

### Option 3: Using Python Script

Create a test script `test_upload.py`:

```python
import requests

# Upload file
with open("test_evidence.pdf", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/evidence/upload",
        files={"file": f}
    )
    result = response.json()
    print("Upload result:", result)
    case_id = result["case_id"]
    artifact_path = result["stored_path"]

# Process evidence
process_response = requests.post(
    "http://127.0.0.1:8000/evidence/process",
    json={
        "case_id": case_id,
        "artifact_path": artifact_path
    }
)
print("Process result:", process_response.json())

# Get report (wait a few seconds for processing)
import time
time.sleep(5)

report_response = requests.get(
    f"http://127.0.0.1:8000/reports/{case_id}"
)
print("Report:", report_response.json())
```

Run it:
```bash
python test_upload.py
```

## What Happens When You Process Evidence

1. **File Type Detection** - System identifies if it's an image or document
2. **Evidence Classification** - CLIP (images) or BERT (documents) classifies the evidence
3. **Content Extraction** - Extracts metadata, objects, text, entities
4. **Normalization** - Standardizes timestamps, locations, names
5. **Timeline Construction** - Builds chronological event timeline
6. **Inconsistency Detection** - Finds contradictions using rules + LLM
7. **Missing Evidence Suggestions** - Recommends additional evidence to collect
8. **Report Generation** - Creates JSON report with all findings

**First-time processing:** Models will download automatically (~600MB)

## Running in Background (Production)

### Using nohup (Linux/Mac)
```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

### Using Windows Service
Use NSSM (Non-Sucking Service Manager) or Task Scheduler

### Using Docker (Future)
```bash
docker build -t evidence-organizer .
docker run -p 8000:8000 evidence-organizer
```

## Stopping the Server

Press `CTRL+C` in the terminal where the server is running.

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Module Not Found Error
```bash
# Make sure you're in the backend directory
cd backend
# Install dependencies
pip install -r requirements.txt
```

### Models Not Loading
- Check internet connection (models download from Hugging Face)
- Check disk space (need ~1GB free)
- Check `.env` file has `EVIDENCE_ENABLE_REAL_AI=true`

### OpenAI API Errors
- Verify API key in `.env` file
- Check you have credits in OpenAI account
- Check internet connection

### Tesseract Not Found
- Install Tesseract OCR
- On Windows, may need to set path in environment variables

## Quick Command Reference

```bash
# Start server
cd backend
uvicorn app.main:app --reload

# Start on different port
uvicorn app.main:app --reload --port 8001

# Start without auto-reload (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Check if server is running
curl http://127.0.0.1:8000/docs
```

## Next Steps After Running

1. **Test with sample files:**
   - Upload a crime scene photo
   - Upload a witness statement PDF
   - Check the generated timeline

2. **Explore API documentation:**
   - Visit http://127.0.0.1:8000/docs
   - Try the interactive API endpoints

3. **Review generated reports:**
   - Check `backend/storage/reports/` directory
   - View JSON and PDF reports

4. **Customize for your needs:**
   - Adjust model parameters
   - Fine-tune on your data
   - Add custom entity types

