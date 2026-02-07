## Context

This is a new Python package for language learners to efficiently create Anki vocabulary cards while watching videos or reading content. The system needs to be cross-platform, highly configurable, and extensible to support various learning scenarios and user preferences.

**Target Users**:
- Language learners watching foreign language videos with subtitles
- Readers learning vocabulary from PDF/EPUB files
- Users studying from web content via browser

**Constraints**:
- Must be cross-platform (Windows, macOS, Linux)
- Configuration should be portable via YAML files
- Must work with Anki without modifying Anki itself (via AnkiConnect or file export)
- Should support offline operation (file export mode)

## Goals / Non-Goals

**Goals:**
- Provide unified interface for creating Anki cards from multiple data sources
- Support both real-time and batch card generation workflows
- Allow extensive customization via YAML configuration
- Enable extensibility for custom parsers, dictionaries, TTS, and AI functions
- Provide plugins for common platforms (Obsidian, browsers, video players)

**Non-Goals:**
- Creating a full-featured video player (will integrate with mpv)
- Creating a full-featured ebook reader (will integrate with existing tools or provide basic support)
- Modifying Anki itself
- Online account management or cloud sync (Anki handles sync)

## Decisions

### 1. Python Package Distribution
**Decision**: Distribute as a standard Python package via PyPI.

**Rationale**:
- Easy installation with `pip install sprachspiel`
- Can also be used as a library for other projects
- Familiar distribution method for Python users

**Alternatives Considered**:
- Single executable via PyInstaller: Harder to integrate with plugins, harder to maintain multiple plugins
- Docker container: Overkill for a CLI/desktop tool

### 2. HTTP Service Architecture
**Decision**: Use FastAPI for HTTP server that bridges between plugins and core functionality.

**Rationale**:
- FastAPI is fast, async, and has good documentation
- Provides automatic OpenAPI docs
- Easy to test
- Serves both browser plugins and mpv Lua script

**Alternatives Considered**:
- Flask: More mature but synchronous by default
- Flask-RESTful: Good structure but less modern than FastAPI

### 3. Player Integration Approach
**Decision**: Integrate with mpv via Lua script + HTTP communication.

**Rationale**:
- mpv has excellent Lua scripting capabilities
- Lua script runs within player, providing integrated UI
- HTTP communication aligns with browser plugin approach (unified architecture)
- Cross-platform

**Alternatives Considered**:
- Python-mpv library controlling external mpv: Requires separate UI, less integrated
- VLC Lua script: Weaker Lua API compared to mpv
- IINA (macOS only): Not cross-platform

### 4. Configuration Format
**Decision**: Use YAML for all configuration.

**Rationale**:
- Human-readable and writable
- Supports comments (good for documentation)
- Good Python library support (PyYAML)
- Portable across platforms

**Alternatives Considered**:
- TOML: Good but less widely used
- JSON: Doesn't support comments, less readable
- Python file: Too flexible, harder to validate

### 5. Card Generation Modes
**Decision**: Support both real-time and queue modes, configurable per user preference.

**Rationale**:
- Real-time mode: Immediate feedback, good for focused study sessions
- Queue mode: Batch processing, good for rapid content consumption
- User control allows different workflows

**Alternatives Considered**:
- Real-time only: Inefficient for bulk operations
- Queue only: No immediate feedback

### 6. Media Resource Strategy
**Decision**: Screenshot + original audio + TTS audio.

**Rationale**:
- Screenshot: Visual context, small file size
- Original audio: Authentic pronunciation with context
- TTS audio: Clear pronunciation for isolated word

**Alternatives Considered**:
- Video clips: Too large for Anki cards
- GIFs: Limited quality, no audio
- TTS only: Loses authentic context

### 7. Context Extraction Strategy
**Decision**: Extract complete current sentence as context.

**Rationale**:
- Provides semantic completeness
- Simple to implement with basic NLP
- Most users expect sentence-level context

**Alternatives Considered**:
- Fixed word window: May break semantic boundaries
- Time window: May include unrelated content
- Advanced NLP: Overkill, adds complexity

### 8. Duplicate Word Handling
**Decision**: Generate separate cards for each occurrence.

**Rationale**:
- Different contexts provide more learning value
- User can review/discard duplicates later if needed
- Simple, predictable behavior

**Alternatives Considered**:
- First occurrence only: Misses valuable context
- User selection: Adds complexity to workflow

### 9. Plugin Architecture
**Decision**:
- Python components: Use entry points for extensibility
- Subtitle parsers: Module-based, configured in YAML
- Enhancement services: Module-based with common interface
- External plugins (Obsidian, browser): Independent projects with HTTP communication

**Rationale**:
- Python entry points: Standard mechanism for Python package extensions
- Module-based parsing: Simple, configurable
- HTTP communication: Language-agnostic, works with any plugin

### 10. Anki Connection Strategy
**Decision**: Support both AnkiConnect and .apkg export, with option to use both simultaneously.

**Rationale**:
- AnkiConnect: Real-time integration, requires Anki running
- .apkg export: Offline support, cross-device compatibility
- Both mode: Maximum flexibility

**Alternatives Considered**:
- AnkiConnect only: No offline support
- .apkg only: No real-time feedback

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Layered Architecture                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Presentation Layer                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  CLI Tool   │  │ HTTP Server │  │ mpv Lua    │  │ Browser/     │         │
│  │  (click)   │  │  (FastAPI)  │  │  Script     │  │ Obsidian     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼─────────────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │                 │
          └─────────────────┴─────────────────┴─────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Service Layer                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Card Engine │  │ Data Source │  │ Enhancement │  │ Config      │         │
