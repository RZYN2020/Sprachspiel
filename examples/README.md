# Sprachspiel Examples

This directory contains example scripts demonstrating various use cases and workflows for the Sprachspiel library.

## Examples Overview

### 01_basic_card_creation.py
Demonstrates the basic workflow of creating a CardData object and processing it through the CardEngine to generate a complete Anki card with enhancements.

**Key concepts:**
- CardData creation
- CardEngine usage
- Field mapping
- AnkiCard generation

**Run:**
```bash
python examples/01_basic_card_creation.py
```

### 02_batch_processing.py
Demonstrates how to add multiple cards to a queue and process them in batches. This is useful when you want to collect cards over time and process them all at once.

**Key concepts:**
- CardQueue management
- Batch processing
- Queue persistence (save/load)
- Processing statistics

**Run:**
```bash
python examples/02_batch_processing.py
```

### 03_field_mapping.py
Demonstrates how to use field mapping with template variables to customize how card data is mapped to Anki fields.

**Key concepts:**
- Template variables (`${word}`, `${translation}`, etc.)
- HTML formatting in templates
- Custom data mapping
- Media references

**Run:**
```bash
python examples/03_field_mapping.py
```

### 04_file_import.py
Demonstrates how to import vocabulary from CSV/text files and process them into Anki cards.

**Key concepts:**
- FileImporter usage
- CSV/TSV/Wordlist formats
- Auto-detection of file formats
- Importing with translations

**Run:**
```bash
python examples/04_file_import.py
```

### 05_server_api_usage.py
Demonstrates how to interact with the Sprachspiel HTTP API to create cards, manage the queue, and check status.

**Key concepts:**
- HTTP API endpoints
- Queue management via API
- Card creation via API
- Server status checking

**Prerequisites:**
```bash
# Start the server in another terminal
sprachspiel start

# Or let the example start it
python examples/05_server_api_usage.py --start-server
```

**Run:**
```bash
# If server is already running
python examples/05_server_api_usage.py

# Or start server automatically
python examples/05_server_api_usage.py --start-server
```

### 06_end_to_end_workflow.py
A complete end-to-end workflow demonstration that combines all concepts: importing vocabulary, processing through the engine, and exporting to Anki.

**Key concepts:**
- Complete workflow
- File import
- Batch processing
- Card generation
- Export preparation

**Run:**
```bash
python examples/06_end_to_end_workflow.py
```

## Running All Examples

To run all examples at once:

```bash
# From the project root
for example in examples/0*.py; do
    echo "Running $example..."
    python "$example"
    echo ""
done
```

## Notes

- All examples use mock configurations and do not require actual API keys or Anki connection
- Examples create temporary files that are cleaned up automatically
- For production use, configure actual services (dictionary, AI, TTS) in your config file
