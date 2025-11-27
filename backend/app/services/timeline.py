import re
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class TimelineEvent:
    """
    Canonical event used in Step 6: Timeline Construction.
    """

    timestamp: datetime
    source: str
    description: str


class TimelineService:
    def build(self, case_id: str, normalized_data: list[dict[str, str]]) -> List[TimelineEvent]:
        """
        Build a simple, sorted timeline from normalized records.

        - For images, use their timestamp and type as a photo/CCTV event.
        - For documents, use time mentions (if any) and summary text.
        """
        events: List[TimelineEvent] = []
        for idx, record in enumerate(normalized_data):
            base_source = record.get("type", "unknown")

            # Image-based event
            if record.get("type") == "image":
                ts_raw = record.get("timestamp") or datetime.utcnow().isoformat()
                dt = datetime.fromisoformat(ts_raw)
                desc = f"Image evidence ({record.get('location', 'UNKNOWN')})"
                events.append(
                    TimelineEvent(
                        timestamp=dt,
                        source=f"{base_source}_{idx}",
                        description=desc,
                    )
                )

            # Document-based events from text time mentions
            elif record.get("type") == "document":
                raw_text = record.get("raw_text", "")
                time_mentions = record.get("time_mentions") or []
                dates = record.get("dates", [])
                
                # Extract actual events from the document text
                extracted_events = self._extract_events_from_text(raw_text, time_mentions, dates)
                
                if extracted_events:
                    print(f"[Timeline] Extracted {len(extracted_events)} events from document")
                    events.extend(extracted_events)
                elif time_mentions:
                    print(f"[Timeline] Using fallback extraction for {len(time_mentions)} time mentions")
                    # Fallback: create events from time mentions
                    for t in time_mentions:
                        try:
                            # Try to parse time and find context around it
                            dt = datetime.strptime(t, "%H:%M")
                            # Use current date or date from document
                            base_date = datetime.utcnow()
                            if dates:
                                try:
                                    # Try to parse first date found
                                    date_str = dates[0]
                                    if "2024" in date_str or "2025" in date_str:
                                        # Extract year, month, day if possible
                                        import re
                                        year_match = re.search(r"20\d{2}", date_str)
                                        if year_match:
                                            base_date = base_date.replace(year=int(year_match.group()))
                                except:
                                    pass
                            dt = dt.replace(year=base_date.year, month=base_date.month, day=base_date.day)
                            
                            # Find context around this time in the text
                            context = self._find_time_context(raw_text, t)
                            events.append(
                                TimelineEvent(
                                    timestamp=dt,
                                    source=f"{base_source}_{idx}",
                                    description=context or f"Event at {t}",
                                )
                            )
                        except Exception:
                            pass
                else:
                    # No time mentions - use document date or current time
                    dt = datetime.utcnow()
                    if dates:
                        try:
                            date_str = dates[0]
                            import re
                            from dateutil import parser
                            dt = parser.parse(date_str)
                        except:
                            pass
                    events.append(
                        TimelineEvent(
                            timestamp=dt,
                            source=f"{base_source}_{idx}",
                            description=record.get("summary", "Document evidence")[:200],
                        )
                    )

        events.sort(key=lambda e: e.timestamp)
        return events
    
    def _extract_events_from_text(self, text: str, time_mentions: List[str], dates: List[str]) -> List[TimelineEvent]:
        """Extract structured events from document text with source identification."""
        events = []
        seen_events = set()  # Track to avoid duplicates
        
        # Pattern to find events with times: "at 8:12:34 PM", "around 8:15 PM", etc.
        time_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm))'
        
        # Identify source types in text
        source_keywords = {
            "CCTV": ["cctv", "camera", "surveillance", "footage"],
            "Witness": ["witness", "statement", "saw", "heard", "observed"],
            "Medical": ["medical", "hospital", "injury", "laceration", "fracture", "examination"],
            "Police": ["police", "officer", "investigation", "memo", "fir"],
        }
        
        # Find all time mentions with context
        for match in re.finditer(time_pattern, text, re.IGNORECASE):
            time_str = match.group(1)
            start_pos = max(0, match.start() - 200)
            end_pos = min(len(text), match.end() + 200)
            context = text[start_pos:end_pos].strip()
            
            # Clean up context - remove extra whitespace
            context = re.sub(r'\s+', ' ', context)
            
            # Identify source from context
            source = "Document"
            context_lower = context.lower()
            for src_name, keywords in source_keywords.items():
                if any(kw in context_lower for kw in keywords):
                    source = src_name
                    break
            
            # Extract meaningful event description
            # Look for action verbs and key phrases
            event_desc = self._extract_event_description(context, time_str)
            
            # Create unique key to avoid duplicates
            event_key = f"{time_str}_{event_desc[:50]}"
            if event_key in seen_events:
                continue
            seen_events.add(event_key)
            
            # Parse time
            try:
                parser_available = False
                try:
                    from dateutil import parser
                    parser_available = True
                    time_obj = parser.parse(time_str)
                except ImportError:
                    # Fallback to basic parsing
                    time_match = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm)?', time_str, re.IGNORECASE)
                    if time_match:
                        hour = int(time_match.group(1))
                        minute = int(time_match.group(2))
                        second = int(time_match.group(3)) if time_match.group(3) else 0
                        am_pm = time_match.group(4)
                        if am_pm and am_pm.upper() == 'PM' and hour != 12:
                            hour += 12
                        elif am_pm and am_pm.upper() == 'AM' and hour == 12:
                            hour = 0
                        from datetime import time as dt_time
                        time_obj = dt_time(hour, minute, second)
                    else:
                        raise ValueError("Could not parse time")
                
                # Use current date or date from document
                base_date = datetime.utcnow()
                if dates:
                    try:
                        date_str = dates[0]
                        if "2024" in date_str or "2025" in date_str:
                            year_match = re.search(r"20\d{2}", date_str)
                            if year_match:
                                base_date = base_date.replace(year=int(year_match.group()))
                            if parser_available:
                                try:
                                    parsed_date = parser.parse(date_str, fuzzy=True)
                                    base_date = parsed_date
                                except:
                                    pass
                    except:
                        pass
                
                # Convert time object to datetime
                if isinstance(time_obj, datetime):
                    dt = time_obj
                else:
                    dt = datetime.combine(base_date.date(), time_obj)
                
                events.append(
                    TimelineEvent(
                        timestamp=dt,
                        source=source,
                        description=event_desc,
                    )
                )
            except Exception as e:
                print(f"Error parsing time {time_str}: {e}")
                pass
        
        return events
    
    def _extract_event_description(self, context: str, time_str: str) -> str:
        """Extract a concise event description from context."""
        # Look for key action phrases
        action_patterns = [
            r'(entered|enters|went into|arrived at)\s+([^.]{0,100})',
            r'(exited|exits|left|departed)\s+([^.]{0,100})',
            r'(altercation|argument|conflict|incident)\s+([^.]{0,100})',
            r'(sustained|received|suffered)\s+(injury|injuries|damage)\s+([^.]{0,100})',
            r'(wearing|wore|wearing)\s+([^.]{0,100})',
            r'(heard|saw|observed|witnessed)\s+([^.]{0,100})',
        ]
        
        context_lower = context.lower()
        for pattern in action_patterns:
            match = re.search(pattern, context_lower, re.IGNORECASE)
            if match:
                # Extract the relevant sentence
                sentences = re.split(r'[.!?]\s+', context)
                for sentence in sentences:
                    if time_str in sentence or any(match.group(1).lower() in sentence.lower() for match in [re.search(pattern, sentence, re.IGNORECASE)] if match):
                        # Clean up the sentence
                        desc = sentence.strip()
                        # Remove excessive whitespace
                        desc = re.sub(r'\s+', ' ', desc)
                        # Limit length
                        return desc[:200]
        
        # Fallback: return first sentence containing the time
        sentences = re.split(r'[.!?]\s+', context)
        for sentence in sentences:
            if time_str in sentence:
                return sentence.strip()[:200]
        
        # Last resort: return context snippet
        return context[:200]
    
    def _find_time_context(self, text: str, time_str: str) -> str:
        """Find context around a time mention in the text."""
        # Find the time in the text
        pattern = re.escape(time_str)
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].strip()
            # Extract first sentence
            sentences = re.split(r'[.!?]\s+', context)
            if sentences:
                return sentences[0][:150]
            return context[:150]
        return f"Event at {time_str}"

