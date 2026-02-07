## ADDED Requirements

### Requirement: Card generation supports real-time mode
The system SHALL support real-time card generation mode, where each selected word immediately generates a card and optionally pushes to Anki.

#### Scenario: Generate card in real-time mode with auto-push enabled
- **WHEN** user selects a word with real-time mode enabled and auto_push is true
- **THEN** system generates card immediately
- **AND** system pushes card to Anki immediately
- **AND** system confirms successful creation to user

#### Scenario: Generate card in real-time mode without auto-push
- **WHEN** user selects a word with real-time mode enabled and auto_push is false
- **THEN** system generates card immediately
- **AND** system stores card in local queue
- **AND** system confirms generation to user

### Requirement: Card generation supports queue mode
The system SHALL support queue mode, where cards are collected and processed in batches.

#### Scenario: Add card to queue
- **WHEN** user selects a word with queue mode enabled
- **THEN** system generates card data
- **AND** system adds card to pending queue
- **AND** system updates queue count

#### Scenario: Process queue with batch size
- **WHEN** user triggers queue processing with batch_size of 10 and queue has 15 cards
- **THEN** system processes first 10 cards
- **AND** system pushes 10 cards to Anki
- **AND** system keeps remaining 5 cards in queue

#### Scenario: Auto-process queue when threshold reached
- **WHEN** auto_process is true and queue reaches batch_size threshold
- **THEN** system automatically processes queue
- **AND** system pushes all cards to Anki
- **AND** system clears queue

### Requirement: Field mapping uses template variables
The system SHALL support configurable field mapping using template variables.

#### Scenario: Map card fields with template variables
- **WHEN** system generates card with field_mapping containing template variables like ${word}, ${context}, ${translation}
- **THEN** system substitutes variables with actual card data
- **AND** system generates properly formatted field values

#### Scenario: Handle missing template variables
- **WHEN** field template references ${undefined_var} that doesn't exist
- **THEN** system substitutes empty string for undefined variable
- **AND** system continues card generation

### Requirement: Duplicate words generate separate cards
The system SHALL generate separate cards for each occurrence of the same word.

#### Scenario: Same word appears multiple times in source
- **WHEN** word "quick" appears at 00:01:23 and 00:03:45 in subtitles
- **AND** user marks both occurrences
- **THEN** system generates two separate cards
- **AND** first card has timestamp 00:01:23
- **AND** second card has timestamp 00:03:45
- **AND** both cards contain respective contexts
