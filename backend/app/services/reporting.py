from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List

from app.config import settings
from app.models.schemas import ReportSummary
from app.services.timeline import TimelineEvent


class ReportingService:
    def persist_summary(
        self,
        case_id: str,
        events: List[TimelineEvent],
        inconsistencies: List[dict[str, str]],
        missing: List[str],
        extracted_data: List[dict] = None,
    ) -> ReportSummary:
        # Build detailed report with all extracted content
        detailed_report = {
            "case_id": case_id,
            "generated_at": datetime.utcnow().isoformat(),
            "timeline_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "source": event.source,
                    "description": event.description,
                }
                for event in events
            ],
            "inconsistencies": inconsistencies,
            "missing_evidence": missing,
            "extracted_content": [],
        }
        
        # Add all extracted data (text, entities, objects, OCR, etc.)
        if extracted_data:
            for data in extracted_data:
                content_item = {
                    "file_type": data.get("type", "unknown"),
                    "classification": data.get("classification", {}),
                    "extracted_text": "",
                    "entities": [],
                    "objects_detected": [],
                    "ocr_text": "",
                    "timestamps": [],
                    "locations": [],
                    "summary": "",
                }
                
                # Document content
                if data.get("type") == "document":
                    content_item["extracted_text"] = data.get("raw_text", "")[:5000]  # Limit to 5000 chars
                    content_item["entities"] = data.get("entities", [])
                    content_item["timestamps"] = data.get("time_mentions", [])
                    content_item["dates"] = data.get("dates", [])
                    content_item["events"] = data.get("events", [])
                    content_item["summary"] = data.get("summary", "")
                
                # Image content
                elif data.get("type") == "image":
                    content_item["ocr_text"] = data.get("ocr_text", "")[:2000]  # Limit OCR text
                    content_item["objects_detected"] = data.get("objects", [])
                    content_item["timestamps"] = data.get("ocr_timestamps", [])
                    content_item["locations"] = data.get("ocr_locations", [])
                    content_item["gps_coordinates"] = data.get("gps_coordinates")
                    content_item["image_timestamp"] = data.get("timestamp")
                
                detailed_report["extracted_content"].append(content_item)
        
        # Generate structured timeline with source and notes
        structured_timeline = self._build_structured_timeline(events, inconsistencies, extracted_data)
        
        # Generate case summary
        case_summary = self._generate_case_summary(events, inconsistencies, extracted_data)
        
        summary = ReportSummary(
            case_id=case_id,
            generated_at=datetime.utcnow(),
            timeline_events=len(events),
            inconsistencies=len(inconsistencies),
            missing_evidence=missing,
            report_path=str(self._pdf_path(case_id)),
            preview={
                "timeline": structured_timeline,
                "inconsistencies": inconsistencies,
                "extracted_content": detailed_report.get("extracted_content", []),
                "case_summary": case_summary,
            },
        )
        
        # Save detailed JSON report
        self._json_path(case_id).write_text(
            json.dumps(detailed_report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        
        # Save basic summary for API response
        summary_path = settings.reports_dir / f"{case_id}_summary.json"
        summary_path.write_text(summary.model_dump_json(), encoding="utf-8")
        
        # Generate PDF placeholder
        self._pdf_path(case_id).write_text(
            "PDF generation placeholder. Integrate ReportLab/WeasyPrint.", encoding="utf-8"
        )
        return summary

    def _json_path(self, case_id: str) -> Path:
        return settings.reports_dir / f"{case_id}.json"

    def _pdf_path(self, case_id: str) -> Path:
        return settings.reports_dir / f"{case_id}.pdf"
    
    def _build_structured_timeline(self, events: List[TimelineEvent], inconsistencies: List[dict], extracted_data: List[dict]) -> List[dict]:
        """Build a structured timeline with source, event, and conflict notes."""
        structured = []
        
        # Map inconsistencies to events
        inconsistency_map = {}
        for inc in inconsistencies:
            inc_type = inc.get("type", "")
            details = inc.get("details", "")
            # Try to extract time from inconsistency details
            time_match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm))', details, re.IGNORECASE)
            if time_match:
                time_key = time_match.group(1)
                if time_key not in inconsistency_map:
                    inconsistency_map[time_key] = []
                inconsistency_map[time_key].append(inc)
        
        if not events:
            print("[Reporting] Warning: No events to build structured timeline")
            return []
        
        for event in events:
            try:
                # Format time
                if event.timestamp and hasattr(event.timestamp, 'strftime'):
                    time_str = event.timestamp.strftime("%I:%M:%S %p") if event.timestamp.second else event.timestamp.strftime("%I:%M %p")
                else:
                    time_str = "N/A"
                
                # Check for conflicts at this time
                notes = []
                if event.timestamp and hasattr(event.timestamp, 'strftime'):
                    event_time_str = event.timestamp.strftime("%I:%M %p")
                    if event_time_str in inconsistency_map:
                        for inc in inconsistency_map[event_time_str]:
                            notes.append(f"{inc.get('type', 'conflict')}: {inc.get('details', '')[:100]}")
                
                structured.append({
                    "time": time_str,
                    "source": event.source or "Unknown",
                    "event": event.description[:200] if event.description else "N/A",
                    "notes": "; ".join(notes) if notes else None,
                })
            except Exception as e:
                print(f"[Reporting] Error formatting event: {e}")
                structured.append({
                    "time": "N/A",
                    "source": "Unknown",
                    "event": str(event.description)[:200] if hasattr(event, 'description') else "N/A",
                    "notes": None,
                })
        
        return structured
    
    def _generate_case_summary(self, events: List[TimelineEvent], inconsistencies: List[dict], extracted_data: List[dict]) -> str:
        """Generate a concise case summary consolidating all evidence."""
        summary_parts = []
        
        # Extract key information from events
        if events:
            summary_parts.append("TIMELINE OF EVENTS:")
            for event in events[:10]:  # Limit to first 10 events
                time_str = event.timestamp.strftime("%I:%M %p")
                summary_parts.append(f"  • {time_str} ({event.source}): {event.description[:150]}")
        
        # Add inconsistencies
        if inconsistencies:
            summary_parts.append("\nINCONSISTENCIES IDENTIFIED:")
            for inc in inconsistencies:
                inc_type = inc.get("type", "Unknown")
                details = inc.get("details", "")
                severity = inc.get("severity", "moderate")
                summary_parts.append(f"  • [{severity.upper()}] {inc_type}: {details[:200]}")
        
        # Extract key entities and locations
        locations = set()
        persons = set()
        for data in extracted_data:
            if data.get("type") == "document":
                for entity in data.get("entities", []):
                    if entity.get("label") in ["GPE", "LOC", "FAC"]:
                        locations.add(entity.get("entity", ""))
                    elif entity.get("label") == "PERSON":
                        persons.add(entity.get("entity", ""))
        
        if locations or persons:
            summary_parts.append("\nKEY ENTITIES:")
            if persons:
                summary_parts.append(f"  • Persons: {', '.join(list(persons)[:5])}")
            if locations:
                summary_parts.append(f"  • Locations: {', '.join(list(locations)[:5])}")
        
        return "\n".join(summary_parts)