│  │             │  │  Manager    │  │  Services   │  │ Manager     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼─────────────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │                 │
          └─────────────────┴─────────────────┴─────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Integration Layer                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ AnkiConnect │  │ File Export │  │ mpv Control │  │ File Watcher│         │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Data Layer                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ config.yaml │  │ Queue Store │  │ Subtitle    │  │ Media Files │         │
│  │             │  │  (JSON/DB)  │  │  Parsers    │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Card Generation Flow (Real-Time Mode)

```
User Select Word
       │
       ▼
Data Source Captures (word, context, timestamp, media)
       │
       ▼
Card Engine Creates Card Data
       │
       ├─▶ Enhancement Services (Dictionary, TTS, AI)
       │       │
       │       └─▶ Enrich Card Data
       │
       ▼
Field Mapping Applied
       │
       ▼
Anki Connectivity Pushes Card
       │
       ▼
User Confirmation
```

### Card Generation Flow (Queue Mode)

```
User Select Word (Multiple Times)
       │
       ▼
Cards Added to Queue
       │
       ▼
User Triggers Processing (or auto-process threshold)
       │
       ▼
Batch Process Queue
       │
       ├─▶ Enhancement Services
       │
       ▼
Anki Connectivity Batch Push
       │
       ▼
Completion Report
```

## Project Structure

```
sprachspiel/
├── pyproject.toml
├── setup.py
├── README.md
├── config.yaml.template
│
├── anki_card_helper/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── card.py              # Card data model
│   │   ├── engine.py            # Card generation engine
│   │   ├── queue.py             # Queue management
│   │   └── mapper.py            # Field mapping
│   │
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── base.py              # Base source interface
│   │   ├── player.py            # mpv integration
│   │   ├── reader.py            # PDF/EPUB/Text reader
│   │   └── file_import.py       # CSV/text import
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── dictionary.py        # Dictionary service
│   │   ├── tts.py               # TTS service
│   │   └── ai.py                # AI model service
│   │
│   ├── anki/
│   │   ├── __init__.py
│   │   ├── base.py              # Base Anki connector
│   │   ├── connect.py           # AnkiConnect implementation
│   │   └── file_export.py       # .apkg export
│   │
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── subtitle_base.py     # Base subtitle parser
│   │   ├── srt.py
│   │   ├── vtt.py
│   │   └── ass.py
│   │
│   └── server/
│       ├── __init__.py
│       ├── app.py               # FastAPI application
│       └── routes.py           # API routes
│
├── plugins/
│   ├── obsidian/
│   │   ├── manifest.json
│   │   └── main.ts
│   │
│   └── browser/
│       ├── manifest.json
│       ├── popup.html
│       ├── popup.js
│       └── background.js
│
└── mpv-script/
    └── sprachspiel.lua     # mpv Lua script
```

## Risks / Trade-offs

### Risk 1: mpv Lua Script Compatibility
**Risk**: mpv Lua API may change across versions, breaking compatibility.

**Mitigation**:
- Pin mpv version requirements
- Document supported mpv versions
- Provide fallback error messages

### Risk 2: AnkiConnect Unavailable
**Risk**: AnkiConnect may not be installed or running, causing connection failures.

**Mitigation**:
- Provide clear error messages with setup instructions
- Support .apkg export as fallback
- Include connection health check in CLI

### Risk 3: External API Rate Limits
**Risk**: Dictionary/TTS/AI APIs may have rate limits, causing failures.

**Mitigation**:
- Implement retry logic with exponential backoff
- Support request queuing and throttling
- Document rate limits and recommend usage patterns

### Risk 4: Media File Bloat
**Risk**: Screenshots and audio files can accumulate, consuming significant disk space.

**Mitigation**:
- Provide cleanup utilities
- Support configurable media retention policy
- Document storage management

### Trade-off 1: Complexity vs. Flexibility
**Trade-off**: Highly configurable system increases complexity for new users.

**Mitigation**:
- Provide sensible defaults with minimal required configuration
- Include example config files with comments
- Provide configuration validation with helpful error messages

### Trade-off 2: Real-time vs. Performance
**Trade-off**: Real-time card generation with enhancement services can have noticeable latency.

**Mitigation**:
- Make enhancement services optional
- Support async/enhanced processing in background
- Provide progress feedback during long operations

## Migration Plan

Since this is a new package, no migration from previous versions is required.

### Installation Steps
1. User installs package: `pip install sprachspiel`
2. Package creates default config directory and template config
3. User configures config.yaml
4. For mpv integration, user installs mpv and places Lua script in mpv scripts directory
5. For browser integration, user installs browser extension
6. For Obsidian integration, user installs Obsidian plugin

### Rollback Strategy
- Uninstall package: `pip uninstall sprachspiel`
- Remove config directory and generated files
- Disable browser/Obsidian plugins

## Open Questions

1. **Queue Storage Format**: Should card queue be stored as JSON file or SQLite database?
   - JSON: Simple, human-readable, sufficient for small queues
   - SQLite: Better for large queues, more robust
   - **Recommendation**: Start with JSON, consider SQLite for future

2. **Media File Organization**: How should generated media files be organized?
   - Option A: Single directory with timestamp-based names
   - Option B: Organized by deck/source/date
   - **Recommendation**: Option B for better organization

3. **Error Handling for Failed Enhancements**: If dictionary/TTS/AI service fails, should card generation proceed?
   - **Recommendation**: Proceed with available data, log errors, offer retry option

4. **CLI vs. TUI vs. GUI**: What should the primary user interface be?
   - **Recommendation**: CLI as primary, HTTP server enables custom UIs
