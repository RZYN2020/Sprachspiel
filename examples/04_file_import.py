"""Example 4: File import and processing.

This example demonstrates how to import vocabulary from CSV/text files
and process them into Anki cards.

Usage:
    python examples/04_file_import.py

Note: This example creates temporary files for demonstration.
"""

import asyncio
import tempfile
from pathlib import Path

from sprachspiel.config import Config
from sprachspiel.sources.file_import import FileImporter


async def demonstrate_file_import() -> None:
    """Demonstrate importing vocabulary from files."""
    print("=" * 60)
    print("Sprachspiel - File Import Example")
    print("=" * 60)

    # Create temporary files for demonstration
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # 1. Simple word list (one word per line)
        wordlist_file = tmp_path / "vocabulary.txt"
        wordlist_file.write_text("""serendipity
ephemeral
mellifluous
resilient
luminous
""")

        print("\n1. Importing from simple word list:")
        print(f"   File: {wordlist_file}")
        print(f"   Content preview:")
        print("   " + "\n   ".join(wordlist_file.read_text().strip().split("\n")[:3]))

        # 2. CSV file with context
        csv_file = tmp_path / "vocabulary.csv"
        csv_file.write_text("""word,context
cat,A small domesticated carnivorous mammal.
dog,A domesticated carnivorous mammal.
bird,A warm-blooded egg-laying vertebrate.
""")

        print("\n2. Importing from CSV file:")
        print(f"   File: {csv_file}")
        print(f"   Content:")
        print("   " + "\n   ".join(csv_file.read_text().strip().split("\n")))

        # 3. Tab-separated file with translations
        tsv_file = tmp_path / "vocabulary.tsv"
        tsv_file.write_text("""word\ttranslation\tcontext
Hund\tdog\tEin Haustier
Katze\tcat\tEin Haustier
Vogel\tbird\tEin Tier
""")

        print("\n3. Importing from TSV file:")
        print(f"   File: {tsv_file}")
        print(f"   Content:")
        print("   " + "\n   ".join(tsv_file.read_text().strip().split("\n")[:2]))
        print("   ...")

        # Initialize file importer
        config_dict = {
            "card_generation": {
                "field_mapping": {
                    "front": "${word}",
                    "back": "${context}",
                }
            }
        }
        config = Config(config_dict)
        importer = FileImporter(config)

        # Import from word list
        print("\n4. Processing word list:")
        cards = importer.import_file(wordlist_file, format="wordlist")
        print(f"   Imported {len(cards)} cards")
        for card in cards[:3]:
            print(f"   - {card.word}")

        # Import from CSV
        print("\n5. Processing CSV file:")
        cards = importer.import_file(csv_file, format="csv")
        print(f"   Imported {len(cards)} cards")
        for card in cards:
            print(f"   - {card.word}: {card.context[:40]}...")

        # Import from TSV
        print("\n6. Processing TSV file:")
        cards = importer.import_file(tsv_file, format="tsv")
        print(f"   Imported {len(cards)} cards")
        for card in cards:
            print(f"   - {card.word} ({card.translation})")

        # Demonstrate auto-detection
        print("\n7. Auto-detecting file formats:")
        for file_path in [wordlist_file, csv_file, tsv_file]:
            detected_format = importer.detect_format(file_path)
            cards = importer.import_file(file_path)  # Auto-detect
            print(f"   {file_path.name} -> {detected_format}: {len(cards)} cards")

    print("\n" + "=" * 60)
    print("File import example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demonstrate_file_import())
