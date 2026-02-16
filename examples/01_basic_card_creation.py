"""Example 1: Basic card creation and enhancement.

This example demonstrates how to create a CardData object and process it
through the CardEngine to generate a complete Anki card with enhancements.

Usage:
    python examples/01_basic_card_creation.py

Note: This example uses mock services. In production, you would configure
actual API keys for dictionary, AI, and TTS services.
"""

import asyncio
from datetime import UTC, datetime

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata, Media
from sprachspiel.core.engine import CardEngine


async def create_basic_card() -> None:
    """Create a basic card and process it through the engine."""
    print("=" * 60)
    print("Sprachspiel - Basic Card Creation Example")
    print("=" * 60)

    # Create a minimal configuration
    # In production, this would load from ~/.config/sprachspiel/config.yaml
    config_dict = {
        "anki": {
            "mode": "file",  # Use file export mode for this example
            "file": {"deck_name": "Example Deck"},
        },
        "card_generation": {
            "mode": "queue",  # Use queue mode for predictable behavior
        },
        # Services are not configured in this example
        "ai": {"api_key": ""},  # Empty API key = disabled
    }

    config = Config(config_dict)

    # Strong-typed configuration access
    print(f"Anki mode: {config.anki.mode}")
    print(f"Deck name: {config.anki.file.deck_name}")

    engine = CardEngine(config)

    # Create a CardData object
    # This represents the raw data for a single vocabulary card
    card_data = CardData(
        word="Serendipity",
        context="Finding something good without looking for it.",
        metadata=CardMetadata(
            source_type="example",
            source_name="basic_example.py",
            position="line 45",
            created_at=datetime.now(UTC),
        ),
        media=Media(),  # Media will be populated by TTS if enabled
    )

    print(f"\n1. Created CardData:")
    print(f"   Word: {card_data.word}")
    print(f"   Context: {card_data.context}")
    print(f"   Source: {card_data.metadata.source_name}")

    # Process the card through the engine
    # This applies enhancements (dictionary, AI, TTS) and maps to Anki fields
    print(f"\n2. Processing card through engine...")
    anki_card = await engine.generate_card(card_data)

    print(f"\n3. Generated AnkiCard:")
    print(f"   Deck: {anki_card.deck_name}")
    print(f"   Model: {anki_card.model_name}")
    print(f"   Tags: {anki_card.tags}")

    print(f"\n4. Fields:")
    for field_name, field_value in anki_card.fields.items():
        print(
            f"   {field_name}: {field_value[:50]}..."
            if len(field_value) > 50
            else f"   {field_name}: {field_value}"
        )

    print(f"\n5. Media files:")
    print(f"   Audio: {anki_card.audio_files}")
    print(f"   Images: {anki_card.image_files}")

    # In a real scenario, we would push the card to Anki
    # success = await engine.push_card(anki_card)
    # print(f"\n6. Push to Anki: {'Success' if success else 'Failed'}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(create_basic_card())
