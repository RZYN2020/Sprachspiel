"""Base Anki connector interface."""

from abc import ABC, abstractmethod
from typing import List

from sprachspiel.core.card import AnkiCard


class BaseAnkiConnector(ABC):
    """Base class for Anki connectors."""

    @abstractmethod
    async def add_note(self, card: AnkiCard) -> str:
        """Add note to Anki.

        Args:
            card: AnkiCard to add.

        Returns:
            Note ID if successful.

        Raises:
            Exception: If note creation fails.
        """
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """Check if connection to Anki is available.

        Returns:
            True if connected.
        """
        pass

    @abstractmethod
    async def add_notes_batch(self, cards: List[AnkiCard]) -> List[str]:
        """Add multiple notes to Anki.

        Args:
            cards: List of AnkiCards to add.

        Returns:
            List of note IDs for successful additions.
        """
        pass
