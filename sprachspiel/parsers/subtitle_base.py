"""Base subtitle parser interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional


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
    def find_entry_at_time(self, entries: list[SubtitleEntry], timestamp: timedelta) -> Optional[SubtitleEntry]:
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
            timestamp_str: Timestamp string (e.g., "00:01:23,000").

        Returns:
            Timedelta.
        """
        # Handle both SRT/VTT (00:01:23,000) and ASS (0:00:01.23) formats
        timestamp_str = timestamp_str.strip()

        # Replace common separators
        timestamp_str = timestamp_str.replace(",", ".").replace(".", ":")

        parts = timestamp_str.split(":")
        parts = [int(p) for p in parts]

        if len(parts) == 4:
            # Hours, minutes, seconds, milliseconds
            return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2], milliseconds=parts[3])
        elif len(parts) == 3:
            # Hours, minutes, seconds.milliseconds
            return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
        elif len(parts) == 2:
            # Minutes, seconds.milliseconds
            return timedelta(minutes=parts[0], seconds=parts[1])
        else:
            # Just seconds
            return timedelta(seconds=parts[0])
