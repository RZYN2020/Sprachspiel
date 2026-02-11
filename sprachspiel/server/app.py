"""FastAPI application for Sprachspiel server."""

from datetime import datetime
from typing import Any

import fastapi
from fastapi import APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.core.engine import CardEngine
from sprachspiel.core.queue import CardQueue


# Pydantic models for API
class WordRequest(BaseModel):
    """Request model for word submission."""

    word: str = Field(..., description="Word or phrase to create card for")
    context: str | None = Field(None, description="Context sentence or text")
    source_type: str | None = Field(None, description="Source type (video, pdf, epub, text, web)")
    source_name: str | None = Field(None, description="Source file name or URL")
    position: str | None = Field(None, description="Position (timestamp, page, line)")
    screenshot: str | None = Field(None, description="Base64 encoded screenshot")
    audio: str | None = Field(None, description="Path or base64 encoded audio")


class QueueStatusResponse(BaseModel):
    """Response model for queue status."""

    size: int = Field(..., description="Number of cards in queue")
    cards: list[dict[str, Any]] = Field(..., description="List of queued cards (summary)")


class CardResponse(BaseModel):
    """Response model for card operations."""

    success: bool = Field(..., description="Operation success status")
    card_id: str | None = Field(None, description="Card ID")
    message: str | None = Field(None, description="Error message if failed")


class ConfigResponse(BaseModel):
    """Response model for configuration."""

    anki_mode: str
    card_generation_mode: str
    queue_size: int


# API key dependency (simple implementation)
async def verify_api_key(_x_api_key: str | None = None) -> bool:
    """Verify API key (placeholder)."""
    # TODO: Implement proper API key verification
    return True


