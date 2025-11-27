## AI Crime Evidence Organizer – Seminar-Ready Methodology

### 1. Problem Statement
- Evidence in modern cases spans photos, CCTV frames, medical scans, PDF statements, and handwritten notes. Every source has unique metadata, formats, and reliability levels.
- Manual collation creates latency and blind spots: cross-team updates lag, contradictory testimony is discovered late, and investigators struggle to maintain a single source of truth.
- Proposed system delivers an automated ingestion-to-report pipeline that enforces structure, improves discovery, and gives legal teams a defensible, auditable narrative.

### 2. Project Objectives
- Auto-classify mixed evidence and attach trust/confidence scores.
- Extract machine-readable text, entities, and contextual metadata from both visual and textual sources.
- Align events on a canonical timeline, flag contradictions, and infer missing artifacts.
- Produce a dashboard/PDF dossier with drill-down links and JSON APIs for case-management integration.
- Reduce manual preprocessing workload by ≥70% while improving transparency and audit readiness.

### 3. System Overview (High-Level Flow)
1. Folder upload via React/HTML → FastAPI backend receives ZIP and registers case ID.
2. File-type detector validates extensions, mime types, and magic bytes; suspicious files quarantined.
3. Evidence classification splits the stream into vision and textual branches.
4. Content extraction modules (OCR, NER, object detection) generate structured feature sets.
5. Normalization service reconciles timestamps, aliases, and geocodes.
6. Timeline builder merges all events into a chronological knowledge graph.
7. Inconsistency engine performs rule-based + LLM reasoning to raise alerts.
8. Missing-evidence recommender inspects coverage gaps.
9. Reporting service renders dashboard widgets, PDF summaries, and JSON exports.

### 4. Detailed Methodology

#### Step 1 – Data Input & Chain of Custody
- React drop zone uploads an encrypted ZIP; FastAPI unpacks into case-specific storage (Azure Blob/S3).
- SHA-256 checksums recorded in PostgreSQL to guarantee integrity; audit trail tracks user, timestamp, IP.
- Optional evidence tagging UI lets officers annotate context (location, officer ID) during upload.

#### Step 2 – File Type Identification
- `python-magic`, `mimetypes`, and header fingerprints classify image/video/document/audio types.
- Validation rules: mismatched extension vs magic byte → flag for manual review.
- Output schema: `{file_id, original_name, detected_type, size_bytes, hash, status}`.

#### Step 3 – Evidence Classification
**A. Vision Branch**
- Pre-processing: EXIF scrub (with secure copy), resolution normalization, color correction for low-light CCTV.
- CLIP embeddings compared against labeled vectors (crime scene, CCTV, injury, weapon, environment).
- MobileNet/ResNet fine-tuned on curated crime datasets supply probabilistic labels.
- YOLOv8/SSD object detection enumerates salient objects (weapons, vehicles, blood pools, number plates).

**B. Document/Text Branch**
- pdfplumber/Textract pull raw text layers; Tesseract handles scanned images.
- SentenceTransformer + BERT/RoBERTa classifier assigns categories (witness statement, FIR, medical, memo).
- GPT-based zero-shot classifier backs up ambiguous cases and emits rationale strings for audits.

#### Step 4 – Content Extraction
**Images**
- EXIF parser captures timestamp, GPS, camera info; stores both original and normalized values.
- OCR identifies timestamps on CCTV overlays or signage; OpenCV detects region-of-interest before Tesseract.
- Object detection results stored as bounding boxes with class, confidence, pixel coordinates.

**Documents**
- NER stack (spaCy `en_core_lg` + fine-tuned BERT) extracts PERSON, ORG, LOCATION, DATE, TIME, INJURY.
- Dependency parsing helps capture actions (“suspect entered store”, “victim sustained fracture”).
- Medical reports mapped to an injury ontology (minor abrasion, deep laceration, fracture).
- All findings serialized into a knowledge graph node per evidence item.

#### Step 5 – Data Normalization
- Time harmonization: convert all timestamps to UTC, maintain source timezone, mark confidence levels (exact, inferred, approximate).
- Location normalization via geocoding API + alias dictionary (e.g., “MG Road” → “Mahatma Gandhi Road, Bengaluru”).
- Name canonicalization: fuzzy matching (Levenshtein + embeddings) clusters aliases (“Sharma Ji” vs “Vikas Sharma”).
- Units normalization (e.g., “9 pm”, “21:00 hrs”) and measurement alignment (cm vs inches in medical notes).

#### Step 6 – Timeline Construction
- Events stored as `{event_id, timestamp, source, description, evidence_refs, confidence}`.
- Rule-based ordering sorts by timestamp, then by confidence when timestamps clash.
- Temporal inference: if statement says “around 10 PM” convert to interval [21:45–22:15].
- Timeline output: interactive chart, tabular export, and GraphQL endpoint for integrations.

