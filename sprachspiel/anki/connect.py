"""AnkiConnect connector for Sprachspiel."""

import json
import time
from typing import List

import requests

from sprachspiel.config import Config
from sprachspiel.anki.base import BaseAnkiConnector
from sprachspiel.core.card import AnkiCard


class AnkiConnect(BaseAnkiConnector):
    """Connector for AnkiConnect HTTP API."""

    def __init__(self, config: Config):
        """Initialize AnkiConnect connector.

        Args:
            config: Configuration instance.
        """
        self.config = config
        self.host = config.get("anki.connect.host", "localhost")
        self.port = config.get("anki.connect.port", 8765)
        self.api_key = config.get("anki.connect.api_key")
        self.url = f"http://{self.host}:{self.port}"
        self.version = 6  # AnkiConnect API version

    def _request(self, action: str, params: dict = None, retry: int = 3) -> dict:
        """Make request to AnkiConnect.

        Args:
            action: API action name.
            params: Request parameters.
            retry: Number of retries.

        Returns:
            Response data.

        Raises:
            requests.RequestException: If request fails.
        """
        request_data = {
            "action": action,
            "version": self.version,
        }

        if params:
            request_data["params"] = params

        if self.api_key:
            request_data["key"] = self.api_key

        last_error = None

        for attempt in range(retry):
            try:
                response = requests.post(
                    self.url,
                    json=request_data,
                    timeout=10,
                )

                response.raise_for_status()

                data = response.json()

                # Check for API errors
                if len(data) == 2:
                    error = data[0]
                    if error is not None:
                        raise RuntimeError(f"AnkiConnect error: {error}")

                return data[1]

            except requests.RequestException as e:
                last_error = e
                if attempt < retry - 1:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    raise

        raise requests.RequestException(f"AnkiConnect request failed after {retry} retries: {last_error}")

    async def add_note(self, card: AnkiCard) -> str:
        """Add note to Anki.

        Args:
            card: AnkiCard to add.

        Returns:
            Note ID if successful.

        Raises:
            Exception: If note creation fails.
        """
        # Build note parameters
        params = {
            "note": {
                "deckName": card.deck_name,
                "modelName": card.model_name,
                "fields": card.fields,
                "tags": card.tags,
            }
        }

        # Add media files
        if card.audio_files or card.image_files:
            params["note"]["options"] = {"allowDuplicate": False}

        result = self._request("addNote", params)

        if result:
            return str(result)

        raise RuntimeError("Failed to add note: No note ID returned")

    def check_connection(self) -> bool:
        """Check if connection to Anki is available.

        Returns:
            True if connected.
        """
        try:
            result = self._request("version")
            return True
        except Exception:
            return False

    async def add_notes_batch(self, cards: List[AnkiCard]) -> List[str]:
        """Add multiple notes to Anki.

        Args:
            cards: List of AnkiCards to add.

        Returns:
            List of note IDs for successful additions.
        """
        # Build notes parameters
        notes = []

        for card in cards:
            note = {
                "deckName": card.deck_name,
                "modelName": card.model_name,
                "fields": card.fields,
                "tags": card.tags,
                "options": {"allowDuplicate": False},
            }
            notes.append(note)

        params = {"notes": notes}

        result = self._request("addNotes", params)

        # Return successful note IDs (non-None values)
        return [str(note_id) for note_id in result if note_id is not None]

    def get_deck_names(self) -> List[str]:
        """Get list of deck names.

        Returns:
            List of deck names.
        """
        return self._request("deckNames")

    def get_model_names(self) -> List[str]:
        """Get list of model names.

        Returns:
            List of model names.
        """
        return self._request("modelNames")

    def create_deck(self, deck_name: str) -> bool:
        """Create a new deck.

        Args:
            deck_name: Name of deck to create.

        Returns:
            True if successful.
        """
        try:
            self._request("createDeck", {"deck": deck_name})
            return True
        except Exception:
            return False

    def create_model(self, model_name: str, fields: List[str]) -> bool:
        """Create a new model.

        Args:
            model_name: Name of model to create.
            fields: List of field names.

        Returns:
            True if successful.
        """
        try:
            params = {
                "modelName": model_name,
                "inOrderFields": fields,
                "sortf": True,
            }

            self._request("createModel", params)
            return True
        except Exception:
            return False
