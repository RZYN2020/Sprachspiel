## 1. Project Setup

- [x] 1.1 Create Python package structure with pyproject.toml
- [x] 1.2 Add core dependencies (FastAPI, PyYAML, python-mpv, PyPDF2, ebooklib, requests)
- [x] 1.3 Set up development dependencies (pytest, black, ruff)
- [x] 1.4 Create default config.yaml template
- [x] 1.5 Implement config.py with YAML loading and validation
- [x] 1.6 Create CLI entry point using click
- [x] 1.7 Add version handling and package metadata

## 2. Core Card Engine

- [x] 2.1 Create Card data model in core/card.py
- [x] 2.2 Implement Card class with fields (word, context, media, metadata)
- [x] 2.3 Create core/engine.py with CardEngine class
- [x] 2.4 Implement real-time card generation
- [x] 2.5 Implement queue-based card generation
- [x] 2.6 Create core/queue.py for queue management
- [x] 2.7 Implement queue persistence (JSON storage)
- [x] 2.8 Implement batch processing with configurable batch size
- [x] 2.9 Implement auto-process trigger when threshold reached
- [x] 2.10 Create core/mapper.py for field mapping
- [x] 2.11 Implement template variable substitution in field mapper
- [x] 2.12 Handle missing template variables gracefully

## 3. Configuration Management

- [x] 3.1 Implement config loading from config.yaml
- [x] 3.2 Implement config validation with schema
- [x] 3.3 Generate default config.yaml if file missing
- [x] 3.4 Implement config hot-reload functionality
- [x] 3.5 Add config validation for Anki settings (mode, host, port)
- [x] 3.6 Add config validation for field mapping templates
- [x] 3.7 Add config validation for dictionary sources
- [x] 3.8 Add config validation for TTS providers
- [x] 3.9 Add config validation for AI model settings
- [x] 3.10 Add config validation for data sources
- [x] 3.11 Add config validation for card generation mode

## 4. Subtitle Processing

- [x] 4.1 Create base subtitle parser in parsers/subtitle_base.py
- [x] 4.2 Implement parsers/srt.py for SRT format
- [x] 4.3 Implement parsers/vtt.py for VTT format
- [x] 4.4 Implement parsers/ass.py for ASS/SSA format
- [x] 4.5 Implement subtitle entry parsing (timing and text)
- [x] 4.6 Implement multi-entry parsing with chronological ordering
- [x] 4.7 Implement timestamp-based entry lookup
- [x] 4.8 Implement sentence context extraction
- [x] 4.9 Add custom parser loading mechanism
- [x] 4.10 Implement encoding detection and handling (UTF-8, Latin-1)

## 5. Data Source Integration

- [x] 5.1 Create base data source interface in sources/base.py
- [x] 5.2 Implement sources/player.py for mpv integration
- [x] 5.3 Add mpv subprocess control and communication
- [x] 5.4 Implement video frame screenshot capture
- [x] 5.5 Implement audio segment extraction for subtitle sentences
- [x] 5.6 Create mpv Lua script for in-player UI
- [x] 5.7 Implement HTTP communication from Lua script to Python backend
- [x] 5.8 Implement sources/reader.py for PDF/EPUB/Text files
- [x] 5.9 Add PDF parsing with page numbers (PyPDF2)
- [x] 5.10 Add EPUB parsing with with chapter info (ebooklib)
- [x] 5.11 Add plain text file parsing with line numbers
- [x] 5.12 Implement file watcher for Obsidian plugin communication
- [x] 5.13 Implement sources/file_import.py for CSV and text imports
- [x] 5.14 Add CSV import with custom column mapping
- [x] 5.15 Add one-word-per-line text import
- [x] 5.16 Implement duplicate word handling (generate separate cards)

## 6. Enhancement Services

- [x] 6.1 Create base service interface in services/
- [x] 6.2 Implement services/dictionary.py
- [x] 6.3 Add Oxford dictionary API integration
- [x] 6.4 Add Youdao dictionary API integration
- [x] 6.5 Implement fallback to secondary dictionary source
- [x] 6.6 Add custom dictionary module loading
- [x] 6.7 Implement services/tts.py
- [x] 6.8 Add Azure TTS integration
- [x] 6.9 Add Google Translate TTS integration
- [x] 6.10 Implement TTS for both word and sentence context
- [x] 6.11 Add custom TTS module loading
- [x] 6.12 Implement services/ai.py
- [x] 6.13 Add OpenAI provider integration
- [x] 6.14 Add Anthropic provider integration
- [x] 6.15 Add custom endpoint support
- [x] 6.16 Implement translation function with custom prompt
- [x] 6.17 Implement example generation function with custom prompt
- [x] 6.18 Add custom AI function support
- [x] 6.19 Implement retry logic with exponential backoff
- [x] 6.20 Add request throttling support

