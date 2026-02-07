## ADDED Requirements

### Requirement: Configuration is stored in YAML file
The system SHALL load all configuration from a YAML file.

#### Scenario: Load configuration from config.yaml
- **WHEN** system starts and config.yaml exists
- **THEN** system loads and parses YAML file
- **AND** system applies all configuration settings

#### Scenario: Use default configuration if file missing
- **WHEN** system starts and config.yaml does not exist
- **THEN** system uses default configuration values
- **AND** system generates example config.yaml file

### Requirement: Configuration supports Anki settings
The system SHALL support configurable Anki connection settings.

#### Scenario: Configure Anki connection mode
- **WHEN** config.yaml specifies anki.mode as "connect", "file", or "both"
- **THEN** system uses specified connection mode

#### Scenario: Configure AnkiConnect host and port
- **WHEN** config.yaml specifies anki.connect.host and anki.connect.port
- **THEN** system uses configured host and port for AnkiConnect connection

#### Scenario: Configure file export directory and deck name
- **WHEN** config.yaml specifies anki.file.output_dir and anki.file.deck_name
- **THEN** system uses configured output directory and deck name for file export

### Requirement: Configuration supports field mapping
The system SHALL support configurable field mapping templates.

#### Scenario: Configure field mapping
- **WHEN** config.yaml specifies anki.field_mapping with template variables
- **THEN** system loads field mapping templates
- **AND** system uses templates when generating card fields

### Requirement: Configuration supports dictionary sources
The system SHALL support configurable dictionary sources with module paths and API keys.

#### Scenario: Configure multiple dictionary sources
- **WHEN** config.yaml specifies dictionaries list with multiple sources
- **THEN** system loads all configured dictionary sources

### Requirement: Configuration supports TTS providers
The system SHALL support configurable TTS providers with module paths and settings.

#### Scenario: Configure TTS provider
- **WHEN** config.yaml specifies tts list with provider name and settings
- **THEN** system loads configured TTS provider

### Requirement: Configuration supports AI model settings
The system SHALL support configurable AI model provider, API key, and custom functions.

#### Scenario: Configure AI model
- **WHEN** config.yaml specifies ai.provider, ai.api_key, and ai.model
- **THEN** system uses configured AI provider and model

#### Scenario: Configure AI custom functions
- **WHEN** config.yaml specifies ai.functions with custom prompts
- **THEN** system loads custom function configurations

### Requirement: Configuration supports data sources
The system SHALL support configurable data sources with type-specific settings.

#### Scenario: Configure player data source
- **WHEN** config.yaml specifies source with type "player" and video/subtitle paths
- **THEN** system initializes player data source with configured paths

#### Scenario: Configure reader data source
- **WHEN** config.yaml specifies source with type "reader" and file path
- **THEN** system initializes reader data source with configured file

#### Scenario: Configure CSV import source
- **WHEN** config.yaml specifies source with type "csv" and column mapping
- **THEN** system initializes CSV importer with configured mapping

### Requirement: Configuration supports card generation mode
The system SHALL support configurable card generation mode settings.

#### Scenario: Configure real-time mode settings
- **WHEN** config.yaml specifies card_generation.mode as "real-time"
- **THEN** system enables real-time generation
- **AND** system applies auto_push setting if configured

#### Scenario: Configure queue mode settings
- **WHEN** config.yaml specifies card_generation.mode as "queue"
- **THEN** system enables queue mode
- **AND** system applies batch_size and auto_process settings

### Requirement: Configuration supports subtitle format
The system SHALL support configurable subtitle format for player data source.

#### Scenario: Configure subtitle format
- **WHEN** config.yaml specifies source.subtitle_format as "srt", "vtt", or "ass"
- **THEN** system uses appropriate subtitle parser

### Requirement: Configuration can be hot-reloaded
The system SHALL support reloading configuration without restart.

#### Scenario: Reload configuration
- **WHEN** user triggers configuration reload
- **THEN** system re-reads config.yaml
- **AND** system applies new configuration settings
- **AND** system maintains current operation state
