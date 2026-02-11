"""Card generation engine for Sprachspiel."""

import asyncio
from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sprachspiel.anki.base import BaseAnkiConnector
    from sprachspiel.anki.connect import AnkiConnect
    from sprachspiel.anki.file_export import FileExporter
else:
    BaseAnkiConnector = object  # type: ignore
    AnkiConnect = object  # type: ignore
    FileExporter = object  # type: ignore

from sprachspiel.config import Config
from sprachspiel.core.card import AnkiCard, CardData
from sprachspiel.core.mapper import FieldMapper


class CardEngine:
    """Engine for generating and processing cards."""

    def __init__(self, config: Config):
        """Initialize card engine.

        Args:
            config: Configuration instance.
        """
        self.config = config
        self.mapper = FieldMapper(config)

        # Initialize components
        self._init_anki()
        self._init_services()

    def _init_anki(self) -> None:
        """Initialize Anki connector."""
        from sprachspiel.anki.connect import AnkiConnect
        from sprachspiel.anki.file_export import FileExporter

        mode = self.config.get("anki.mode")

        self.anki_connectors: list[BaseAnkiConnector] = []
        self.anki_connect: AnkiConnect | None = None
        self.file_exporter: FileExporter | None = None

        if mode in ["connect", "both"]:
            self.anki_connect = AnkiConnect(self.config)
            self.anki_connectors.append(self.anki_connect)

        if mode in ["file", "both"]:
            self.file_exporter = FileExporter(self.config)
            self.anki_connectors.append(self.file_exporter)

    def _init_services(self) -> None:
        """Initialize enhancement services."""
        from sprachspiel.services.ai import AIService
        from sprachspiel.services.dictionary import DictionaryService
        from sprachspiel.services.tts import TTSService

        # Initialize services (lazy load based on config)
        self.dictionary = DictionaryService(self.config)
        self.tts = TTSService(self.config)
        self.ai = AIService(self.config)

    async def generate_card(self, card_data: CardData) -> AnkiCard:
        """Generate a complete card with enhancements.

        Args:
            card_data: Raw card data.

        Returns:
            Complete AnkiCard ready for pushing.
        """
        # Enhancement: Dictionary lookup
        if self.dictionary.is_configured():
            try:
                dict_result = await self.dictionary.lookup(card_data.word)
                card_data.translation = dict_result.get("translation")
                card_data.definition = dict_result.get("definition")
                card_data.example = dict_result.get("example")
            except Exception as e:
                print(f"Dictionary lookup failed: {e}")

        # Enhancement: AI functions
        if self.ai.is_configured():
            try:
                # Run AI functions in parallel
                ai_tasks: list[Coroutine[Any, Any, str | None]] = []

                if self.ai.has_function("translate") and not (card_data.translation):
                    ai_tasks.append(self.ai.call_function("translate", card_data.word))

                if self.ai.has_function("example") and not (card_data.example):
                    ai_tasks.append(self.ai.call_function("example", card_data.word))

                # Run all AI
                results = await asyncio.gather(*ai_tasks, return_exceptions=True)  # type: ignore[arg-type]

                # Apply results
                if self.ai.has_function("translate") and len(results) > 0 and results[0]:
                    if not isinstance(results[0], Exception):  # type: ignore[arg-type]
                        card_data.translation = results[0]  # type: ignore[assignment]

                if self.ai.has_function("example") and len(results) > 1 and results[1]:
                    if not isinstance(results[1], Exception):  # type: ignore[arg-type]
                        card_data.example = results[1]  # type: ignore[assignment]

                # Run custom AI functions
                for func_name in self.ai.get_custom_functions():
                    result = await self.ai.call_function(func_name, card_data.word)
                    if result and not isinstance(result, Exception):
                        card_data.custom_data[func_name] = result

            except Exception as e:
                print(f"AI enhancement failed: {e}")

        # Enhancement: TTS
        if self.tts.is_configured():
            try:
                # Generate TTS audio for word
                audio_word = await self.tts.synthesize(card_data.word)
                card_data.media.audio_word = audio_word
            except Exception as e:
                print(f"TTS synthesis failed: {e}")

        # Map to Anki fields
        anki_card = self.mapper.map_card(card_data)

        return anki_card

    def generate_card_sync(self, card_data: CardData) -> AnkiCard:
        """Synchronous wrapper for generate_card.

        Args:
            card_data: Raw card data.

        Returns:
            Complete AnkiCard ready for pushing.
        """
        return asyncio.run(self.generate_card(card_data))

    async def push_card(self, card: AnkiCard) -> bool:
        """Push card to Anki.

        Args:
            card: AnkiCard to push.

        Returns:
            True if push was successful.
        """
        success = True

        for connector in self.anki_connectors:
            try:
                await connector.add_note(card)
            except Exception as e:
                print(f"Failed to push card via {connector.__class__.__name__}: {e}")
                success = False

        return success

    def push_card_sync(self, card: AnkiCard) -> bool:
        """Synchronous wrapper for push_card.

        Args:
            card: AnkiCard to push.

        Returns:
            True if push was successful.
        """
        return asyncio.run(self.push_card(card))

    async def process_queue(self) -> tuple[int, int]:
        """Process all cards in queue.

        Returns:
            Tuple of (success_count, total_count).
        """
        from sprachspiel.core.queue import CardQueue

        queue = CardQueue(self.config)

        if queue.is_empty():
            return (0, 0)

        # Get batch size
        batch_size = self.config.get("card_generation.queue.batch_size", 10)

        # Process in batches
        total = queue.size()
        success_count = 0

        while not queue.is_empty():
            batch = queue.get_batch(batch_size)

            # Enhance and map cards
            anki_cards: list[tuple[AnkiCard, str]] = []
            for card_data in batch:
                anki_card = await self.generate_card(card_data)
                anki_cards.append((anki_card, card_data.id))

            # Push to Anki
            for anki_card, card_id in anki_cards:
                if await self.push_card(anki_card):
                    queue.remove(card_id)
                    success_count += 1

        return (success_count, total)

    def process_queue_sync(self) -> tuple[int, int]:
        """Synchronous wrapper for process_queue.

        Returns:
            Tuple of (success_count, total_count).
        """
        return asyncio.run(self.process_queue())
