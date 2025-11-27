# Complete Testing Guide

## Quick Start Testing

### Step 1: Create PDFs (Optional)
```bash
cd test_data
pip install reportlab
python create_test_pdfs.py
```

### Step 2: Start Server
```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Step 3: Test with Sample Files

#### Test Case 1: Single Document
1. Upload `sample_witness_statement.pdf`
2. Process it
3. Check report for:
   - Extracted text
   - Entities (Vikas Sharma, MG Road, etc.)
   - Timeline events
   - Timestamps extracted

#### Test Case 2: Multiple Documents (Full Case)
1. Upload all 4 PDFs:
   - `sample_witness_statement.pdf`
   - `sample_medical_report.pdf`
   - `sample_fir.pdf`
   - `sample_police_memo.pdf`
2. Process each one (use same case_id or different)
3. Get report to see:
   - All extracted content
   - Timeline from all documents
   - Inconsistencies detected:
     - Time conflict (8:15 PM vs 8:25 PM)
     - Injury severity conflict (minor vs deep laceration)
     - Clothing description conflict (black vs white shirt)
   - Missing evidence suggestions

## Expected Results

### Entity Extraction
- **Names:** Vikas Sharma, Rajesh Kumar, Ramesh Patel, Anil Singh, Mohan Das, Dr. Priya Menon
- **Locations:** MG Road, Bangalore, ABC Supermarket, Park Street, City General Hospital
- **Organizations:** ABC Supermarket, City General Hospital, Central Police Station

### Timeline Events
1. 8:12 PM - Suspect enters shop (CCTV/Witness)
2. 8:15 PM - Argument heard (Witness)
3. 8:25 PM - Altercation (CCTV)
4. 8:30 PM - Suspect exits (Witness/CCTV)
5. 8:35 PM - Police called (Witness/FIR)
6. 9:00 PM - Police arrive (Witness/FIR)
7. 10:30 PM - Medical examination (Medical Report)

### Inconsistencies
1. **Time Conflict:** 
   - Witness: Argument at 8:15 PM
   - CCTV: Altercation at 8:25 PM
   - **Type:** time_conflict

2. **Injury Severity:**
   - Witness: "minor injury" / "small cut"
   - Medical: "deep laceration" / "compound fracture"
   - **Type:** statement_vs_medical

3. **Clothing Description:**
   - FIR: Suspect wore black shirt
   - Witness: Exited in white shirt
   - **Type:** description_conflict

### Missing Evidence Suggestions
- Forensic report
- CCTV from neighboring shops
- Additional witness statements
- Phone records
- Crime scene photographs

## Testing Checklist

- [ ] Upload text file → Check text extraction
- [ ] Upload PDF → Check text extraction
- [ ] Process document → Check entity extraction
- [ ] Process multiple documents → Check timeline
- [ ] Check inconsistencies detected
- [ ] Check missing evidence suggestions
- [ ] Verify report formatting
- [ ] Test with image file (if available)
- [ ] Check OCR text extraction (if image has text)

## Troubleshooting

### No Text Extracted
- Check if file is scanned PDF (needs OCR)
- Verify pdfplumber is working
- Check file encoding

### No Entities Found
- Verify spaCy model is installed
- Check if text is long enough
- Ensure proper NER model loaded

### No Inconsistencies Detected
- Make sure multiple documents processed
- Check if documents have conflicting information
- Verify reasoning service is working

### Missing Evidence Not Suggested
- Check if OpenAI API key is set
- Verify LLM reasoning is enabled
- Check if enough evidence is present

## Advanced Testing

### Test with Real Images
1. Create image with text overlay (CCTV style)
2. Upload and process
3. Check OCR text extraction
4. Verify object detection (if YOLO working)

### Test Timeline Accuracy
- Upload documents with different timestamps
- Verify chronological ordering
- Check time normalization

### Test Entity Linking
- Upload multiple documents mentioning same person
- Check if entities are linked/canonicalized

## Success Criteria

✅ Text extracted from all documents  
✅ Entities correctly identified  
✅ Timeline built chronologically  
✅ Inconsistencies detected  
✅ Missing evidence suggested  
✅ Report formatted clearly  
✅ All features working end-to-end

