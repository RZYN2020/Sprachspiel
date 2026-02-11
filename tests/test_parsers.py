"""Tests for subtitle parsers."""

from datetime import timedelta

import pytest

from sprachspiel.parsers.ass import ASSParser
from sprachspiel.parsers.srt import SRTParser
from sprachspiel.parsers.subtitle_base import BaseSubtitleParser, SubtitleEntry
from sprachspiel.parsers.vtt import VTTParser


class ConcreteSubtitleParser(BaseSubtitleParser):
    """Concrete implementation for testing BaseSubtitleParser."""

    def parse(self, content: str) -> list[SubtitleEntry]:
        return []

    def find_entry_at_time(self, entries: list[SubtitleEntry], timestamp: timedelta) -> SubtitleEntry | None:
        return None

    def extract_sentence(self, text: str) -> str:
        return text


class TestSubtitleEntry:
    """Unit tests for SubtitleEntry."""

    def test_entry_creation(self) -> None:
        """Test subtitle entry creation."""
        start = timedelta(hours=0, minutes=1, seconds=23)
        end = timedelta(hours=0, minutes=1, seconds=28)

        entry = SubtitleEntry(start=start, end=end, text="Hello world", index=1)

        assert entry.start == start
        assert entry.end == end
        assert entry.text == "Hello world"
        assert entry.index == 1


class TestBaseSubtitleParser:
    """Unit tests for BaseSubtitleParser."""

    def test_base_not_implemented(self) -> None:
        """Test base parser works with concrete implementation."""
        parser = ConcreteSubtitleParser()

        entries = parser.parse("content")
        assert entries == []

        entry = parser.find_entry_at_time([], timedelta())
        assert entry is None

        sentence = parser.extract_sentence("test")
        assert sentence == "test"


class TestSRTParser:
    """Unit tests for SRT parser."""

    @pytest.fixture
    def srt_parser(self) -> SRTParser:
        """Create SRT parser for testing."""
        return SRTParser()

    def test_parse_empty_content(self, srt_parser: SRTParser) -> None:
        """Test parsing empty SRT content."""
        entries = srt_parser.parse("")

        assert len(entries) == 0

    def test_parse_single_entry(self, srt_parser: SRTParser) -> None:
        """Test parsing single SRT entry."""
        content = """1
00:01:23,000 --> 00:01:28,000
Hello world
"""
        entries = srt_parser.parse(content)

        assert len(entries) == 1
        assert entries[0].text == "Hello world"
        assert entries[0].index == 1

    def test_parse_multiple_entries(self, srt_parser: SRTParser) -> None:
        """Test parsing multiple SRT entries."""
        content = """1
00:01:23,000 --> 00:01:28,000
Hello world

2
00:02:00,000 --> 00:02:05,000
Second subtitle
"""
        entries = srt_parser.parse(content)

        assert len(entries) == 2
        assert entries[0].text == "Hello world"
        assert entries[1].text == "Second subtitle"

    def test_clean_html_tags(self, srt_parser: SRTParser) -> None:
        """Test that HTML tags are cleaned."""
        content = """1
00:01:23,000 --> 00:01:28,000
<i>Hello</i> <b>world</b>
"""
        entries = srt_parser.parse(content)

        assert "Hello" in entries[0].text
        assert "world" in entries[0].text
        assert "<" not in entries[0].text
        assert ">" not in entries[0].text

    def test_extract_sentence(self, srt_parser: SRTParser) -> None:
        """Test sentence extraction."""
        content = """1
00:01:23,000 --> 00:01:28,000
The quick brown fox jumps over the lazy dog.
"""
        entries = srt_parser.parse(content)

        sentence = srt_parser.extract_sentence(entries[0].text)

        assert "quick brown fox" in sentence.lower()

    def test_find_entry_at_time(self, srt_parser: SRTParser) -> None:
        """Test finding entry by timestamp."""
        content = """1
00:01:23,000 --> 00:01:28,000
Hello world

2
00:02:00,000 --> 00:02:05,000
Second subtitle
"""
        entries = srt_parser.parse(content)

        # Find entry within first subtitle
        entry = srt_parser.find_entry_at_time(entries, timedelta(seconds=24))
        assert entry is not None
        assert entry.text == "Hello world"

        # Find entry within second subtitle
        entry = srt_parser.find_entry_at_time(entries, timedelta(seconds=120))
        assert entry is not None
        assert entry.text == "Second subtitle"

        # Find entry outside all subtitles
        entry = srt_parser.find_entry_at_time(entries, timedelta(seconds=300))
        assert entry is None


class TestVTTParser:
    """Unit tests for VTT parser."""

    @pytest.fixture
    def vtt_parser(self) -> VTTParser:
        """Create VTT parser for testing."""
        return VTTParser()

    def test_parse_empty_content(self, vtt_parser: VTTParser) -> None:
        """Test parsing empty VTT content."""
        entries = vtt_parser.parse("")

        assert len(entries) == 0

    def test_parse_single_entry(self, vtt_parser: VTTParser) -> None:
        """Test parsing single VTT entry."""
        content = """00:01:23.000 --> 00:01:28.000
Hello world
"""
        entries = vtt_parser.parse(content)

        assert len(entries) == 1
        assert entries[0].text == "Hello world"

    def test_clean_html_tags(self, vtt_parser: VTTParser) -> None:
        """Test that HTML tags are cleaned."""
        content = """00:01:23.000 --> 00:01:28.000
<i>Hello</i> <b>world</b>
"""
        entries = vtt_parser.parse(content)

        assert "Hello" in entries[0].text
        assert "world" in entries[0].text


class TestASSParser:
    """Unit tests for ASS parser."""

    @pytest.fixture
    def ass_parser(self) -> ASSParser:
        """Create ASS parser for testing."""
        return ASSParser()

    def test_parse_empty_content(self, ass_parser: ASSParser) -> None:
        """Test parsing empty ASS content."""
        entries = ass_parser.parse("")

        assert len(entries) == 0

    def test_parse_simple_content(self, ass_parser: ASSParser) -> None:
        """Test parsing simple ASS content."""
        content = """[Events]
Format: Start,End,Text
Dialogue: 0,0:00.00,0,0:05.00,,0,0,0,,Hello world
"""
        entries = ass_parser.parse(content)

        assert len(entries) == 1
