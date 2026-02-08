"""AI model service for translation and example generation."""

from typing import Any

from sprachspiel.config import Config


class AIService:
    """Service for AI model integration."""

    def __init__(self, config: Config):
        """Initialize AI service.

        Args:
            config: Configuration instance.
        """
        self.config = config
        self.provider = config.get("ai.provider", "openai")
        self.api_key = config.get("ai.api_key", "")
        self.base_url = config.get("ai.base_url", "https://api.openai.com/v1")
        self.model = config.get("ai.model", "gpt-4o-mini")
        self.functions = config.get("ai.functions", {})

    def is_configured(self) -> bool:
        """Check if AI service is configured.

        Returns:
            True if API key is set and functions are configured.
        """
        return bool(self.api_key) and len(self.functions) > 0

    def has_function(self, name: str) -> bool:
        """Check if function is configured.

        Args:
            name: Function name.

        Returns:
            True if function is configured.
        """
        return name in self.functions

    def get_custom_functions(self) -> dict[str, Any]:
        """Get custom AI functions (non-reserved).

        Returns:
            Dictionary of custom functions.
        """
        reserved = {"translate", "example"}
        return {
            k: v for k, v in self.functions.items() if k not in reserved
        }

    async def call_function(
        self, name: str, word: str, **kwargs: Any
    ) -> str | None:
        """Call AI function for word.

        Args:
            name: Function name.
            word: Word to process.
            **kwargs: Additional parameters.

        Returns:
            Function result or None.
        """
        if name not in self.functions:
            return None

        func_config = self.functions[name]
        prompt = func_config.get("prompt", "")

        # Replace ${word} placeholder
        prompt = prompt.replace("${word}", word)

        # Replace other kwargs
        for key, value in kwargs.items():
            prompt = prompt.replace(f"${{{key}}}", str(value))

        try:
            return await self._call_api(prompt)
        except Exception as e:
            print(f"AI function {name} failed: {e}")
            raise

    async def _call_api(self, prompt: str) -> str:
        """Call AI API with prompt.

        Args:
            prompt: Prompt to send.

        Returns:
            AI response.
        """

        if self.provider == "openai" or "api.openai.com" in self.base_url:
            return await self._call_openai(prompt)
        elif self.provider == "anthropic":
            return await self._call_anthropic(prompt)
        else:
            return await self._call_custom_endpoint(prompt)

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API.

        Args:
            prompt: Prompt to send.

        Returns:
            AI response.
        """
        import requests

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API.

        Args:
            prompt: Prompt to send.

        Returns:
            AI response.
        """
        import requests

        url = f"{self.base_url}/messages"

        headers: dict[str, Any] = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        data: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 100,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result["content"][0]["text"].strip()

    async def _call_custom_endpoint(self, prompt: str) -> str:
        """Call custom endpoint (OpenAI-compatible format).

        Args:
            prompt: Prompt to send.

        Returns:
            AI response.
        """
        import requests

        url = f"{self.base_url}/chat/completions"

        headers: dict[str, Any] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