def create_app(config: Config) -> fastapi.FastAPI:
    """Create FastAPI application.

    Args:
        config: Configuration instance.

    Returns:
        Configured FastAPI application.
    """
    app = fastapi.FastAPI(
        title="Sprachspiel API",
        description="Anki card generation assistant API",
        version="0.1.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure specific origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create routers
    router = APIRouter(prefix="/api/v1")
    _setup_routes(router, config)

    app.include_router(router)

    # Root endpoint
    @app.get("/")
    def root() -> dict[str, Any]:  # type: ignore[misc]
        """Root endpoint."""
        return {
            "name": "Sprachspiel",
            "version": "0.1.0",
            "description": "Anki card generation assistant",
            "endpoints": {
                "word": "/api/v1/word",
                "queue": "/api/v1/queue",
                "config": "/api/v1/config",
            },
        }

    return app


def _setup_routes(router: APIRouter, config: Config) -> None:
    """Setup API routes.

    Args:
        router: API router.
        config: Configuration instance.
    """
    # Initialize components
    queue = CardQueue(config)
    engine = CardEngine(config)

    @router.post("/word", response_model=CardResponse)  # type: ignore[misc]
    async def create_card(
        request: WordRequest, api_key_valid: bool = Depends(verify_api_key)
    ) -> CardResponse:
        """Create card from word selection.

        Args:
            request: Word request data.
            api_key_valid: API key verification result.

        Returns:
            Card creation response.
        """
        if not api_key_valid:
            raise HTTPException(status_code=401, detail="Invalid API key")

        try:
            # Create card data
            card_data = CardData(
                word=request.word,
                context=request.context or request.word,
                metadata=CardMetadata(
                    source_type=request.source_type or "unknown",
                    source_name=request.source_name or "unknown",
                    position=request.position,
                ),
            )

            # Handle media from request
            if request.screenshot:
                card_data.media.screenshot = _save_base64_image(
                    request.screenshot, config
                )
            if request.audio:
                card_data.media.audio_word = _save_base64_audio(request.audio, config)

            # Check card generation mode
            mode = config.get("card_generation.mode", "queue")

            if mode == "real-time":
                # Generate and push immediately
                anki_card = await engine.generate_card(card_data)
                pushed = await engine.push_card(anki_card)

                if pushed:
                    return CardResponse(success=True, card_id=card_data.id)  # type: ignore[call-arg]
                else:
                    return CardResponse(
                        success=False,
                        message="Failed to push card to Anki",  # type: ignore[call-arg]
                    )
            else:
                # Add to queue
                queue.add(card_data)

                # Check auto-process
                auto_process = config.get("card_generation.queue.auto_process", False)
                batch_size = config.get("card_generation.queue.batch_size", 10)

                if auto_process and queue.size() >= batch_size:
                    success_count, total = await engine.process_queue()
                    return CardResponse(
                        success=True,
                        message=f"Processed {success_count}/{total} cards",  # type: ignore[call-arg]
                    )

                return CardResponse(success=True, card_id=card_data.id)  # type: ignore[call-arg]

        except Exception as e:
            return CardResponse(success=False, message=str(e))  # type: ignore[call-arg]

    @router.get("/queue/status", response_model=QueueStatusResponse)  # type: ignore[misc]
    async def get_queue_status(
        api_key_valid: bool = Depends(verify_api_key)
    ) -> QueueStatusResponse:
        """Get queue status.

        Args:
            api_key_valid: API key verification result.

        Returns:
            Queue status response.
        """
        if not api_key_valid:
            raise HTTPException(status_code=401, detail="Invalid API key")

        cards = queue.get_all()
        card_summaries: list[dict[str, Any]] = [
            {
                "id": card.id,
                "word": card.word,
                "source_type": card.metadata.source_type,
            }
            for card in cards
        ]

        return QueueStatusResponse(size=queue.size(), cards=card_summaries)

    @router.post("/queue/process")  # type: ignore[misc]
    async def process_queue(
        api_key_valid: bool = Depends(verify_api_key)
    ) -> dict[str, Any]:
        """Process all cards in queue.

        Args:
            api_key_valid: API key verification result.

        Returns:
            Process result.
        """
        if not api_key_valid:
            raise HTTPException(status_code=401, detail="Invalid API key")

        if queue.is_empty():
            return {"success": True, "message": "Queue is empty"}

        success_count, total = await engine.process_queue()

        return {
            "success": True,
            "message": f"Processed {success_count}/{total} cards",
        }

    @router.get("/queue/clear")  # type: ignore[misc]
    async def clear_queue(
        api_key_valid: bool = Depends(verify_api_key)
    ) -> dict[str, Any]:
        """Clear all cards from queue.

        Args:
            api_key_valid: API key verification result.

        Returns:
            Clear result.
        """
        if not api_key_valid:
            raise HTTPException(status_code=401, detail="Invalid API key")

        size = queue.size()
        queue.clear()

        return {
            "success": True,
            "message": f"Cleared {size} cards from queue",
        }

    @router.get("/config", response_model=ConfigResponse)  # type: ignore[misc]
    async def get_config(
        api_key_valid: bool = Depends(verify_api_key)
    ) -> ConfigResponse:
        """Get current configuration.

        Args:
            api_key_valid: API key verification result.

        Returns:
            Configuration response.
        """
        if not api_key_valid:
            raise HTTPException(status_code=401, detail="Invalid API key")

        return ConfigResponse(
            anki_mode=config.get("anki.mode", "both"),
            card_generation_mode=config.get("card_generation.mode", "queue"),
            queue_size=queue.size(),
        )

    @router.post("/config/reload")  # type: ignore[misc]
    async def reload_config(
        api_key_valid: bool = Depends(verify_api_key)
    ) -> dict[str, Any]:
        """Reload configuration from file.

        Args:
            api_key_valid: API key verification result.

        Returns:
            Reload result.
        """
        if not api_key_valid:
            raise HTTPException(status_code=401, detail="Invalid API key")

        config.reload()

        return {
            "success": True,
            "message": "Configuration reloaded",
        }


def _save_base64_image(data: str, config: Config) -> str | None:
    """Save base64 encoded image to file.

    Args:
        data: Base64 encoded image data.
        config: Configuration instance.

    Returns:
        Path to saved image file, or None if invalid.
    """
    import base64
    from pathlib import Path

    try:
        # Handle data URL scheme
        if "," in data:
            _header, image_data = data.split(",", 1)
        else:
            image_data = data

        # Decode
        decoded = base64.b64decode(image_data)

        # Determine format from header or config
        format = config.get("media.screenshot_format", "png")

        # Create media directory
        media_dir = Path(config.get("media.storage_dir", "./media"))
        media_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"screenshot_{timestamp}.{format}"
        filepath = media_dir / filename

        with open(filepath, "wb") as f:
            f.write(decoded)

        return str(filepath)
    except Exception:
        return None


def _save_base64_audio(data: str, config: Config) -> str | None:
    """Save base64 encoded audio to file.

    Args:
        data: Base64 encoded audio data or file path.
        config: Configuration instance.

    Returns:
        Path to saved audio file, or None if invalid.
    """
    from pathlib import Path

    # If data is a file path, return it
    if "," not in data and Path(data).exists():
        return data

    try:
        import base64

        # Handle data URL scheme
        if "," in data:
            _header, audio_data = data.split(",", 1)
        else:
            audio_data = data

        # Decode
        decoded = base64.b64decode(audio_data)

        # Create media directory
        media_dir = Path(config.get("media.storage_dir", "./media"))
        media_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        format = config.get("media.audio_format", "mp3")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"audio_{timestamp}.{format}"
        filepath = media_dir / filename

        with open(filepath, "wb") as f:
            f.write(decoded)

        return str(filepath)
    except Exception:
        return None
