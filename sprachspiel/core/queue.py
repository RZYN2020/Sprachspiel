"""Card queue management for Sprachspiel."""

import json
from pathlib import Path

from sprachspiel.config import QUEUE_DIR, Config
from sprachspiel.core.card import CardData


class CardQueue:
    """Manage pending cards in a queue."""

    def __init__(self, config: Config):
        """Initialize card queue.

        Args:
            config: Configuration instance.
        """
        self.config = config
        # Use storage_dir from config if provided, otherwise use default QUEUE_DIR
        storage_dir = config.get("card_generation.queue.storage_dir")
        if storage_dir:
            self.queue_file = Path(storage_dir) / "queue.json"
        else:
            self.queue_file = QUEUE_DIR / "queue.json"
        self._queue: dict[str, CardData] = {}
        self._load()

    def _load(self) -> None:
        """Load queue from file."""
        if not self.queue_file.exists():
            self._queue = {}
            return

        try:
            with open(self.queue_file, encoding="utf-8") as f:
                data = json.load(f)
                self._queue = {k: CardData.from_dict(v) for k, v in data.items()}
        except (json.JSONDecodeError, KeyError, TypeError):
            # If the file is corrupted, start with an empty queue
            self._queue = {}

    def load(self) -> None:
        """Load queue from file (public method)."""
        self._load()

    def _save(self) -> None:
        """Save queue to file."""
        # Ensure the parent directory exists
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.queue_file, "w", encoding="utf-8") as f:
            data = {k: v.to_dict() for k, v in self._queue.items()}
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save(self) -> None:
        """Save queue to file (public method)."""
        self._save()

    def add(self, card: CardData) -> None:
        """Add card to queue.

        Args:
            card: Card data to add.
        """
        self._queue[card.id] = card
        self._save()

    def get(self, card_id: str) -> CardData:
        """Get card by ID.

        Args:
            card_id: Card ID.

        Returns:
            Card data.

        Raises:
            KeyError: If card not found.
        """
        return self._queue[card_id]

    def remove(self, card_id: str) -> bool:
        """Remove card from queue.

        Args:
            card_id: Card ID.

        Returns:
            True if card was removed, False if not found.
        """
        if card_id in self._queue:
            del self._queue[card_id]
            self._save()
            return True
        return False

    def get_all(self) -> list[CardData]:
        """Get all cards in queue.

        Returns:
            List of all cards in queue.
        """
        return list(self._queue.values())

    def clear(self) -> None:
        """Clear all cards from queue."""
        self._queue.clear()
        self._save()

    def size(self) -> int:
        """Get queue size.

        Returns:
            Number of cards in queue.
        """
        return len(self._queue)

    def is_empty(self) -> bool:
        """Check if queue is empty.

        Returns:
            True if queue is empty.
        """
        return len(self._queue) == 0

    def get_batch(self, batch_size: int) -> list[CardData]:
        """Get a batch of cards.

        Args:
            batch_size: Maximum number of cards to return.

        Returns:
            List of cards (up to batch_size).
        """
        cards = list(self._queue.values())[:batch_size]
        return cards

    def remove_batch(self, card_ids: list[str]) -> int:
        """Remove a batch of cards from queue.

        Args:
            card_ids: List of card IDs to remove.

        Returns:
            Number of cards removed.
        """
        removed = 0
        for card_id in card_ids:
            if card_id in self._queue:
                del self._queue[card_id]
                removed += 1

        if removed > 0:
            self._save()

        return removed
