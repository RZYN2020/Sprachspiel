## ADDED Requirements

### Requirement: Player data source supports subtitle parsing
The system SHALL integrate with video player (mpv) and parse subtitle files to extract context and timing information.

#### Scenario: Parse SRT subtitle file
- **WHEN** player data source loads video with SRT subtitle file
- **THEN** system parses subtitle entries with timing and text
- **AND** system extracts sentence context for selected words

#### Scenario: Parse VTT subtitle file
- **WHEN** player data source loads video with VTT subtitle file
- **THEN** system parses subtitle entries with timing and text

#### Scenario: Parse ASS subtitle file
- **WHEN** player data source loads video with ASS subtitle file
- **THEN** system parses subtitle entries with timing and text

### Requirement: Player data source captures video frame screenshot
The system SHALL capture screenshot of video frame at current timestamp when word is selected.

#### Scenario: Capture screenshot at current timestamp
- **WHEN** user selects word at timestamp 00:01:23
- **THEN** system captures video frame at 00:01:23
- **AND** system saves screenshot as image file
- **AND** system includes screenshot file path in card data

### Requirement: Player data source captures audio segment
The system SHALL capture audio segment for current sentence when word is selected.

#### Scenario: Capture audio segment for sentence
- **WHEN** user selects word and audio capture is enabled
- **THEN** system extracts audio for subtitle sentence timestamp range
- **AND** system saves audio as MP3 file
- **AND** system includes audio file path in card data

### Requirement: Reader data source supports PDF files
The system SHALL support reading PDF files and extracting text with page numbers.

#### Scenario: Extract word context from PDF
- **WHEN** user selects word in PDF reader
- **THEN** system extracts sentence containing the word
- **AND** system records page number
- **AND** system includes page number in card metadata

### Requirement: Reader data source supports EPUB files
The system SHALL support reading EPUB files and extracting text with chapter/page information.

#### Scenario: Extract word context from EPUB
- **WHEN** user selects word in EPUB reader
- **THEN** system extracts sentence containing the word
- **AND** system records chapter name and location
- **AND** system includes chapter info in card metadata

### Requirement: Reader data source supports plain text files
The system SHALL support reading plain text files and extracting text with line numbers.

#### Scenario: Extract word context from text file
- **WHEN** user selects word in text file
- **THEN** system extracts sentence containing the word
- **AND** system records line number
- **AND** system includes line number in card metadata

### Requirement: Browser plugin communicates via HTTP
The system SHALL provide HTTP API for browser plugin to send word selections and receive responses.

#### Scenario: Browser plugin sends word selection
- **WHEN** browser plugin POSTs word selection to HTTP endpoint
- **THEN** system processes word selection
- **AND** system returns success response with card preview

#### Scenario: Browser plugin requests card queue status
- **WHEN** browser plugin GETs queue status endpoint
- **THEN** system returns current queue count and pending items

### Requirement: Obsidian plugin communicates via file
The system SHALL support receiving word selections from Obsidian plugin via local file.

#### Scenario: Obsidian plugin writes to marker file
- **WHEN** Obsidian plugin writes word selection to marker file
- **THEN** system watches file and processes new entries
- **AND** system generates cards from entries

### Requirement: CSV import supports custom column mapping
The system SHALL support importing words from CSV files with custom column mapping.

#### Scenario: Import CSV with column mapping
- **WHEN** user imports CSV file with column mapping configured (word: 0, context: 1)
- **THEN** system reads CSV rows
- **AND** system extracts word from column 0
- **AND** system extracts context from column 1
- **AND** system generates cards for each row

### Requirement: Text file import supports one word per line
The system SHALL support importing words from text files with one word per line.

#### Scenario: Import text file with one word per line
- **WHEN** user imports text file with one_word_per_line enabled
- **THEN** system reads each line as a word
- **AND** system generates cards for each word
