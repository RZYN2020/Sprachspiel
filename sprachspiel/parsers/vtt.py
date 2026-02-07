"""VTT (WebVTT) subtitle parser."""

import re

from sprachspiel.parsers.subtitle_base import BaseSubtitleParser, SubtitleEntry


class VTTParser(BaseSubtitleParser):
    """Parser for WebVTT subtitle format."""

    # VTT cue pattern
    CUE_PATTERN = {
        r"(\d{2}):(\d{2})\.(\d{3})\s*-->\s*"  # Start time
        r"(\d{2}):(\d{2})\.(\d{3})\s*\n"  # End time
        r"((?:.+\n?)*)"  # Text (one or more lines)
        r"(?:\n|\r\n|$)"  # End of cue
    }

    def parse(self, content: str) -> list[SubtitleEntry]:
        """Parse VTT subtitle content.

        Args:
            content: Raw VTT file content.

        Returns:
            List of subtitle entries in chronological order.
        """
        entries = []
        lines = content.splitlines()
        index = 0

        # Skip header
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line.startswith("-->") and ":" in line:
                # Found a timestamp line, parse cue
                start_str, end_str = line.split(">")
                start_str = start_str.strip()
                end_str = end_str.strip()

                start = self.parse_timestamp(start_str)
                end = self.parse_timestamp(end_str)

                # Collect text lines
                text_lines = []
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith("-->"):
                    text_line = lines[j].strip()
                    if text_line and not text_line.startswith("NOTE"):
                        text_lines.append(text_line)
                    j += 1

                text = "\n".join(text_lines)
                text = self._clean_text(text)

                if text:
                    entries.append(SubtitleEntry(start=start, end=end, text=text, index=index))
                    index += 1

                i = j
            else:
                i += 1

        return entries

    def find_entry_at_time(
        self, entries: list[SubtitleEntry], timestamp
    ) -> list[SubtitleEntry] | None:
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

    def _clean_text(self, text: str) -> str:
        """Clean subtitle text.

        Args:
            text: Raw subtitle text.

        Returns:
            Cleaned text.
        """
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Remove VTT tags
        text = re.sub(r"<\.{1,5}>", "", text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()