#### Step 7 – Inconsistency Detection
- **Rule Templates:** time conflicts, location mismatches, statement-vs-medical severity, FIR description vs imagery.
- **Semantic Layer:** embeddings (OpenAI text-embedding-3-large) map similar claims to compare attributes.
- **LLM Reasoning:** GPT-4/5 chain-of-thought prompts analyze grouped evidence to produce human-readable contradiction briefs, each citing source IDs.
- Each inconsistency has severity (`critical`, `moderate`, `info`) and resolution workflow (assign to investigator).

#### Step 8 – Missing Evidence Recommendation
- Coverage matrix tracks categories: forensics, night CCTV, neighbor statements, digital logs, medical follow-ups, call records.
- LLM-based reasoning inspects case profile and proposes prioritized requests (“Obtain forensic swabs”, “Capture alleyway CCTV 20:00–22:00”).
- Suggestions linked to relevant gaps and optionally auto-generate task tickets.

#### Step 9 – Report Generation
- Evidence table with filters (type, confidence, source) + inline previews.
- Timeline visualization (Plotly/Chart.js) and narrative summary paragraphs.
- Inconsistency dashboard lists conflicts, impacted charges, recommended verification steps.
- Missing evidence checklist toggles completion as new files arrive.
- Export pathways: PDF (WeasyPrint/ReportLab), HTML dashboard, JSON/CSV for legal systems.

### 5. Algorithms & Models Summary
| Task | Primary Models / Tools |
| --- | --- |
| Image classification | CLIP, MobileNet, ResNet |
| Object detection | YOLOv8, SSD |
| OCR | Tesseract, Google Vision, AWS Textract |
| Document text extraction | pdfplumber, PyPDF2, Textract |
| NLP entity extraction | spaCy NER, BERT NER |
| Timeline generation | Rule-based timestamp parser + interval reasoning |
| Inconsistency detection | GPT-4/5 reasoning + logic rules |
| Missing evidence | LLM reasoning with coverage matrix |

### 6. Reference Architecture
```
Uploader (React) → FastAPI Gateway → Ingestion Queue (Celery/RabbitMQ)
    → File Store (S3/Azure Blob) + Metadata DB (PostgreSQL + PostGIS)
    → Processing Workers (Vision/OCR/NLP) running on GPU nodes
    → Normalization & Knowledge Graph Service (Neo4j)
    → Reasoning Engine (LLM microservice)
    → Reporting API + Dashboard (Next.js or Streamlit) + PDF Generator
```
- Observability: Prometheus metrics, ELK stack for logs, audit dashboard for evidence chain-of-custody.

### 7. Expected Results
- Auto-organized repository, searchable by entity, time, location, and object.
- Timeline with drill-through to original evidence.
- Contradiction alerts reduce oversight; missing-evidence prompts drive proactive investigation.
- Court-ready PDF with citations and chain-of-custody appendix.

### 8. Novelty & Impact
- First unified stack combining computer vision, OCR, NLP, and LLM reasoning for law enforcement workflows.
- Automatic timeline construction from heterogeneous sources dramatically improves situational awareness.
- Contradiction detection + coverage analysis enables data-driven prosecution strategy.

### 9. Limitations
- Accuracy depends on image clarity, scan quality, and training data representativeness.
- Handwritten OCR remains challenging; fallback manual review may be required.
- LLM reasoning tied to prompt/response quality and may need human verification.
- GPU resources increase cost; offline deployments demand optimized models.

### 10. Future Scope
- Live integration with police RMS and digital evidence lockers.
- Smart suggestions for investigative steps or likely suspect movements.
- 3D crime scene reconstruction using photogrammetry and LiDAR feeds.
- Cross-camera facial recognition and identity resolution across cases.
- Mobile companion app for on-site upload, annotation, and rapid feedback.

### 11. Deployment & Security Considerations
- Zero-trust architecture; evidence buckets encrypted at rest (AES-256) and in transit (TLS 1.3).
- Role-based access control with multi-factor authentication; detailed audit logs.
- Data retention policies aligned with jurisdictional mandates; configurable purging.
- Model governance: drift monitoring, periodic re-training, bias audits.

### 12. Evaluation Metrics
- Classification accuracy per evidence type, OCR character accuracy, NER F1.
- Precision/recall of inconsistency detection validated on historical cases.
- Time saved per case (baseline manual vs automated).
- User satisfaction scores from investigators/legal teams.

### 13. Seminar Delivery Tips
- Start with a real-world anecdote highlighting manual pain points.
- Use the workflow diagram to walk the audience end-to-end.
- Demo timeline + inconsistency dashboard snippets to showcase value.
- Close with impact metrics and roadmap to inspire adoption.

