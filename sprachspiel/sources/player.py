"""Player data source for video/mpv integration."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sprachspiel.parsers.subtitle_base import BaseSubtitleParser, SubtitleEntry
else:
    BaseSubtitleParser = object  # type: ignore
    SubtitleEntry = object  # type: ignore

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.parsers.ass import ASSParser
from sprachspiel.parsers.srt import SRTParser
from sprachspiel.parsers.vtt import VTTParser
from sprachspiel.sources.base import BaseDataSource
from sprachspiel.types import SourceConfig


class PlayerDataSource(BaseDataSource):
    """Data source for video player integration."""

    def __init__(self, config: Config, source_config: SourceConfig):
        """Initialize player data source.

        Args:
            config: Configuration instance.
            source_config: Source-specific configuration.
        """
        self.config = config
        video_path = source_config.get("video_path")
        subtitle_path = source_config.get("subtitle_path")
        if video_path is None or subtitle_path is None:
            raise ValueError("video_path and subtitle_path are required")
        self.video_path = Path(video_path)
        self.subtitle_path = Path(subtitle_path)
        self.format = source_config.get("subtitle_format", "srt")

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
        return parser_class()  # type: ignore[abstract, misc]

    def _load_subtitles(self) -> list:
        """Load and parse subtitle file.

        Returns:
            List of subtitle entries.
        """
        if not self.subtitle_path.exists():
            return []

        with open(self.subtitle_path, encoding="utf-8") as f:
            content = f.read()

        return self.parser.parse(content)  # type: ignore[return-value]

    def get_card_data(self, word: str, context: str | None = None) -> CardData:
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

    def _find_context_for_word(self, word: str) -> str | None:
        """Find context sentence containing word.

        Args:
            word: Word to search for.

        Returns:
            Context sentence if found.
        """
        word_lower = word.lower()

        for entry in self.entries:  # type: ignore[attr-defined]
            if word_lower in entry.text.lower():  # type: ignore[attr-defined]
                return self.parser.extract_sentence(entry.text)  # type: ignore[attr-defined]

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
