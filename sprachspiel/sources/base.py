"""Base data source interface."""

from abc import ABC, abstractmethod
from typing import Optional

from sprachspiel.core.card import CardData


class BaseDataSource(ABC):
    """Base class for data sources."""

    @abstractmethod
    def get_card_data(self, word: str, context: Optional[str] = None) -> CardData:
        """Get card data for selected word.

        Args:
            word: Selected word or phrase.
            context: Context text (sentence, paragraph, etc.).

        Returns:
            Card data with word, context, and metadata.
        """
        pass

    @abstractmethod
    def capture_media(self, card: CardData) -> CardData:
        """Capture media resources for card.

        Args:
            card: Card data to enhance with media.

        Returns:
            Card data with media attached.
        """
        pass
