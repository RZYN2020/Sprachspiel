# Sprachspiel

Anki card generation assistant for language learners.

## Features

- **Multi-source support**: Create cards from videos (with subtitles), PDF/EPUB/Text files, CSV imports, and web content
- **Dual Anki connection**: Real-time push via AnkiConnect or export to .apkg files (or both)
- **Enhancement services**: Dictionary lookups, TTS pronunciation, AI-powered translation and example generation
- **Flexible configuration**: YAML-based configuration with customizable field mapping templates
- **Queue mode**: Batch card generation and processing
- **Extensible**: Custom parsers, dictionaries, TTS providers, and AI functions

## Installation

```bash
pip install sprachspiel
```

For optional mpv player integration:
```bash
pip install sprachspiel[mpv]
```

## Quick Start

1. **Create configuration**:
   ```bash
   # Configuration will be created at ~/.config/sprachspiel/config.yaml
   sprachspiel config anki.mode both
   ```

2. **Start the HTTP server**:
   ```bash
   sprachspiel start
   ```

3. **Use the API**:
   - Send word selections to `http://localhost:8000/api/v1/word`
   - Check queue status at `http://localhost:8000/api/v1/queue/status`
   - Process queue with `POST http://localhost:8000/api/v1/queue/process`

## Configuration

Configuration is stored in `~/.config/sprachspiel/config.yaml`. Example:

```yaml
anki:
  mode: both  # connect | file | both
  connect:
    host: localhost
    port: 8765
  file:
    output_dir: ./output
    deck_name: Sprachspiel
  field_mapping:
    front: "${word}"
    back: |
      ${translation}

      <b>Definition:</b> ${definition}

      <b>Example:</b> ${example}
    audio: "[sound:${audio_file}.mp3]"
    tags: "${source_type} ${source_name}"

card_generation:
  mode: queue  # real-time | queue
  queue:
    auto_process: false
    batch_size: 10

dictionaries:
  - name: oxford
    module: dicts.oxford_api
    api_key: your_api_key

tts:
  - name: google
    module: tts.google_translate
    voice: en-US

ai:
  provider: openai
  api_key: your_openai_key
  model: gpt-4o-mini
  functions:
    translate:
      prompt: "Translate '${word}' to Chinese. Return only translation."
    example:
      prompt: "Generate a natural English sentence using '${word}'. Return only the sentence."

media:
  organization: hierarchical
  storage_dir: ./media
  screenshot_format: png
  audio_format: mp3
```

## CLI Commands

| Command | Description |
|----------|-------------|
| `sprachspiel start` | Start HTTP server |
| `sprachspiel process-queue` | Process all cards in queue |
| `sprachspiel export` | Export queue to .apkg file |
| `sprachspiel status` | Show connection and queue status |
| `sprachspiel config <key> [value]` | Get or set config values |
| `sprachspiel reload` | Reload configuration from file |

### Options

- `--config, -c <path>`: Use custom config file
- `--verbose, -v`: Enable verbose output
- `--debug`: Enable debug output

## HTTP API

### Endpoints

| Endpoint | Method | Description |
|----------|----------|-------------|
| `/api/v1/word` | POST | Create card from word selection |
| `/api/v1/queue/status` | GET | Get queue status and pending cards |
| `/api/v1/queue/process` | POST | Process all cards in queue |
| `/api/v1/queue/clear` | GET | Clear all cards from queue |
| `/api/v1/config` | GET | Get current configuration |
| `/api/v1/config/reload` | POST | Reload configuration |

### Example: Create Card

```bash
curl -X POST http://localhost:8000/api/v1/word \
  -H "Content-Type: application/json" \
  -d '{
    "word": "quick",
    "context": "The quick brown fox jumps over the lazy dog.",
    "source_type": "video",
    "source_name": "test.mp4",
    "position": "00:01:23"
  }'
```

### Example: Queue Status

```bash
curl http://localhost:8000/api/v1/queue/status
```

Response:
```json
{
  "size": 5,
  "cards": [
    {"id": "...", "word": "quick", "source_type": "video"},
    ...
  ]
}
```

## Data Sources

### Player Source (mpv Integration)

Integrate with mpv video player for subtitle-based card creation.

Features:
- Load video with subtitle file (SRT/VTT/ASS formats)
- Select words from subtitles in-player
- Automatic context extraction (current sentence)
- Screenshot capture at current timestamp
- Audio segment extraction

### Reader Source

Process PDF, EPUB, or plain text files.

Features:
- PDF parsing with page numbers (using pypdf)
- EPUB parsing with chapter info (using ebooklib)
- Text file parsing with line numbers
- Word selection and context extraction

### File Import

Import words from CSV or text files.

Features:
- CSV import with custom column mapping
- One-word-per-line text import
- Batch card creation

## Enhancement Services

### Dictionary Service

Look up words in configured dictionaries.

Built-in support:
- Oxford Dictionary API
- Youdao Dictionary API
- Custom modules

### TTS Service

Generate pronunciation audio.

Built-in support:
- Google Translate TTS (free)
- Azure TTS (requires API key)
- Custom modules

### AI Service

Use AI models for text generation.

Built-in support:
- OpenAI
- Anthropic
- Custom endpoints

Functions:
- Translation (configurable prompt)
- Example sentence generation (configurable prompt)
- Custom functions (user-defined)

## Development

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=sprachspiel --cov-report=html

# Format code
black sprachspiel tests

# Lint code
ruff check sprachspiel tests
```

## Project Structure

```
sprachspiel/
├── pyproject.toml
├── config.yaml
├── sprachspiel/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── core/
│   │   ├── card.py
│   │   ├── engine.py
│   │   ├── queue.py
│   │   └── mapper.py
│   ├── sources/
│   │   ├── base.py
│   │   ├── player.py
│   │   ├── reader.py
│   │   └── file_import.py
│   ├── services/
│   │   ├── dictionary.py
│   │   ├── tts.py
│   │   └── ai.py
│   ├── anki/
│   │   ├── base.py
│   │   ├── connect.py
│   │   └── file_export.py
│   ├── parsers/
│   │   ├── subtitle_base.py
│   │   ├── srt.py
│   │   ├── vtt.py
│   │   └── ass.py
│   └── server/
│       ├── app.py
│       └── routes.py
└── tests/
    ├── __init__.py
    ├── test_card.py
    ├── test_config.py
    └── test_engine.py
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
