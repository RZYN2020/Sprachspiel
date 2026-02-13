"""Example 6: End-to-end workflow demonstration.

This example demonstrates a complete workflow from importing vocabulary
from a file, processing through the card engine, and exporting to Anki.

Usage:
    python examples/06_end_to_end_workflow.py

Note: This example uses a mock configuration and does not require
actual Anki or API services.
"""

import asyncio
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from sprachspiel.anki.base import AnkiCard
from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.core.engine import CardEngine
from sprachspiel.core.queue import CardQueue
from sprachspiel.sources.file_import import FileImporter


async def run_end_to_end_workflow() -> None:
    """Run the complete end-to-end workflow."""
    print("=" * 70)
    print("Sprachspiel - End-to-End Workflow Demonstration")
    print("=" * 70)
    print()
    print("This example demonstrates the complete workflow:")
    print("1. Create vocabulary file")
    print("2. Import vocabulary from file")
    print("3. Add cards to processing queue")
    print("4. Process cards through the engine")
    print("5. Export to Anki package file")
    print()
    print("-" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        # =====================================================================
        # Step 1: Create vocabulary file
        # =====================================================================
        print("\n📄 STEP 1: Creating vocabulary file")
        print("-" * 40)

        vocab_file = temp_path / "german_vocabulary.csv"
        vocab_content = """word,translation,context,example
Hund,dog,Ein Haustier,Der Hund bellt laut.
Katze,cat,Ein Haustier,Die Katze schläft.
Vogel,bird,Ein Tier,Der Vogel singt.
Haus,house,Ein Gebäude,Das Haus ist groß.
Buch,book,Ein Gegenstand,Das Buch ist interessant.
"""
        vocab_file.write_text(vocab_content)

        print(f"Created: {vocab_file.name}")
        print(f"Location: {vocab_file}")
        print(f"Content preview:")
        for i, line in enumerate(vocab_content.strip().split("\n")[:4], 1):
            print(f"  {i}: {line[:60]}...")

        # =====================================================================
        # Step 2: Import vocabulary
        # =====================================================================
        print("\n📥 STEP 2: Importing vocabulary from file")
        print("-" * 40)

        config_dict = {
            "card_generation": {
                "field_mapping": {
                    "front": "${word}",
                    "back": "${translation}",
                }
            }
        }
        config = Config(config_dict)
        importer = FileImporter(config)

        cards = importer.import_file(vocab_file, format="csv")

        print(f"Imported {len(cards)} cards:")
        for i, card in enumerate(cards[:5], 1):
            print(f"  {i}. {card.word} = {card.translation}")
            if len(card.context) > 40:
                print(f"     Context: {card.context[:40]}...")
            else:
                print(f"     Context: {card.context}")

        # =====================================================================
        # Step 3: Add to processing queue
        # =====================================================================
        print("\n📋 STEP 3: Adding cards to processing queue")
        print("-" * 40)

        queue_config_dict = {
            "card_generation": {
                "mode": "queue",
                "queue": {
                    "storage_dir": str(temp_path / "queue"),
                    "auto_save": True,
                },
            }
        }
        queue_config = Config(queue_config_dict)
        queue = CardQueue(queue_config)

        print(f"Queue storage: {queue.queue_file}")
        print(f"Initial queue size: {queue.size()}")

        for card in cards:
            queue.add(card)

        print(f"Added {len(cards)} cards to queue")
        print(f"Current queue size: {queue.size()}")

        # Save queue
        queue.save()
        print("Queue saved to disk")

        # =====================================================================
        # Step 4: Process cards through engine
        # =====================================================================
        print("\n⚙️  STEP 4: Processing cards through the engine")
        print("-" * 40)

        engine_config_dict = {
            "anki": {
                "mode": "file",
                "deck": "German Vocabulary",
                "model": "Basic (and reversed card)",
            },
            "card_generation": {
                "mode": "realtime",
                "field_mapping": {
                    "German": "${word}",
                    "English": "${translation}",
                    "Context": "${context}",
                    "Full": "${word} = ${translation}",
                },
            },
            "dictionary": {"enabled": False},
            "ai": {"enabled": False},
            "tts": {"enabled": False},
        }
        engine_config = Config(engine_config_dict)
        engine = CardEngine(engine_config)

        # Reload queue with fresh instance
        fresh_queue = CardQueue(queue_config)
        fresh_queue.load()

        print(f"Loaded {fresh_queue.size()} cards from queue")
        print("\nProcessing cards:")

        anki_cards: list[AnkiCard] = []
        while not fresh_queue.is_empty():
            batch = fresh_queue.get_batch(2)
            print(f"\n  Processing batch of {len(batch)} cards...")

            for card_data in batch:
                anki_card = await engine.generate_card(card_data)
                anki_cards.append(anki_card)
                print(f"  ✓ {anki_card.fields.get('German', 'N/A')}")

        print(f"\nGenerated {len(anki_cards)} Anki cards")

        # Display sample output
        print("\nSample card output:")
        if anki_cards:
            sample = anki_cards[0]
            print(f"  Deck: {sample.deck_name}")
            print(f"  Model: {sample.model_name}")
            print(f"  Fields:")
            for field_name, field_value in sample.fields.items():
                print(f"    - {field_name}: {field_value}")

        # =====================================================================
        # Step 5: Export to Anki package
        # =====================================================================
        print("\n📦 STEP 5: Export to Anki package (demonstration)")
        print("-" * 40)

        export_dir = temp_path / "exports"
        export_dir.mkdir(exist_ok=True)

        # Note: In a real scenario, we would use FileExporter
        # For this demo, we just show the concept
        print(f"Export directory: {export_dir}")
        print(f"Cards ready for export: {len(anki_cards)}")

        # Create a summary file to demonstrate
        summary_file = export_dir / "export_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Sprachspiel Export Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total cards: {len(anki_cards)}\n")
            f.write(f"Deck: German Vocabulary\n")
            f.write(f"Model: Basic (and reversed card)\n\n")
            f.write("Cards:\n")
            for i, anki_card in enumerate(anki_cards, 1):
                f.write(f"  {i}. {anki_card.fields.get('German', 'N/A')}\n")

        print(f"Summary file created: {summary_file}")
        print(f"\nExport summary preview:")
        print(summary_file.read_text()[:500] + "...")

    # =====================================================================
    # Summary
    # =====================================================================
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  - Created vocabulary file with {len(cards)} entries")
    print(f"  - Imported and processed all cards")
    print(f"  - Generated Anki cards ready for export")
    print(f"\nFiles created in: {temp_path}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_end_to_end_workflow())
