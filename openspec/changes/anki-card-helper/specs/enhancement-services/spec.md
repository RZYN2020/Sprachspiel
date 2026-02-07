## ADDED Requirements

### Requirement: Dictionary service supports multiple sources
The system SHALL support querying multiple dictionary sources configured in config.yaml.

#### Scenario: Query dictionary with configured source
- **WHEN** user requests dictionary lookup for word "quick" with "oxford" source configured
- **THEN** system queries Oxford dictionary API
- **AND** system returns definition, part of speech, and example sentence

#### Scenario: Fallback to secondary dictionary source
- **WHEN** primary dictionary source fails and secondary source is configured
- **THEN** system queries secondary dictionary source
- **AND** system returns results from secondary source

### Requirement: Dictionary service supports custom sources
The system SHALL allow users to add custom dictionary source modules.

#### Scenario: Use custom dictionary module
- **WHEN** user configures custom dictionary module path
- **THEN** system loads custom module
- **AND** system uses custom module for dictionary queries

### Requirement: TTS service supports multiple providers
The system SHALL support multiple TTS providers for generating pronunciation audio.

#### Scenario: Generate TTS audio with configured provider
- **WHEN** TTS is enabled and Azure provider is configured
- **THEN** system calls Azure TTS API with word and voice settings
- **AND** system saves audio file
- **AND** system returns audio file path

#### Scenario: Generate TTS for word and sentence
- **WHEN** TTS is configured for both word and context
- **THEN** system generates audio for word
- **AND** system generates audio for sentence context
- **AND** system returns both audio file paths

### Requirement: TTS service supports custom providers
The system SHALL allow users to add custom TTS provider modules.

#### Scenario: Use custom TTS module
- **WHEN** user configures custom TTS module path
- **THEN** system loads custom module
- **AND** system uses custom module for TTS generation

### Requirement: AI model service supports custom functions
The system SHALL support configurable AI functions for translation, example generation, and other custom tasks.

#### Scenario: AI translates word to Chinese
- **WHEN** AI translation function is configured with prompt template
- **THEN** system replaces ${word} in prompt with actual word
- **AND** system calls AI model API
- **AND** system returns translation result

#### Scenario: AI generates example sentence
- **WHEN** AI example generation function is configured
- **THEN** system sends word to AI model with configured prompt
- **AND** system returns generated example sentence

#### Scenario: AI executes custom function
- **WHEN** user configures custom AI function with custom prompt
- **THEN** system sends word to AI model with custom prompt
- **AND** system returns result
- **AND** result is available as template variable in field mapping

### Requirement: AI model service supports multiple providers
The system SHALL support multiple AI model providers (OpenAI, Anthropic, local models, custom endpoints).

#### Scenario: Use OpenAI provider
- **WHEN** AI provider is configured as "openai" with API key and model
- **THEN** system calls OpenAI API with configured settings

#### Scenario: Use custom endpoint
- **WHEN** AI provider is configured with custom base_url and API key
- **THEN** system calls custom endpoint with standard API format
