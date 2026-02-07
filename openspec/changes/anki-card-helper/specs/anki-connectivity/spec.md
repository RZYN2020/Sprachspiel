## ADDED Requirements

### Requirement: AnkiConnect mode supports real-time card push
The system SHALL support pushing cards to Anki via AnkiConnect HTTP API.

#### Scenario: Push card to Anki via AnkiConnect
- **WHEN** Anki mode is configured as "connect" and card is ready
- **THEN** system establishes connection to AnkiConnect at configured host:port
- **AND** system sends "addNote" request with deck name, model, and fields
- **AND** system handles success response
- **AND** system returns note ID

#### Scenario: Handle AnkiConnect connection failure
- **WHEN** AnkiConnect is not running or connection fails
- **THEN** system logs error message
- **AND** system queues card for retry
- **AND** system notifies user of failure

#### Scenario: Handle AnkiConnect authentication
- **WHEN** AnkiConnect requires authentication
- **THEN** system includes API key in request
- **AND** system processes authenticated requests

### Requirement: File export mode supports .apkg generation
The system SHALL support exporting cards as .apkg (Anki package) files.

#### Scenario: Export cards as .apkg file
- **WHEN** Anki mode is configured as "file" and cards are ready
- **THEN** system generates .apkg file with configured deck name
- **AND** system saves file to configured output directory
- **AND** system returns file path

#### Scenario: Export multiple decks
- **WHEN** file export is configured with multiple deck names
- **THEN** system generates .apkg file containing all specified decks

### Requirement: Dual mode supports both AnkiConnect and file export
The system SHALL support "both" mode to simultaneously push via AnkiConnect and export to file.

#### Scenario: Push and export in dual mode
- **WHEN** Anki mode is configured as "both"
- **THEN** system pushes card via AnkiConnect
- **AND** system exports card to file
- **AND** system reports status of both operations

### Requirement: Anki connectivity supports custom deck and model
The system SHALL allow users to specify custom deck name and note model.

#### Scenario: Use custom deck and model
- **WHEN** user configures custom deck_name and model in anki config
- **THEN** system uses configured deck name when pushing cards
- **AND** system uses configured model when pushing cards
