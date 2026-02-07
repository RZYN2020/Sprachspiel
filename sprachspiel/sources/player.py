"""Player data source for video/mpv integration."""

from pathlib import Path
from typing import Optional

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata, Media
from sprachspiel.sources.base import BaseDataSource
from sprachspiel.parsers.subtitle_base import BaseSubtitleParser
from sprachspiel.parsers.srt import SRTParser
from sprachspiel.parsers.vtt import VTTParser
from sprachspiel.parsers.ass import ASSParser


class PlayerDataSource(BaseDataSource):
    """Data source for video player integration."""

    def __init__(self, config: Config, source_config: dict):
        """Initialize player data source.

        Args:
            config: Configuration instance.
            source_config: Source-specific configuration.
        """
        self.config = config
        self.video_path = Path(source_config.get("video_path"))
        self.subtitle_path = Path(source_config.get("subtitle_path"))
        self.format = source_config.get("subtitle_format", "srt")

        # Load subtitle parser
        self.parser = self._get_parser(self.format)
        self.entries = self._load_subtitles()

    def _get_parser(self, format: str) -> BaseSubtitleParser:
        """Get subtitle parser for format.

        Args:
            format: Subtitle format (srt, vtt, ass).

        Returns:
            Subtitle parser instance.
        """
        parsers = {
            "srt": SRTParser,
            "vtt": VTTParser,
            "ass": ASSParser,
        }

        parser_class = parsers.get(format.lower(), SRTParser)
        return parser_class()

    def _load_subtitles(self) -> list:
        """Load and parse subtitle file.

        Returns:
            List of subtitle entries.
        """
        if not self.subtitle_path.exists():
            return []

        with open(self.subtitle_path, "r", encoding="utf-8") as f:
            content = f.read()

        return self.parser.parse(content)

    def get_card_data(self, word: str, context: Optional[str] = None) -> CardData:
        """Get card data for selected word.

        Args:
            word: Selected word or phrase.
            context: Context text (from subtitle).

        Returns:
            Card data with word, context, and metadata.
        """
        # Use provided context or extract from word position
        if not context and self.entries:
            context = self._find_context_for_word(word)

        return CardData(
            word=word,
            context=context or word,
            metadata=CardMetadata(
                source_type="video",
                source_name=self.video_path.name,
                position=None,  # Will be set by mpv Lua script
            ),
        )

    def _find_context_for_word(self, word: str) -> Optional[str]:
        """Find context sentence containing word.

        Args:
            word: Word to search for.

        Returns:
            Context sentence if found.
        """
        word_lower = word.lower()

        for entry in self.entries:
            if word_lower in entry.text.lower():
                return self.parser.extract_sentence(entry.text)

        return None

    def capture_media(self, card: CardData) -> CardData:
        """Capture media resources for card.

        Args:
            card: Card data to enhance with media.

        Returns:
            Card data with media attached.
        """
        # Media capture will be done by mpv Lua script
        # and communicated via HTTP server
        # This is a placeholder for the integration
        return card
