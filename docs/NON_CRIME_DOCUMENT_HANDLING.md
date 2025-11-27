# Non-Crime Document Handling

## Overview

The AI Crime Evidence Organizer is designed to handle **both crime-related and non-crime documents**. The system automatically detects the document type and adjusts its processing accordingly.

## How It Works

### 1. **Document Classification**

The system uses BERT-based classification to identify document types:

- **Crime-related documents:**
  - `witness_statement` - Witness statements
  - `medical_report` - Medical examination reports
  - `fir` - First Information Report
  - `police_memo` - Police internal memos

- **General documents:**
  - `general_document` - Any non-crime document (project reports, articles, letters, invoices, etc.)

**Detection Logic:**
- The system checks for crime-related keywords (crime, suspect, victim, police, arrest, incident, etc.)
- If no crime keywords are found, it classifies as `general_document`
- BERT embeddings are used to match document content to category prompts

### 2. **Content Extraction**

**Works for ALL documents:**
- ✅ Text extraction (PDF, images via OCR)
- ✅ Named Entity Recognition (names, locations, organizations, dates)
- ✅ Timestamp extraction
- ✅ Timeline building (if dates/times are present)

### 3. **Missing Evidence Suggestions**

**For Crime Documents:**
- Suggests crime-specific evidence (CCTV, witness statements, medical reports, forensic reports, etc.)

**For Non-Crime Documents:**
- Provides generic feedback:
  - "Document processed successfully. All text and entities have been extracted."
  - Warns if no entities or timestamps are found
  - No crime-related suggestions

## Example: Project Report Processing

**Input:** A project report PDF (like your "Startup Pilot" document)

**Output:**
```
Classification: general_document (not "fir")

EXTRACTED CONTENT:
- All text from the document
- Entities: Names (Vedika Jaipurkar, Anshdeep Singh Bhandari, etc.)
- Locations: Nagpur, etc.
- Organizations: Shri Ramdeobaba College, etc.
- Dates: 2025-2026, etc.

MISSING EVIDENCE SUGGESTIONS:
- "Document processed successfully. All text and entities have been extracted."
- (No crime-related suggestions)
```

## Case ID Generation

**Note:** Case IDs are automatically generated for **all documents** (crime or non-crime). This is intentional and allows:
- Tracking multiple document uploads
- Organizing reports by case
- Maintaining a processing history

The Case ID is a unique identifier (hash) generated from the upload timestamp and file metadata. It doesn't imply the document is crime-related.

## Improvements Made

1. **Better Classification:**
   - Added crime keyword detection before BERT classification
   - Prefers `general_document` for non-crime content
   - Improved confidence scoring

2. **Context-Aware Suggestions:**
   - Only suggests crime evidence for crime documents
   - Provides helpful feedback for general documents

3. **Fallback Handling:**
   - All fallback classifications default to `general_document` (not `legal_document`)

## Testing

To test with a non-crime document:
1. Upload any PDF (project report, article, letter, invoice)
2. The system will:
   - Classify it as `general_document`
   - Extract all text and entities
   - Provide appropriate (non-crime) suggestions
   - Generate a case ID for tracking

## Summary

✅ **Works with any document type**
✅ **Automatically detects crime vs. non-crime**
✅ **Provides appropriate suggestions based on document type**
✅ **Case ID generation is universal (not crime-specific)**

