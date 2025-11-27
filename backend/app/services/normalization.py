from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


class NormalizationService:
    """
    Step 5 of the methodology: Data Normalization.

    - All timestamps -> canonical ISO format.
    - Locations -> simple canonical form (placeholder for real geocoding).
    - Future: name canonicalization and alias clustering.
    """

    def normalize(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        normalized = extracted.copy()

        timestamp = extracted.get("timestamp")
        if timestamp:
            normalized["timestamp"] = self._to_iso(timestamp)

        location = extracted.get("location")
        if location:
            normalized["location"] = self._normalize_location(location)

        return normalized

    def _to_iso(self, timestamp: str) -> str:
        # Handle EXIF-like and common formats, fall back to now
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y:%m:%d %H:%M:%S"):
            try:
                dt = datetime.strptime(timestamp, fmt)
                return dt.strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError:
                continue
        try:
            dt = datetime.fromisoformat(timestamp)
        except ValueError:
            dt = datetime.utcnow()
        return dt.strftime("%Y-%m-%dT%H:%M:%S")

    def _normalize_location(self, location: str) -> str:
        # Here we simply upper-case; in a real system this would call
        # a geocoding service and an alias dictionary.
        return location.strip().upper()

