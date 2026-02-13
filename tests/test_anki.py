"""Tests for Anki connectivity."""

from unittest.mock import MagicMock, patch

import pytest

from sprachspiel.anki.base import BaseAnkiConnector
from sprachspiel.anki.connect import AnkiConnect
from sprachspiel.anki.file_export import FileExporter
from sprachspiel.config import Config
from sprachspiel.core.card import AnkiCard


@pytest.fixture
def mock_config() -> Config:
    """Create mock configuration for testing."""
    return Config()


@pytest.fixture
def mock_anki_connect(mock_config: Config) -> AnkiConnect:
    """Create mock AnkiConnect for testing."""
    return AnkiConnect(mock_config)


class TestAnkiConnect:
    """Unit tests for AnkiConnect."""

    def test_init_with_config(self, mock_config: Config) -> None:
        """Test AnkiConnect initialization."""
        connector = AnkiConnect(mock_config)

        assert connector.config is mock_config
        assert connector.host == "localhost"
        assert connector.port == 8765
        assert connector.version == 6

    def test_init_with_custom_host_port(self, mock_config: Config) -> None:
        """Test AnkiConnect initialization with custom host and port."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "anki.connect.host": "192.168.1.1",
                "anki.connect.port": 8080,
            }.get(key, default)
        )
        connector = AnkiConnect(mock_config)

        assert connector.host == "192.168.1.1"
        assert connector.port == 8080

    def test_check_connection_success(
        self, mock_anki_connect: AnkiConnect
    ) -> None:
        """Test successful connection check."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [None, 6]
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = mock_anki_connect.check_connection()

            assert result is True

    def test_check_connection_failure(
        self, mock_anki_connect: AnkiConnect
    ) -> None:
        """Test failed connection check."""
        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("Connection failed")

            result = mock_anki_connect.check_connection()

            assert result is False

    @pytest.mark.asyncio
    async def test_add_note(self, mock_anki_connect: AnkiConnect) -> None:
        """Test adding note to Anki."""
        card = AnkiCard(
            deck_name="Test Deck",
            model_name="Basic",
            fields={"Front": "test", "Back": "test back"},
            tags=["tag1"],
            audio_files=[],
            image_files=[],
        )

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [None, 12345]
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            note_id = await mock_anki_connect.add_note(card)

            assert note_id == "12345"

    @pytest.mark.asyncio
    async def test_add_notes_batch(self, mock_anki_connect: AnkiConnect) -> None:
        """Test adding multiple notes to Anki."""
        cards = [
            AnkiCard(
                deck_name="Test Deck",
                model_name="Basic",
                fields={"Front": f"test{i}", "Back": f"back{i}"},
                tags=["tag1"],
                audio_files=[],
                image_files=[],
            )
            for i in range(3)
        ]

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [None, [100, 101, None]]
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            note_ids = await mock_anki_connect.add_notes_batch(cards)

            assert len(note_ids) == 2
            assert "100" in note_ids
            assert "101" in note_ids

    def test_get_deck_names(self, mock_anki_connect: AnkiConnect) -> None:
        """Test getting deck names."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [None, ["Deck1", "Deck2"]]
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            decks = mock_anki_connect.get_deck_names()

            assert decks == ["Deck1", "Deck2"]

    def test_get_model_names(self, mock_anki_connect: AnkiConnect) -> None:
        """Test getting model names."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [None, ["Basic", "Cloze"]]
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            models = mock_anki_connect.get_model_names()

            assert models == ["Basic", "Cloze"]

    def test_create_deck(self, mock_anki_connect: AnkiConnect) -> None:
        """Test creating a new deck."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [None, None]
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = mock_anki_connect.create_deck("New Deck")

            assert result is True

    def test_create_deck_failure(self, mock_anki_connect: AnkiConnect) -> None:
        """Test creating deck on failure."""
        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("API error")

            result = mock_anki_connect.create_deck("New Deck")

            assert result is False

    def test_create_model(self, mock_anki_connect: AnkiConnect) -> None:
        """Test creating a new model."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [None, None]
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = mock_anki_connect.create_model("New Model", ["Field1", "Field2"])

            assert result is True

    @pytest.mark.asyncio
    async def test_add_note_with_api_key(
        self, mock_config: Config
    ) -> None:
        """Test adding note with API key authentication."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "anki.connect.api_key": "test_api_key"
            }.get(key, default)
        )
        connector = AnkiConnect(mock_config)

        card = AnkiCard(
            deck_name="Test",
            model_name="Basic",
            fields={"Front": "test"},
            tags=[],
            audio_files=[],
            image_files=[],
        )

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [None, 123]
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            await connector.add_note(card)

            # Verify API key was included
            assert mock_post.called

    @pytest.mark.asyncio
    async def test_add_note_retry_on_failure(
        self, mock_anki_connect: AnkiConnect
    ) -> None:
        """Test retry logic on failed requests."""
        call_count = 0

        import requests

        def side_effect(*_args: object, **_kwargs: object) -> MagicMock:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # First two calls fail
                raise requests.RequestException("Temporary error")
            mock_resp = MagicMock()
            mock_resp.json.return_value = [None, 123]
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        card = AnkiCard(
            deck_name="Test",
            model_name="Basic",
            fields={"Front": "test"},
            tags=[],
            audio_files=[],
            image_files=[],
        )

        with patch("requests.post") as mock_post:
            mock_post.side_effect = side_effect

            await mock_anki_connect.add_note(card)

            assert call_count == 3  # 2 failures + 1 success


class TestFileExporter:
    """Unit tests for FileExporter."""

    def test_init_with_config(self, mock_config: Config) -> None:
        """Test FileExporter initialization."""
        exporter = FileExporter(mock_config)

        assert exporter.config is mock_config

    def test_export_cards(self, mock_config: Config) -> None:
        """Test exporting cards to .apkg file."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "anki.file.output_dir": "/tmp/output",
                "anki.file.deck_name": "Test Deck",
            }.get(key, default)
        )
        exporter = FileExporter(mock_config)

        cards = [
            AnkiCard(
                deck_name="Test Deck",
                model_name="Basic",
                fields={"Front": f"test{i}", "Back": f"back{i}"},
                tags=["tag"],
                audio_files=[],
                image_files=[],
            )
            for i in range(2)
        ]

        with patch("zipfile.ZipFile") as mock_zip:
            mock_zip_instance = MagicMock()
            mock_zip_instance.write.return_value = None
            mock_zip_instance.close.return_value = None
            mock_zip.return_value.__enter__.return_value = mock_zip_instance

            output_path = exporter.export_cards(cards)

            assert output_path is not None
            assert output_path.name.endswith(".apkg")


class ConcreteAnkiConnector(BaseAnkiConnector):
    """Concrete implementation for testing BaseAnkiConnector."""

    def __init__(self, config: Config) -> None:
        self.config = config

    async def add_note(self, card: AnkiCard) -> str:
        return "test-id"

    def check_connection(self) -> bool:
        return True

    async def add_notes_batch(self, cards: list[AnkiCard]) -> list[str]:
        return ["id1", "id2"]


class TestBaseAnkiConnector:
    """Unit tests for BaseAnkiConnector."""

    def test_base_implementation_works(self, mock_config: Config) -> None:
        """Test base connector works with concrete implementation."""
        connector = ConcreteAnkiConnector(mock_config)

        assert connector.check_connection() is True
