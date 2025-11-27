# Supported File Formats

## Input File Formats

The AI Crime Evidence Organizer supports the following file formats:

### ✅ Supported Formats

#### Images
- **.jpg / .jpeg** - JPEG images
- **.png** - PNG images
- **.bmp** - Bitmap images
- **.tiff** - TIFF images

**What the system extracts from images:**
- EXIF metadata (timestamp, GPS coordinates)
- OCR text (timestamps, locations, signs, license plates)
- Object detection (persons, vehicles, weapons, etc.)
- Classification (crime scene, CCTV, injury, weapon, environment)

#### Documents
- **.pdf** - PDF documents (both text-based and scanned)
- **.txt** - Plain text files

**What the system extracts from documents:**
- Full text content
- Named entities (names, locations, dates, organizations)
- Timestamps and dates
- Events and actions
- Classification (witness statement, medical report, FIR, police memo, legal document)

### ⚠️ Partially Supported

#### Documents (may need conversion)
- **.doc / .docx** - Microsoft Word documents
  - **Note:** Convert to PDF first for best results
  - You can use online converters or Microsoft Word to save as PDF

- **.xls / .xlsx** - Excel spreadsheets
  - **Note:** Convert to PDF first

### ❌ Not Currently Supported

- **.mp4 / .avi / .mov** - Video files (listed in allowed extensions but not fully processed)
- **.mp3 / .wav** - Audio files
- **.zip / .rar** - Archive files (upload individual files instead)

## File Size Recommendations

- **Images:** Up to 10MB recommended
- **PDFs:** Up to 50MB recommended
- **Text files:** No practical limit

## Best Practices

### For Best Results:

1. **PDFs:**
   - Use text-based PDFs (not scanned images) when possible
   - For scanned PDFs, ensure good image quality
   - Single-page or multi-page PDFs both work

2. **Images:**
   - Higher resolution = better OCR results
   - Clear, readable text in images
   - Good lighting/contrast for CCTV images
   - Include EXIF data if possible (for timestamps)

3. **Text Files:**
   - Use UTF-8 encoding
   - Plain text format works best

## How to Convert Files

### Word to PDF:
1. Open in Microsoft Word
2. File → Save As → PDF
3. Or use online converter: https://www.ilovepdf.com/word-to-pdf

### Excel to PDF:
1. Open in Microsoft Excel
2. File → Save As → PDF
3. Or use online converter

### Image Formats:
- Most image formats can be converted using:
  - Online: https://convertio.co/
  - Software: GIMP, Photoshop, Paint

## Example Input Files

### Recommended Test Files:

1. **Witness Statement:**
   - Format: `.pdf` or `.txt`
   - Content: Text document with names, dates, locations

2. **Medical Report:**
   - Format: `.pdf` or `.txt`
   - Content: Medical examination details

3. **CCTV Image:**
   - Format: `.jpg` or `.png`
   - Content: Image with timestamp overlay, location text

4. **Crime Scene Photo:**
   - Format: `.jpg` or `.png`
   - Content: Photo with EXIF metadata (timestamp, GPS)

5. **FIR Document:**
   - Format: `.pdf` or `.txt`
   - Content: Official police complaint

## Processing Details

### Image Processing:
1. File uploaded → File type detected
2. EXIF metadata extracted (timestamp, GPS)
3. OCR performed (text extraction)
4. Object detection (YOLO)
5. Classification (CLIP)
6. All data combined in report

### Document Processing:
1. File uploaded → File type detected
2. Text extracted (pdfplumber or Tesseract for scanned)
3. Named Entity Recognition (spaCy/BERT)
4. Time/date extraction
5. Event extraction
6. Classification (BERT)
7. All data combined in report

## Troubleshooting

### "File type not supported"
- Check file extension is in allowed list
- Convert to supported format if needed

### "Poor OCR results"
- Use higher resolution images
- Ensure text is clear and readable
- Check image quality

### "No text extracted from PDF"
- PDF might be scanned (image-based)
- System will use OCR automatically
- Ensure PDF pages are clear

### "No entities found"
- Document might be too short
- Ensure document contains names, locations, dates
- Check if text extraction worked

## Quick Reference

| Format | Supported | Best For | Notes |
|--------|-----------|----------|-------|
| .pdf | ✅ Yes | Documents | Text-based or scanned |
| .txt | ✅ Yes | Documents | Plain text |
| .jpg | ✅ Yes | Images | Photos, CCTV |
| .png | ✅ Yes | Images | Screenshots, diagrams |
| .bmp | ✅ Yes | Images | Bitmap images |
| .tiff | ✅ Yes | Images | High-quality images |
| .doc | ⚠️ Partial | Documents | Convert to PDF first |
| .docx | ⚠️ Partial | Documents | Convert to PDF first |
| .mp4 | ⚠️ Partial | Videos | Not fully processed yet |

## Summary

**Best Input Formats:**
- **Documents:** `.pdf` or `.txt`
- **Images:** `.jpg` or `.png`

**Always Supported:**
- PDF files (text or scanned)
- Text files
- Common image formats (JPG, PNG, BMP, TIFF)

**Convert First:**
- Word documents → PDF
- Excel files → PDF
- Other formats → PDF or supported image format

