"""Base subtitle parser interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class SubtitleEntry:
    """A single subtitle entry."""

    start: timedelta  # Start time
    end: timedelta  # End time
    text: str  # Subtitle text
    index: int  # Entry index for ordering


class BaseSubtitleParser(ABC):
    """Base class for subtitle parsers."""

    @abstractmethod
    def parse(self, content: str) -> list[SubtitleEntry]:
        """Parse subtitle content.

        Args:
            content: Raw subtitle file content.

        Returns:
            List of subtitle entries in chronological order.
        """
        pass

    @abstractmethod
    def find_entry_at_time(self, entries: list[SubtitleEntry], timestamp: timedelta) -> SubtitleEntry | None:
        """Find subtitle entry at given timestamp.

        Args:
            entries: List of subtitle entries.
            timestamp: Timestamp to search for.

        Returns:
            Subtitle entry if found, None otherwise.
        """
        pass

    @abstractmethod
    def extract_sentence(self, text: str) -> str:
        """Extract complete sentence from text.

        Args:
            text: Subtitle text.

        Returns:
            Complete sentence.
        """
        pass

    @staticmethod
    def parse_timestamp(timestamp_str: str) -> timedelta:
        """Parse timestamp string to timedelta.

        Args:
            timestamp_str: Timestamp string (e.g., "00:01:23,000" for SRT
            or "00:01:23.000" for VTT).

        Returns:
            Timedelta.
        """
        # Handle both SRT (00:01:23,000), VTT (00:01:23.000), and ASS (0:00:01.23)
        timestamp_str = timestamp_str.strip()

        # Replace comma with period for consistent decimal separator
        timestamp_str = timestamp_str.replace(",", ".")

        # Split by colon to get time components
        parts_str = timestamp_str.split(":")

        if len(parts_str) == 3:
            # Format: "HH:MM:SS.mmm" (VTT) or "HH:MM:SS,mmm" (SRT)
            hours = int(parts_str[0])
            minutes = int(parts_str[1])
            # Split seconds and milliseconds
            sec_parts = parts_str[2].split(".")
            seconds = int(sec_parts[0])
            milliseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0
            return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
        elif len(parts_str) == 2:
            # Format: "MM:SS.mmm" or "H:MM:SS.cc" (ASS format)
            # ASS format uses centiseconds (2 digits), VTT/SRT uses milliseconds (3 digits)
            sec_parts = parts_str[1].split(".")
            seconds = int(sec_parts[0])
            if len(sec_parts) > 1:
                frac_part = sec_parts[1].ljust(3, "0")[:3]  # Pad or truncate to 3 digits
                milliseconds = int(frac_part)
            else:
                milliseconds = 0
            return timedelta(minutes=int(parts_str[0]), seconds=seconds, milliseconds=milliseconds)
        elif len(parts_str) == 1:
            # Just seconds
            return timedelta(seconds=int(parts_str[0]))
        else:
            # Fallback for other formats
            return timedelta()
