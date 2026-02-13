"""Example 2: Batch processing with card queue.

This example demonstrates how to add multiple cards to a queue and
process them in batches. This is useful when you want to collect cards
over time and process them all at once.

Usage:
    python examples/02_batch_processing.py
"""

import asyncio
from datetime import UTC, datetime

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.core.engine import CardEngine
from sprachspiel.core.queue import CardQueue


async def demonstrate_batch_processing() -> None:
    """Demonstrate batch processing workflow."""
    print("=" * 60)
    print("Sprachspiel - Batch Processing Example")
    print("=" * 60)

    # Configuration
    config_dict = {
        "anki": {
            "mode": "file",
            "deck": "Vocabulary Deck",
            "model": "Basic (and reversed card)",
        },
        "card_generation": {
            "mode": "queue",  # Queue mode for batch processing
            "field_mapping": {
                "front": "${word}",
                "back": "${translation}",
            },
        },
        "dictionary": {"enabled": False},
        "ai": {"enabled": False},
        "tts": {"enabled": False},
    }

    config = Config(config_dict)
    engine = CardEngine(config)
    queue = CardQueue(config)

    # Sample vocabulary words to add to queue
    vocabulary = [
        {"word": "Ephemeral", "context": "Lasting for a very short time."},
        {"word": "Ubiquitous", "context": "Present, appearing, or found everywhere."},
        {"word": "Mellifluous", "context": "A sound that is sweet and musical."},
        {"word": "Luminous", "context": "Full of or shedding light."},
        {"word": "Resilient", "context": "Able to withstand or recover quickly."},
    ]

    print("\n1. Adding cards to queue...")
    for i, item in enumerate(vocabulary, 1):
        card_data = CardData(
            word=item["word"],
            context=item["context"],
            metadata=CardMetadata(
                source_type="batch_example",
                source_name="02_batch_processing.py",
                position=f"item {i}",
                created_at=datetime.now(UTC),
            ),
        )
        queue.add(card_data)
        print(f"   Added: {item['word']}")

    print(f"\n2. Queue status:")
    print(f"   Total cards in queue: {queue.size()}")
    print(f"   Is empty: {queue.is_empty()}")

    print(f"\n3. Processing queue in batches...")
    # Process the queue
    # Note: In a real scenario, this would process and push to Anki
    # For this example, we'll just demonstrate the flow

    batch_size = 3
    processed = 0
    total = queue.size()

    while not queue.is_empty():
        batch = queue.get_batch(batch_size)
        print(f"\n   Processing batch of {len(batch)} cards...")

        for card_data in batch:
            # Generate the card
            anki_card = await engine.generate_card(card_data)
            print(f"   - {anki_card.fields.get('front', 'N/A')}")
            processed += 1

        # In real usage: success = await engine.push_card(anki_card)
        # For demo, we remove from queue manually
        for card_data in batch:
            queue.remove(card_data.id)

    print(f"\n4. Processing complete!")
    print(f"   Processed: {processed}/{total} cards")

    print(f"\n5. Queue status after processing:")
    print(f"   Total cards in queue: {queue.size()}")
    print(f"   Is empty: {queue.is_empty()}")

    # Demonstrate saving and loading queue
    print(f"\n6. Demonstrating queue persistence...")
    # Add a card back for demo
    queue.add(CardData(word="Demo", context="Demo card", metadata=CardMetadata(
        source_type="demo", source_name="demo", created_at=datetime.now(UTC)
    )))
    queue.save()
    print(f"   Queue saved to: {queue.queue_file}")

    # Clear and reload
    queue.clear()
    print(f"   Queue cleared. Size: {queue.size()}")

    queue.load()
    print(f"   Queue reloaded. Size: {queue.size()}")

    print("\n" + "=" * 60)
    print("Batch processing example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demonstrate_batch_processing())
