"""
Step 4: Content Extraction from images and documents using real AI models.

Uses:
- PIL/EXIF for image metadata
- YOLO for object detection
- Tesseract OCR for text in images
- pdfplumber for PDF text extraction
- BERT/spaCy NER for entity extraction
"""

from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
import re

from PIL import Image, ExifTags
import pdfplumber
import pytesseract

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

from app.config import settings
from app.services.model_manager import model_manager


class ExtractionService:
    """
    Content Extraction Service with real AI models.
    """

    def extract(self, artifact_path: Path) -> Dict[str, Any]:
        """
        Extract content from evidence file.
        
        Returns:
            Dict with extracted metadata, entities, objects, OCR text, etc.
        """
        extension = artifact_path.suffix.lower()
        if extension in {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}:
            return self._extract_image_metadata(artifact_path)
        return self._extract_document_metadata(artifact_path)

    # -----------------
    # Image extraction
    # -----------------
    def _extract_image_metadata(self, artifact_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from images:
        - EXIF timestamps and GPS
        - Object detection using YOLO
        - OCR text using Tesseract
        """
        timestamp = None
        gps = None
        gps_coords = None

        # Extract EXIF metadata
        try:
            image = Image.open(artifact_path)
            exif = {
                ExifTags.TAGS.get(k, k): v
                for k, v in (image._getexif() or {}).items()
                if k in ExifTags.TAGS
            }
            raw_dt = exif.get("DateTimeOriginal") or exif.get("DateTime")
            if raw_dt:
                try:
                    timestamp = datetime.strptime(raw_dt, "%Y:%m:%d %H:%M:%S").isoformat()
                except ValueError:
                    # Try alternative formats
                    try:
                        timestamp = datetime.strptime(raw_dt, "%Y-%m-%d %H:%M:%S").isoformat()
                    except ValueError:
                        pass

            # Extract GPS coordinates
            gps_info = exif.get("GPSInfo")
            if gps_info:
                gps = "GPS_AVAILABLE"
                # Convert GPS to decimal degrees
                try:
                    lat_ref = gps_info.get(1, "N")
                    lat_data = gps_info.get(2, (0, 0, 0))
                    lon_ref = gps_info.get(3, "E")
                    lon_data = gps_info.get(4, (0, 0, 0))

                    lat = float(lat_data[0]) + float(lat_data[1]) / 60.0 + float(lat_data[2]) / 3600.0
                    if lat_ref == "S":
                        lat = -lat

                    lon = float(lon_data[0]) + float(lon_data[1]) / 60.0 + float(lon_data[2]) / 3600.0
                    if lon_ref == "W":
                        lon = -lon

                    gps_coords = {"latitude": lat, "longitude": lon}
                except Exception:
                    pass
        except Exception as e:
            print(f"EXIF extraction error: {e}")

        # Object detection using YOLO
        objects_detected = []
        if settings.enable_real_ai:
            try:
                objects_detected = model_manager.detect_objects_yolo(artifact_path)
            except Exception as e:
                print(f"YOLO detection error: {e}")

        # OCR text extraction using Tesseract
        ocr_text = ""
        ocr_timestamps = []
        ocr_locations = []
        try:
            image = Image.open(artifact_path)
            ocr_text = pytesseract.image_to_string(image)
            
            # Extract timestamps from OCR text
            time_patterns = [
                r"\b\d{1,2}:\d{2}:\d{2}\b",  # HH:MM:SS
                r"\b\d{1,2}:\d{2}\s?(AM|PM|am|pm)\b",  # HH:MM AM/PM
                r"\b\d{4}[-/]\d{2}[-/]\d{2}\s+\d{1,2}:\d{2}\b",  # Date + time
            ]
            for pattern in time_patterns:
                matches = re.findall(pattern, ocr_text)
                ocr_timestamps.extend(matches)

            # Extract location-like text (capitalized words, street names, etc.)
            location_patterns = [
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(Road|Street|Avenue|Lane|Drive)\b",
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(Shop|Store|Market|Mall)\b",
            ]
            for pattern in location_patterns:
                matches = re.findall(pattern, ocr_text)
                ocr_locations.extend([m[0] if isinstance(m, tuple) else m for m in matches])
        except Exception as e:
            print(f"OCR extraction error: {e}")

        return {
            "type": "image",
            "timestamp": timestamp,
            "location": gps or "UNKNOWN",
            "gps_coordinates": gps_coords,
            "objects": objects_detected,
            "ocr_text": ocr_text[:1000],  # Limit OCR text length
            "ocr_timestamps": list(set(ocr_timestamps))[:10],
            "ocr_locations": list(set(ocr_locations))[:10],
            "notes": "EXIF, YOLO object detection, and OCR extraction completed.",
        }

    # -----------------
    # Document extraction
    # -----------------
    def _extract_document_metadata(self, artifact_path: Path) -> Dict[str, Any]:
        """
        Extract content from documents:
        - Text extraction from PDFs
        - Named Entity Recognition using BERT/spaCy
        - Time expression extraction
        - Event/action extraction
        """
        text = self._read_pdf_text(artifact_path)
        
        # Extract entities using BERT/spaCy NER
        entities = []
        if settings.enable_real_ai and text:
            try:
                entities = model_manager.extract_entities_bert(text)
            except Exception as e:
                print(f"Entity extraction error: {e}")
                entities = self._simple_entity_guess(text)
        else:
            entities = self._simple_entity_guess(text)

        # Extract time expressions
        time_mentions = self._extract_time_expressions(text)

        # Extract dates
        dates = self._extract_dates(text)

        # Extract actions/events (simple pattern matching)
        events = self._extract_events(text)

        summary = text[:500] + "..." if len(text) > 500 else text

        return {
            "type": "document",
            "raw_text": text,
            "entities": entities,
            "time_mentions": time_mentions,
            "dates": dates,
            "events": events,
            "summary": summary,
        }

    def _read_pdf_text(self, artifact_path: Path) -> str:
        """Extract text from PDF or plain text files."""
        if artifact_path.suffix.lower() != ".pdf":
            try:
                return artifact_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                return ""

        chunks: List[str] = []
        try:
            with pdfplumber.open(artifact_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    chunks.append(page_text)
        except Exception:
            # Fallback: try OCR on scanned PDFs
            if PDF2IMAGE_AVAILABLE:
                try:
                    images = convert_from_path(str(artifact_path), dpi=200)
                    for img in images:
                        text = pytesseract.image_to_string(img)
                        chunks.append(text)
                except Exception as e:
                    print(f"PDF OCR extraction error: {e}")
            else:
                print("pdf2image not available. Install poppler for scanned PDF OCR.")

        return "\n".join(chunks)

    def _simple_entity_guess(self, text: str) -> List[Dict[str, str]]:
        """Fallback regex-based entity extraction."""
        entities: List[Dict[str, str]] = []
        # Look for capitalized names (potential persons or locations)
        for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text[:5000]):
            candidate = match.group(1)
            if len(candidate.split()) <= 4:
                label = "PERSON_OR_LOCATION"
                entities.append({"entity": candidate, "label": label})
        return entities[:50]

    def _extract_time_expressions(self, text: str) -> List[str]:
        """Extract time expressions from text."""
        patterns = [
            r"\b\d{1,2}:\d{2}\s?(AM|PM|am|pm)\b",
            r"\b\d{1,2}:\d{2}:\d{2}\b",
            r"\b\d{1,2}:\d{2}\b",
            r"\b(at|around|approximately)\s+\d{1,2}\s?(AM|PM|am|pm)\b",
        ]
        found: List[str] = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            found.extend([m if isinstance(m, str) else " ".join(m) for m in matches])
        return list(set(found))[:20]

    def _extract_dates(self, text: str) -> List[str]:
        """Extract date expressions from text."""
        patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
            r"\b\d{4}[-/]\d{2}[-/]\d{2}\b",
        ]
        found: List[str] = []
        for pattern in patterns:
            found.extend(re.findall(pattern, text, re.IGNORECASE))
        return list(set(found))[:20]

    def _extract_events(self, text: str) -> List[Dict[str, str]]:
        """Extract action/event phrases from text."""
        # Simple pattern matching for common crime-related actions
        action_patterns = [
            (r"(entered|went into|arrived at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", "location_entry"),
            (r"(heard|witnessed|saw|observed)\s+([a-z]+(?:\s+[a-z]+)*)", "observation"),
            (r"(injured|stabbed|hit|attacked|assaulted)", "violence"),
            (r"(left|exited|departed)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", "location_exit"),
        ]
        events = []
        for pattern, event_type in action_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                events.append({
                    "event": match.group(0),
                    "type": event_type,
                    "context": text[max(0, match.start() - 50):match.end() + 50],
                })
        return events[:30]
