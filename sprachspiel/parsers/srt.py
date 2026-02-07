"""SRT subtitle parser."""

import re
from typing import List

from sprachspiel.parsers.subtitle_base import BaseSubtitleParser, SubtitleEntry


class SRTParser(BaseSubtitleParser):
    """Parser for SRT subtitle format."""

    # SRT entry pattern
    ENTRY_PATTERN = re.compile(
        r"(\d+)\s*\n"  # Index
        r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*"  # Start time
        r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*\n"  # End time
        r"(.+?)\s*(?:\n|$)"  # Text (non-greedy)
        r"(?:\n|\r\n|$)"  # End of entry (or end of file)
    , re.DOTALL | re.MULTILINE
    )

    def parse(self, content: str) -> List[SubtitleEntry]:
        """Parse SRT subtitle content.

        Args:
            content: Raw SRT file content.

        Returns:
            List of subtitle entries in chronological order.
        """
        entries = []
        matches = self.ENTRY_PATTERN.finditer(content)

        for match in matches:
            index = int(match.group(1))

            # Parse start time
            start = self.parse_timestamp(match.group(2))

            # Parse end time
            end = self.parse_timestamp(match.group(6))

            # Get text and clean up
            text = match.group(10).strip()
            text = self._clean_text(text)

            entries.append(SubtitleEntry(start=start, end=end, text=text, index=index))

        return entries

    def find_entry_at_time(
        self, entries: List[SubtitleEntry], timestamp
    ) -> List[SubtitleEntry] | None:
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
        # Remove HTML tags and formatting
        cleaned = self._clean_text(text)
        return cleaned.strip()

    def _clean_text(self, text: str) -> str:
        """Clean subtitle text.

        Args:
            text: Raw subtitle text.

        Returns:
            Cleaned text.
        """
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Remove common subtitle formatting
        text = re.sub(r"\{[^}]+\}", "", text)  # {an8}
        text = re.sub(r"&[^;]+;", " ", text)  # HTML entities

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove leading/trailing dashes and pipes
        text = text.strip("-| ")

        return text.strip()