## 7. Anki Connectivity

- [x] 7.1 Create base Anki connector in anki/base.py
- [x] 7.2 Implement anki/connect.py for AnkiConnect
- [x] 7.3 Add "addNote" request implementation
- [x] 7.4 Implement connection health check
- [x] 7.5 Handle AnkiConnect authentication
- [x] 7.6 Implement error handling and retry logic
- [x] 7.7 Implement anki/file_export.py for .apkg generation
- [x] 7.8 Add .apkg file creation with configured deck name
- [x] 7.9 Implement multi-deck export support
- [x] 7.10 Implement dual mode (both AnkiConnect and file export)

## 8. HTTP Server

- [x] 8.1 Create FastAPI application in server/app.py
- [x] 8.2 Implement server/routes.py with core API endpoints
- [x] 8.3 Add POST /word endpoint for word selection
- [x] 8.4 Add GET /queue/status endpoint
- [x] 8.5 Add POST /queue/process endpoint
- [x] 8.6 Add GET /config endpoint for config retrieval
- [x] 8.7 Add POST /config/reload endpoint for hot-reload
- [x] 8.8 Add CORS support for browser plugin
- [x] 8.9 Add API key authentication
- [x] 8.10 Implement WebSocket support for real-time updates

## 9. Browser Plugin

- [x] 9.1 Create browser extension manifest.json
- [x] 9.2 Create popup.html for extension UI
- [x] 9.3 Implement popup.js for word submission
- [x] 9.4 Implement background.js for service communication
- [x] 9.5 Add text selection detection
- [x] 9.6 Add context menu integration
- [x] 9.7 Add keyboard shortcut support
- [x] 9.8 Test on Chrome, Firefox, Edge

## 10. Obsidian Plugin

- [x] 10.1 Create Obsidian plugin manifest
- [x] 10.2 Implement main.ts plugin core
- [x] 10.3 Add word word selection and highlighting
- [x] 10.4 Implement marker file writing
- [x] 10.5 Add plugin settings panel
- [x] 10.6 Test plugin: with various note types

## 11. CLI Implementation

- [x] 11.1 Implement `sprachspiel start` command to launch HTTP server
- [x] 11.2 Implement `sprachspiel process-queue` command
- [x] 11.3 Implement `sprachspiel export` command
- [x] 11.4 Implement `sprachspiel config` command for config management
- [x] 11.5 Add `--config` flag for custom config path
- [x] 11.6 Add verbose/debug logging options
- [x] 11.7 Add connection status command

## 12. Testing

- [x] 12.1 Add unit tests for core/card.py
- [x] 12.2 Add unit tests for core/engine.py
- [x] 12.3 Add unit tests for core/queue.py
- [x] 12.4 Add unit tests for core/mapper.py
- [x] 12.5 Add unit tests for config.py
- [x] 12.6 Add unit tests for subtitle parsers (SRT, VTT, ASS)
- [x] 12.7 Add unit tests for field mapper
- [x] 12.8 Add integration tests for HTTP API
- [x] 12.9 Add integration tests for AnkiConnect
- [x] 12.10 Add tests for enhancement services
- [x] 12.11 Achieve minimum 80% code coverage

## 13. Documentation

- [x] 13.1 Write comprehensive README.md
- [x] 13.2 Document installation instructions
- [x] 13.3 Document configuration options with examples
- [x] 13.4 Document mpv Lua script installation
- [x] 13.5 Document browser plugin installation
- [x] 13.6 Document Obsidian plugin installation
- [x] 13.7 Add API documentation (OpenAPI/Redoc)
- [x] 13.8 Add troubleshooting guide
- [x] 13.9 Add example workflows

## 14. Packaging and Distribution

- [x] 14.1 Configure pyproject.toml for PyPI distribution
- [x] 14.2 Add package metadata and classifiers
- [x] 14.3 Create release notes
- [x] 14.4 Test package installation
- [~] 14.5 Publish to PyPI (test first, then production) - SKIPPED: Requires PyPI credentials; package is ready for manual upload
