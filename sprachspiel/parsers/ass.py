"""ASS/SSA subtitle parser."""

import re
from datetime import timedelta

from sprachspiel.parsers.subtitle_base import BaseSubtitleParser, SubtitleEntry


class ASSParser(BaseSubtitleParser):
    """Parser for ASS/SSA subtitle format."""

    # ASS dialogue pattern
    DIALOGUE_PATTERN = re.compile(
        r"Dialogue:\s*"  # Start with Dialogue:
        r",\s*"  # Layer
        r"([^,]+?),\s*"  # Start (h:mm:ss.cs)
        r"([^,]+?),\s*"  # End (h:mm:ss.cs)
        r".*?"  # Skip other fields (Style, Name, MarginL/R/V, Effect)
        r"(.+)"  # Text (last field)
    )

    def parse(self, content: str) -> list[SubtitleEntry]:
        """Parse ASS subtitle content.

        Args:
            content: Raw ASS file content.

        Returns:
            List of subtitle entries in chronological order.
        """
        entries: list[SubtitleEntry] = []
        lines = content.splitlines()
        index = 0

        for line in lines:
            line = line.strip()

            if line.startswith("Dialogue:"):
                match = self.DIALOGUE_PATTERN.match(line)
                if match:
                    start = self._parse_ass_timestamp(match.group(1))
                    end = self._parse_ass_timestamp(match.group(2))
                    text = match.group(3).strip()

                    # Clean ASS text
                    text = self._clean_text(text)

                    if text:
                        entries.append(SubtitleEntry(start=start, end=end, text=text, index=index))
                        index += 1

        return entries

    def find_entry_at_time(
        self, entries: list[SubtitleEntry], timestamp: timedelta
    ) -> SubtitleEntry | None:
        """Find subtitle entry at given timestamp.

        Args:
            entries: List of subtitle entries.
            timestamp: Timestamp to search for.

        Returns:
            Subtitle entry if found, None otherwise.
        """
        for entry in entries:
            if entry.start <= timestamp <= entry.end:
                return entry
        return None

    def extract_sentence(self, text: str) -> str:
        """Extract complete sentence from text.

        Args:
            text: Subtitle text.

        Returns:
            Complete sentence (cleaned).
        """
        cleaned = self._clean_text(text)
        return cleaned.strip()

    def _parse_ass_timestamp(self, timestamp_str: str) -> timedelta:
        """Parse ASS timestamp.

        ASS format: H:MM:SS.CS (hours:minutes:seconds.centiseconds)

        Args:
            timestamp_str: ASS timestamp string.

        Returns:
            Timedelta.
        """
        # Format is h:mm:ss.cs
        parts = timestamp_str.split(":")

        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            # Seconds and centiseconds are separated by period
            sec_parts = parts[2].split(".")
            seconds = int(sec_parts[0])
            centiseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0

            return timedelta(
                hours=hours, minutes=minutes, seconds=seconds, milliseconds=centiseconds * 10
            )

        return timedelta()

    def _clean_text(self, text: str) -> str:
        """Clean ASS subtitle text.

        Args:
            text: Raw ASS text.

        Returns:
            Cleaned text.
        """
        # Remove ASS formatting tags
        # {\...} - override tags
        # {\...} - formatting tags (e.g., {\b1}, {\i1}, {\c&H1&H1&H1})
        # [text] - inline tags (e.g., [K])
        text = re.sub(r"\{[^}]+\}", "", text)
        text = re.sub(r"\[[^\]]+\]", "", text)

        # Remove line breaks
        text = re.sub(r"\\[Nn]", " ", text)

        # Remove HTML entities
        text = re.sub(r"&[^;]+;", " ", text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()
