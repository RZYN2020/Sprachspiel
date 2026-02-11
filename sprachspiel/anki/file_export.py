"""File export connector for .apkg generation."""

import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from sprachspiel.anki.base import BaseAnkiConnector
from sprachspiel.config import Config
from sprachspiel.core.card import AnkiCard


class FileExporter(BaseAnkiConnector):
    """Connector for exporting to .apkg files."""

    def __init__(self, config: Config):
        """Initialize file exporter.

        Args:
            config: Configuration instance.
        """
        self.config = config
        self.deck_name = config.get("anki.file.deck_name", "Sprachspiel")
        self.output_dir = Path(config.get("anki.file.output_dir", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def add_note(self, card: AnkiCard) -> str:
        """Add note to file export (not implemented for single notes).

        Args:
            card: AnkiCard to add.

        Returns:
            Note ID.

        Raises:
            NotImplementedError: Single note export not supported.
        """
        raise NotImplementedError(
            "Single note export not supported. Use export_cards() for batch export."
        )

    def check_connection(self) -> bool:
        """Check if file export is available.

        Returns:
            Always True (file export is always available).
        """
        return True

    async def add_notes_batch(self, cards: list[AnkiCard]) -> list[str]:
        """Add multiple notes to export.

        Args:
            cards: List of AnkiCards to add.

        Returns:
            List of note IDs (indices).
        """
        raise NotImplementedError(
            "Batch note export not supported. Use export_cards() for export."
        )

    def export_cards(self, cards: list[AnkiCard], output_dir: Path | None = None) -> Path:
        """Export cards to as .apkg file.

        Args:
            cards: List of AnkiCardsari to export.
            output_dir: Output directory. Uses config default if None.

        Returns:
            Path to generated .apkg file.
        """
        actual_output_dir: Path
        if output_dir:
            actual_output_dir = Path(output_dir)
        else:
            actual_output_dir = self.output_dir

        actual_output_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        apkg_filename = f"{self.deck_name}_{timestamp}.apkg"
        apkg_path = actual_output_dir / apkg_filename

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create Anki collection structure
            self._create_anki_package(cards, temp_path)

            # Create .apkg file (zip)
            with zipfile.ZipFile(apkg_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(temp_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(temp_path)
                        zf.write(file_path, arcname)

        return apkg_path

    def _create_anki_package(self, cards: list[AnkiCard], output_dir: Path) -> None:
        """Create Anki package directory structure.

        Args:
            cards: List of AnkiCards to export.
            output_dir: Output directory for package.
        """
        # Create media subdirectory
        media_dir = output_dir / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        # Collect all media files
        media_files: dict[str, str] = {}
        file_index = 0

        for card in cards:
            for audio_file in card.audio_files:
                if Path(audio_file).exists():
                    # Copy to media directory with numbered name
                    ext = Path(audio_file).suffix
                    new_name = f"{file_index}{ext}"
                    shutil.copy(audio_file, media_dir / new_name)
                    media_files[Path(audio_file).name] = new_name
                    file_index += 1

            for image_file in card.image_files:
                if Path(image_file).exists():
                    ext = Path(image_file).suffix
                    new_name = f"{file_index}{ext}"
                    shutil.copy(image_file, media_dir / new_name)
                    media_files[Path(image_file).name] = new_name
                    file_index += 1

        # Create deck JSON
        deck_json: dict[str, Any] = {
            "name": self.deck_name,
            "mid": 1600000000,  # Default model ID
            "fields": list(self._get_field_names(cards)),
            "css": "",
            "tmpls": [
                {
                    "name": "Card 1",
                    "qfmt": self._get_front_template(cards),
                    "afmt": self._get_back_template(cards),
                    "bqfmt": "",
                    "bafmt": "",
                }
            ],
            "sort": {"field": 0, "order": "asc"},
            "mod": 1600000000,
        }

        # Create notes JSON
        notes: list[dict[str, Any]] = []
        for i, card in enumerate(cards):
            note: dict[str, Any] = {
                "guid": self._generate_guid(i),
                "mid": 1600000000,
                "mod": int(datetime.now().timestamp()),
                "usn": -1,
                "tags": ",".join(card.tags),
                "flds": list(card.fields.values()),
                "data": "",
            }
            notes.append(note)

        # Create deck directory
        deck_dir = output_dir / str(1600000000)
        deck_dir.mkdir(parents=True, exist_ok=True)

        # Write deck.json
        with open(deck_dir / "deck.json", "w", encoding="utf-8") as f:
            json.dump(deck_json, f, ensure_ascii=False)

        # Write notes.json
        with open(deck_dir / "notes.json", "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False)

        # Create meta.json
        meta_json: dict[str, Any] = {
            "exported_at": datetime.now().isoformat(),
            "deck_name": self.deck_name,
            "note_count": len(cards),
            "models": [1600000000],
            "decks": [1600000000],
        }

        with open(output_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta_json, f, ensure_ascii=False)

    def _get_field_names(self, cards: list[AnkiCard]) -> set[str]:
        """Get all field names from cards.

        Args:
            cards: List of AnkiCards.

        Returns:
            Set of field names.
        """
        field_names: set[str] = set()

        for card in cards:
            field_names.update(card.fields.keys())

        # Ensure standard fields exist
        standard_fields = {"Front", "Back"}
        field_names.update(standard_fields)

        return field_names

    def _get_front_template(self, cards: list[AnkiCard]) -> str:
        """Get front template from cards.

        Args:
            cards: List of AnkiCards.

        Returns:
            Front template string.
        """
        # Try to find front/back fields
        fields = self._get_field_names(cards)

        front_field = "Front"
        for field in fields:
            if field.lower() in ["front", "question"]:
                front_field = field
                break

        return "{{" + front_field + "}}"

    def _get_back_template(self, cards: list[AnkiCard]) -> str:
        """Get back template from cards.

        Args:
            cards: List of AnkiCards.

        Returns:
            Back template string.
        """
        fields = self._get_field_names(cards)

        back_field = "Back"
        for field in fields:
            if field.lower() in ["back", "answer"]:
                back_field = field
                break

        return "{{" + back_field + "}}"

    def _generate_guid(self, index: int) -> str:
        """Generate GUID for note.

        Args:
            index: Note index.

        Returns:
            GUID string.
        """
        import uuid
        return str(uuid.uuid5(uuid.NAMESPACE_URL, str(index)))
