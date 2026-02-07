"""Card data model for Sprachspiel."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class Media:
    """Media resources attached to a card."""

    screenshot: Optional[str] = None  # Path to screenshot image
    audio_word: Optional[str] = None  # Path to TTS audio for word
    audio_context: Optional[str] = None  # Path to audio for context (original or TTS)
    video_segment: Optional[str] = None  # Path to video clip (rarely used)


@dataclass
class CardMetadata:
    """Metadata about the card source."""

    source_type: str  # "video", "pdf", "epub", "text", "web", etc.
    source_name: str  # File name, URL, etc.
    position: Optional[str] = None  # Timestamp, page number, line number, etc.
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CardData:
    """Data for a single Anki card."""

    # Core content
    word: str
    context: str

    # Enhanced data (populated by enhancement services)
    translation: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str] = None

    # Media resources
    media: Media = field(default_factory=Media)

    # Metadata
    metadata: CardMetadata = field(default_factory=CardMetadata)

    # Custom data (from AI functions, etc.)
    custom_data: dict[str, Any] = field(default_factory=dict)

    # Unique identifier
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        """Convert card to dictionary.

        Returns:
            Dictionary representation of card.
        """
        return {
            "id": self.id,
            "word": self.word,
            "context": self.context,
            "translation": self.translation,
            "definition": self.definition,
            "example": self.example,
            "media": {
                "screenshot": self.media.screenshot,
                "audio_word": self.media.audio_word,
                "audio_context": self.media.audio_context,
                "video_segment": self.media.video_segment,
            },
            "metadata": {
                "source_type": self.metadata.source_type,
                "source_name": self.metadata.source_name,
                "position": self.metadata.position,
                "created_at": self.metadata.created_at.isoformat(),
            },
            "custom_data": self.custom_data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CardData":
        """Create card from dictionary.

        Args:
            data: Dictionary representation of card.

        Returns:
            Card instance.
        """
        media_data = data.get("media", {})
        metadata_data = data.get("metadata", {})

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            word=data["word"],
            context=data["context"],
            translation=data.get("translation"),
            definition=data.get("definition"),
            example=data.get("example"),
            media=Media(
                screenshot=media_data.get("screenshot"),
                audio_word=media_data.get("audio_word"),
                audio_context=media_data.get("audio_context"),
                video_segment=media_data.get("video_segment"),
            ),
            metadata=CardMetadata(
                source_type=metadata_data.get("source_type", "unknown"),
                source_name=metadata_data.get("source_name", "unknown"),
                position=metadata_data.get("position"),
                created_at=datetime.fromisoformat(metadata_data.get("created_at", datetime.now(timezone.utc).isoformat()))
                if metadata_data.get("created_at")
                else datetime.now(timezone.utc),
            ),
            custom_data=data.get("custom_data", {}),
        )


@dataclass
class AnkiCard:
    """Anki-ready card with field mapping applied."""

    deck_name: str
    model_name: str
    fields: dict[str, str]
    tags: list[str]
    audio_files: list[str]  # List of audio files to embed
    image_files: list[str]  # List of image files to embed
