"""Example 5: Server API usage.

This example demonstrates how to interact with the Sprachspiel HTTP API
to create cards, manage the queue, and check status.

Usage:
    # First, start the server in another terminal:
    sprachspiel start

    # Then run this example:
    python examples/05_server_api_usage.py

Or programmatically start the server:
    python examples/05_server_api_usage.py --start-server
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import requests


def check_server_running(base_url: str = "http://localhost:8765") -> bool:
    """Check if the Sprachspiel server is running."""
    try:
        response = requests.get(f"{base_url}/api/v1/queue/status", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


def start_server() -> subprocess.Popen:
    """Start the Sprachspiel server."""
    print("Starting Sprachspiel server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "sprachspiel.cli", "start"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait for server to start
    for _ in range(10):
        time.sleep(0.5)
        if check_server_running():
            print("Server started successfully!")
            return process
    raise RuntimeError("Failed to start server")


def demonstrate_api(base_url: str = "http://localhost:8765") -> None:
    """Demonstrate the Sprachspiel HTTP API."""
    print("=" * 60)
    print("Sprachspiel - Server API Usage Example")
    print("=" * 60)

    # API endpoint base
    api_base = f"{base_url}/api/v1"

    print(f"\n1. Checking server status...")
    response = requests.get(f"{api_base}/queue/status")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    print(f"\n2. Creating a new card...")
    card_data = {
        "word": "Serendipity",
        "context": "Finding something good without looking for it.",
        "metadata": {
            "source_type": "api_example",
            "source_name": "05_server_api_usage.py",
            "position": "example 2",
        },
    }
    response = requests.post(f"{api_base}/word", json=card_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    print(f"\n3. Creating another card...")
    card_data2 = {
        "word": "Ephemeral",
        "context": "The beauty of cherry blossoms is ephemeral.",
        "metadata": {
            "source_type": "api_example",
            "source_name": "05_server_api_usage.py",
            "position": "example 3",
        },
    }
    response = requests.post(f"{api_base}/word", json=card_data2)
    print(f"   Status: {response.status_code}")
    print(f"   Card created: {response.json().get('word', 'N/A')}")

    print(f"\n4. Checking queue status...")
    response = requests.get(f"{api_base}/queue/status")
    queue_status = response.json()
    print(f"   Queue size: {queue_status.get('queue_size', 'N/A')}")
    print(f"   Is empty: {queue_status.get('is_empty', 'N/A')}")

    print(f"\n5. Getting current configuration...")
    response = requests.get(f"{api_base}/config")
    config_data = response.json()
    print(f"   Config keys: {list(config_data.keys())}")

    print(f"\n6. Processing the queue...")
    print(f"   (In real usage, this would process and push cards to Anki)")
    # Uncomment to actually process:
    # response = requests.post(f"{api_base}/queue/process")
    # print(f"   Result: {response.json()}")

    print(f"\n7. Clearing the queue...")
    response = requests.get(f"{api_base}/queue/clear")
    clear_result = response.json()
    print(f"   Cleared: {clear_result.get('cleared', 'N/A')} cards")

    print(f"\n8. Verifying queue is empty...")
    response = requests.get(f"{api_base}/queue/status")
    queue_status = response.json()
    print(f"   Queue size: {queue_status.get('queue_size', 'N/A')}")
    print(f"   Is empty: {queue_status.get('is_empty', 'N/A')}")

    print("\n" + "=" * 60)
    print("Server API usage example completed!")
    print("=" * 60)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Sprachspiel Server API Example")
    parser.add_argument(
        "--start-server",
        action="store_true",
        help="Start the server before running the example",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8765",
        help="Base URL for the Sprachspiel server",
    )
    args = parser.parse_args()

    server_process = None

    try:
        if args.start_server:
            server_process = start_server()
        elif not check_server_running(args.base_url):
            print("Error: Sprachspiel server is not running.")
            print(f"\nPlease start the server first:")
            print(f"  sprachspiel start")
            print(f"\nOr run this script with --start-server:")
            print(f"  python {__file__} --start-server")
            sys.exit(1)

        demonstrate_api(args.base_url)

    finally:
        if server_process:
            print("\nStopping server...")
            server_process.terminate()
            server_process.wait()


if __name__ == "__main__":
    main()
