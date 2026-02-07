## ADDED Requirements

### Requirement: Subtitle parser extracts timing and text
The system SHALL parse subtitle files and extract timing information and text content.

#### Scenario: Parse SRT subtitle entry
- **WHEN** SRT parser processes entry "00:01:23,000 --> 00:01:28,000\nHello world"
- **THEN** system extracts start time 00:01:23
- **AND** system extracts end time 00:01:28
- **AND** system extracts text "Hello world"

#### Scenario: Parse VTT subtitle entry
- **WHEN** VTT parser processes entry "00:01:23.000 --> 00:01:28.000\nHello world"
- **THEN** system extracts start time 00:01:23
- **AND** system extracts end time 00:01:28
- **AND** system extracts text "Hello world"

#### Scenario: Parse ASS subtitle entry
- **WHEN** ASS parser processes entry with "Start: 1234, End: 2345, Text: Hello world"
- **THEN** system extracts start time from timestamp
- **AND** system extracts end time from timestamp
- **AND** system extracts text from Text field

### Requirement: Subtitle parser handles multiple entries
The system SHALL parse subtitle files with multiple entries.

#### Scenario: Parse subtitle file with multiple entries
- **WHEN** subtitle file contains 10 entries
- **THEN** system parses all 10 entries
- **AND** system maintains chronological order
- **AND** system stores all entries for lookup

### Requirement: Subtitle parser supports word lookup
The system SHALL support looking up which subtitle entry contains a word at a specific timestamp.

#### Scenario: Find subtitle entry by timestamp
- **WHEN** user selects word at timestamp 00:01:25
- **THEN** system finds subtitle entry containing timestamp 00:01:25
- **AND** system returns entry with text and timing

### Requirement: Subtitle parser extracts sentence context
The system SHALL extract the complete sentence containing a selected word.

#### Scenario: Extract sentence from subtitle entry
- **WHEN** subtitle entry contains "The quick brown fox jumps over the lazy dog."
- **AND** user selects word "quick"
- **THEN** system returns complete sentence "The quick brown fox jumps over the lazy dog."

### Requirement: Subtitle parser is extensible
The system SHALL support adding custom subtitle parsers for new formats.

#### Scenario: Use custom subtitle parser
- **WHEN** user configures custom subtitle parser module in config.yaml
- **THEN** system loads custom parser module
- **AND** system uses custom parser for specified format

### Requirement: Subtitle parser handles encoding issues
The system SHALL handle different text encodings in subtitle files.

#### Scenario: Parse UTF-8 subtitle file
- **WHEN** subtitle file is encoded in UTF-8
- **THEN** system correctly parses text with Unicode characters

#### Scenario: Parse non-UTF-8 subtitle file
- **WHEN** subtitle file is encoded in Latin-1 or other encoding
- **THEN** system detects encoding
- **AND** system correctly parses text
