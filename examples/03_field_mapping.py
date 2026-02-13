"""Example 3: Field mapping and template variables.

This example demonstrates how to use field mapping with template variables
to customize how card data is mapped to Anki fields.

Usage:
    python examples/03_field_mapping.py
"""

import asyncio
from datetime import UTC, datetime

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata, Media
from sprachspiel.core.mapper import FieldMapper


async def demonstrate_field_mapping() -> None:
    """Demonstrate various field mapping configurations."""
    print("=" * 60)
    print("Sprachspiel - Field Mapping Example")
    print("=" * 60)

    # Sample card data
    card_data = CardData(
        word="Eloquent",
        context="She gave an eloquent speech.",
        translation="口才好的，雄辩的",
        definition="Fluent or persuasive in speaking or writing.",
        example="The lawyer's eloquent argument won the case.",
        metadata=CardMetadata(
            source_type="example",
            source_name="field_mapping_demo",
            position="page 1",
            created_at=datetime.now(UTC),
        ),
        media=Media(
            screenshot="/path/to/screenshot.png",
            audio_word="/path/to/word.mp3",
        ),
        custom_data={
            "part_of_speech": "adjective",
            "difficulty": "intermediate",
        },
    )

    print("\n1. Sample Card Data:")
    print(f"   Word: {card_data.word}")
    print(f"   Context: {card_data.context}")
    print(f"   Translation: {card_data.translation}")
    print(f"   Definition: {card_data.definition}")
    print(f"   Example: {card_data.example}")
    print(f"   Custom Data: {card_data.custom_data}")

    # Configuration 1: Basic mapping
    print("\n" + "-" * 60)
    print("2. Basic Field Mapping (Simple)")
    print("-" * 60)

    config_dict = {
        "card_generation": {
            "field_mapping": {
                "front": "${word}",
                "back": "${translation}",
            }
        }
    }
    config = Config(config_dict)
    mapper = FieldMapper(config)
    anki_card = mapper.map_card(card_data)

    print(f"   Front: {anki_card.fields['front']}")
    print(f"   Back: {anki_card.fields['back']}")

    # Configuration 2: Rich mapping with HTML
    print("\n" + "-" * 60)
    print("3. Rich Field Mapping (HTML formatted)")
    print("-" * 60)

    config_dict = {
        "card_generation": {
            "field_mapping": {
                "front": "<h2>${word}</h2><p>${context}</p>",
                "back": """<h3>${translation}</h3>
<p><strong>Definition:</strong> ${definition}</p>
<p><strong>Example:</strong> ${example}</p>""",
            }
        }
    }
    config = Config(config_dict)
    mapper = FieldMapper(config)
    anki_card = mapper.map_card(card_data)

    print(f"   Front:")
    print(f"   {anki_card.fields['front']}")
    print(f"\n   Back:")
    print(f"   {anki_card.fields['back']}")

    # Configuration 3: With media references
    print("\n" + "-" * 60)
    print("4. Mapping with Media References")
    print("-" * 60)

    config_dict = {
        "card_generation": {
            "field_mapping": {
                "word": "${word}",
                "context": "${context}",
                "translation": "${translation}",
                # Media paths are also available as template variables
                "screenshot": "${media.screenshot}",
                "audio": "${media.audio_word}",
            }
        }
    }
    config = Config(config_dict)
    mapper = FieldMapper(config)
    anki_card = mapper.map_card(card_data)

    print("   Mapped Fields:")
    for field_name, field_value in anki_card.fields.items():
        print(f"   - {field_name}: {field_value}")

    # Configuration 4: Custom data mapping
    print("\n" + "-" * 60)
    print("5. Mapping with Custom Data")
    print("-" * 60)

    config_dict = {
        "card_generation": {
            "field_mapping": {
                "word": "${word}",
                "part_of_speech": "${custom.part_of_speech}",
                "difficulty": "${custom.difficulty}",
                # Nested custom data
                "full_info": "${word} (${custom.part_of_speech}) - Difficulty: ${custom.difficulty}",
            }
        }
    }
    config = Config(config_dict)
    mapper = FieldMapper(config)
    anki_card = mapper.map_card(card_data)

    print("   Mapped Fields with Custom Data:")
    for field_name, field_value in anki_card.fields.items():
        print(f"   - {field_name}: {field_value}")

    # Demonstrate media file handling
    print("\n" + "-" * 60)
    print("6. Media Files in AnkiCard")
    print("-" * 60)

    print(f"   Audio files: {anki_card.audio_files}")
    print(f"   Image files: {anki_card.image_files}")
    print(f"   Tags: {anki_card.tags}")

    print("\n" + "=" * 60)
    print("Field mapping example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demonstrate_field_mapping())
