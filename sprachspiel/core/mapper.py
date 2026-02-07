"""Field mapping with template variable substitution."""

import re
from pathlib import Path
from typing import Any, Dict, Optional

from sprachspiel.core.card import CardData, AnkiCard


class TemplateError(Exception):
    """Raised when template variable is malformed."""

    def __init__(self, message: str, template: Optional[str] = None):
        super().__init__(message)
        self.template = template


class FieldMapper:
    """Map card data to Anki fields using template variables."""

    # Pattern for template variables: ${variable_name}
    VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")

    def __init__(self, config):
        """Initialize field mapper.

        Args:
            config: Configuration instance.
        """
        self.config = config
        self.field_mapping = config.get("anki.field_mapping", {})
        self.deck_name = config.get("anki.file.deck_name", "Default")
        self.model_name = config.get("anki.file.model_name", "Basic")

    def map_card(self, card: CardData) -> AnkiCard:
        """Map card data to Anki card.

        Args:
            card: Card data to map.

        Returns:
            AnkiCard with fields populated.
        """
        # Build variable context
        variables = self._build_variable_context(card)

        # Map each field
        fields = {}
        for field_name, template in self.field_mapping.items():
            try:
                fields[field_name] = self._substitute_template(template, variables)
            except TemplateError as e:
                # Log error but continue with partial result
                print(f"Warning: Template error for field {field_name}: {e}")

        # Collect media files
        audio_files = []
        image_files = []

        if card.media.audio_word:
            audio_files.append(card.media.audio_word)
        if card.media.audio_context:
            audio_files.append(card.media.audio_context)
        if card.media.screenshot:
            image_files.append(card.media.screenshot)
        if card.media.video_segment:
            # Video segments typically embedded via video tags, not as separate files
            pass

        # Build tags
        tags = self._build_tags(card)

        return AnkiCard(
            deck_name=self.deck_name,
            model_name=self.model_name,
            fields=fields,
            tags=tags,
            audio_files=audio_files,
            image_files=image_files,
        )

    def _build_variable_context(self, card: CardData) -> Dict[str, Any]:
        """Build variable context for template substitution.

        Args:
            card: Card data.

        Returns:
            Dictionary of variables for template substitution.
        """
        variables = {
            "word": card.word,
            "context": card.context,
            "translation": card.translation or "",
            "definition": card.definition or "",
            "example": card.example or "",
            "source_type": card.metadata.source_type,
            "source_name": card.metadata.source_name,
            "position": card.metadata.position or "",
        }

        # Add media paths
        if card.media.screenshot:
            variables["screenshot"] = str(card.media.screenshot)
        else:
            variables["screenshot"] = ""

        if card.media.audio_word:
            variables["audio_file"] = str(Path(card.media.audio_word).stem)
        else:
            variables["audio_file"] = ""

        # Add custom data
        for key, value in card.custom_data.items():
            variables[key] = value

        return variables

    def _substitute_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute template variables.

        Args:
            template: Template string with ${variable} placeholders.
            variables: Dictionary of variable values.

        Returns:
            String with variables substituted.

        Raises:
            TemplateError: If template is malformed.
        """
        if not isinstance(template, str):
            return str(template) if template else ""

        def replace_var(match):
            var_name = match.group(1)

            # Handle nested variable access (e.g., ${media.screenshot})
            parts = var_name.split(".")
            value = variables

            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, "")
                else:
                    value = getattr(value, part, "")
                    if value is None:
                        value = ""
                    break

            return str(value)

        try:
            return self.VAR_PATTERN.sub(replace_var, template)
        except Exception as e:
            raise TemplateError(f"Failed to substitute template: {e}", template) from e

    def _build_tags(self, card: CardData) -> list:
        """Build tags for card.

        Args:
            card: Card data.

        Returns:
            List of tags.
        """
        # Get tags from field mapping if configured
        tags_template = self.field_mapping.get("tags", "")
        variables = self._build_variable_context(card)

        if tags_template:
            tags_str = self._substitute_template(tags_template, variables)
            tags = [tag.strip() for tag in tags_str.split() if tag.strip()]
        else:
            # Default tags
            tags = [card.metadata.source_type]

        return tags
