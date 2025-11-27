# Troubleshooting 404 Errors

## Understanding the 404 Error

A 404 error means the server cannot find the requested resource. Here's how to debug it:

## Common Causes

### 1. Server Not Running
**Symptom:** All API calls return 404

**Solution:**
```bash
cd backend
uvicorn app.main:app --reload
```

Verify server is running:
- Open http://127.0.0.1:8000/health in browser
- Should return: `{"status": "ok"}`

### 2. Wrong API URL
**Symptom:** Frontend can't reach backend

**Check:**
- Frontend uses: `http://localhost:8000`
- Make sure server is running on port 8000
- If using different port, update `frontend/index.html` line 100:
  ```javascript
  const API = "http://localhost:8000"; // Change port if needed
  ```

### 3. CORS Issues
**Symptom:** Browser console shows CORS errors

**Solution:** Already configured in `main.py`, but verify:
- CORS middleware is enabled
- `allow_origins=["*"]` is set

### 4. Missing Endpoint
**Symptom:** Specific endpoint returns 404

**Available Endpoints:**
- `GET /` - Root endpoint (API info)
- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /evidence/upload` - Upload evidence
- `POST /evidence/process` - Process evidence
- `GET /reports/{case_id}` - Get report

## Debugging Steps

### Step 1: Check Server Status
```bash
# Test health endpoint
curl http://127.0.0.1:8000/health

# Or open in browser
# http://127.0.0.1:8000/health
```

### Step 2: Check API Documentation
Open in browser:
```
http://127.0.0.1:8000/docs
```

This shows all available endpoints and lets you test them.

### Step 3: Check Browser Console
1. Open browser Developer Tools (F12)
2. Go to "Network" tab
3. Try the action that causes 404
4. Look at the failed request:
   - What URL was requested?
   - What was the response status?
   - What was the response body?

### Step 4: Check Server Logs
Look at the terminal where uvicorn is running:
- Are there any error messages?
- Do you see the request being received?

## Common 404 Scenarios

### Scenario 1: Frontend Can't Find API
**Error:** `Failed to load resource: the server responded with a status of 404`

**Check:**
1. Is server running? → `http://127.0.0.1:8000/health`
2. Is API URL correct in frontend? → Check `index.html` line 100
3. Are you accessing from `file://` protocol? → Use a local web server

**Solution for file:// protocol:**
```bash
# Option 1: Use Python's HTTP server
cd frontend
python -m http.server 8080
# Then open: http://localhost:8080/index.html

# Option 2: Serve frontend through FastAPI
# (Add static file serving to main.py)
```

### Scenario 2: Report Not Found
**Error:** `GET /reports/{case_id}` returns 404

**Cause:** Report hasn't been generated yet

**Solution:**
1. Make sure you uploaded a file first
2. Make sure you processed the evidence
3. Wait a few seconds for processing to complete
4. Check if report file exists: `backend/storage/reports/{case_id}.json`

### Scenario 3: Artifact Not Found
**Error:** `POST /evidence/process` returns 404

**Cause:** File path is incorrect

**Solution:**
1. Check the `stored_path` from upload response
2. Make sure the path is correct (Windows paths use backslashes)
3. Verify file exists at that location

## Quick Fixes

### Fix 1: Add Root Endpoint
Already added in `main.py`:
```python
@app.get("/")
async def root():
    return {"message": "AI Crime Evidence Organizer API"}
```

### Fix 2: Serve Frontend from FastAPI
Add to `main.py`:
```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="../frontend"), name="static")
```

### Fix 3: Use Relative URLs
If serving frontend separately, make sure API URL is correct.

## Testing Endpoints

### Test with curl:
```bash
# Health check
curl http://127.0.0.1:8000/health

# Root endpoint
curl http://127.0.0.1:8000/

# Upload (replace with actual file)
curl -X POST http://127.0.0.1:8000/evidence/upload -F "file=@test.pdf"
```

### Test with Browser:
1. Open http://127.0.0.1:8000/docs
2. Use interactive API documentation
3. Test each endpoint directly

## Windows-Specific Issues

### KeyboardInterrupt in Uvicorn Reloader

**Symptom:** You see errors like:
```
Process SpawnProcess-6:
Traceback (most recent call last):
  ...
KeyboardInterrupt
```

**Cause:** This is a known Windows issue with uvicorn's `--reload` feature. When you stop the server (CTRL+C), the reloader subprocess gets interrupted and shows this error.

**Solution:**
1. **Use the non-reload version (Recommended for Windows):**
   ```bash
   # Use run_server.bat (without --reload)
   cd backend
   run_server.bat
   
   # Or manually:
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

2. **The error is harmless** - Your server still works fine, it's just a subprocess cleanup issue.

3. **For development with auto-reload:**
   - Use `run_server_reload.bat` if you need auto-reload
   - The KeyboardInterrupt errors are expected and can be ignored
   - Server functionality is not affected

**Note:** The error only appears when stopping the server, not during normal operation.

## Still Getting 404?

1. **Check server logs** - Look for error messages
2. **Check browser console** - Look for specific error details
3. **Verify endpoint exists** - Check http://127.0.0.1:8000/docs
4. **Check file paths** - Make sure all paths are correct
5. **Restart server** - Sometimes a restart fixes issues

## Need More Help?

- Check server is running: `http://127.0.0.1:8000/health`
- Check API docs: `http://127.0.0.1:8000/docs`
- Verify frontend API URL matches server URL
- Check browser console for detailed error messages

