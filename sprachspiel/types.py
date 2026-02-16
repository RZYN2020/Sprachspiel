"""Type definitions for Sprachspiel.

This module contains type aliases and TypedDict definitions
for strong typing throughout the codebase.
"""

from typing import Any, TypedDict


class MediaDict(TypedDict, total=False):
    """Dictionary representation of Media."""

    screenshot: str | None
    audio_word: str | None
    audio_context: str | None
    video_segment: str | None


class CardMetadataDict(TypedDict, total=False):
    """Dictionary representation of CardMetadata."""

    source_type: str
    source_name: str
    position: str | None
    created_at: str


class CardDict(TypedDict, total=False):
    """Dictionary representation of CardData."""

    id: str
    word: str
    context: str
    translation: str | None
    definition: str | None
    example: str | None
    media: MediaDict
    metadata: CardMetadataDict
    custom_data: dict[str, str]


class DictionaryResult(TypedDict, total=False):
    """Result from dictionary lookup."""

    translation: str | None
    definition: str | None
    example: str | None


class VariableContext(TypedDict, total=False):
    """Context variables for template substitution."""

    word: str
    context: str
    translation: str
    definition: str
    example: str
    source_type: str
    source_name: str
    position: str
    screenshot: str
    audio_file: str
    custom_data: dict[str, str]


class CardSummary(TypedDict, total=False):
    """Summary of a card for API responses."""

    id: str
    word: str
    source_type: str


class SourceConfig(TypedDict, total=False):
    """Configuration for data sources."""

    file_path: str
    source_type: str
    path: str
    type: str
    video_path: str
    subtitle_path: str
    subtitle_format: str
    columns: dict[str, int]
    _skip_header: bool
    one_word_per_line: bool


# Type aliases for common patterns
FieldMapping = dict[str, str]
TagList = list[str]
AudioFiles = list[str]
ImageFiles = list[str]
DictValue = str | None | dict[str, Any]
