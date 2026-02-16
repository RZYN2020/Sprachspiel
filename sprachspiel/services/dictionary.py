"""Dictionary service for word lookups."""

from typing import Any, cast

from sprachspiel.config import Config, DictionaryConfig
from sprachspiel.exceptions import DictionaryError
from sprachspiel.logging_config import get_logger
from sprachspiel.types import DictionaryResult

logger = get_logger(__name__)


class DictionaryService:
    """Service for dictionary lookups."""

    def __init__(self, config: Config):
        """Initialize dictionary service.

        Args:
            config: Configuration instance.
        """
        self.config = config
        self.dictionaries = config.dictionaries

    def is_configured(self) -> bool:
        """Check if dictionary service is configured.

        Returns:
            True if at least one dictionary is configured.
        """
        return len(self.dictionaries) > 0

    async def lookup(self, word: str) -> DictionaryResult:
        """Look up word in configured dictionaries.

        Args:
            word: Word to look up.

        Returns:
            Dictionary with translation, definition, example.
        """
        result: DictionaryResult = {
            "translation": None,
            "definition": None,
            "example": None,
        }

        for dict_config in self.dictionaries:
            try:
                dict_result = await self._lookup_dictionary(word, dict_config)

                # Use first successful result (any non-empty field qualifies)
                if (
                    dict_result.get("translation")
                    or dict_result.get("definition")
                    or dict_result.get("example")
                ):
                    result.update(cast(DictionaryResult, dict_result))
                    break
            except Exception as e:
                logger.warning(f"Dictionary lookup failed for {dict_config.name}: {e}")

        return result

    async def _lookup_dictionary(self, word: str, dict_config: DictionaryConfig) -> dict[str, Any]:
        """Look up word in specific dictionary.

        Args:
            word: Word to look up.
            dict_config: Dictionary configuration.

        Returns:
            Dictionary with translation, definition, example.
        """
        module_name = dict_config.module

        # Built-in dictionaries
        result = {"translation": None, "definition": None, "example": None}

        if module_name in ("oxford", "dicts.oxford_api"):
            result = await self._lookup_oxford(word, dict_config)
        elif module_name in ("youdao", "dicts.youdao_api"):
            result = await self._lookup_youdao(word, dict_config)
        # Custom module support (must have a dot but not be a built-in module)
        elif module_name and "." in module_name:
            return await self._lookup_custom(word, dict_config)

        return result

    async def _lookup_custom(self, word: str, dict_config: DictionaryConfig) -> dict[str, Any]:
        """Look up word using custom dictionary module.

        Args:
            word: Word to look up.
            dict_config: Dictionary configuration.

        Returns:
            Dictionary with translation, definition, example.
        """
        module_name = dict_config.module

        try:
            # Import custom module
            from importlib import import_module

            if not module_name:
                raise ValueError("Module name is required")

            parts = module_name.split(".")
            module = import_module(".".join(parts[:-1]))
            lookup_func = getattr(module, parts[-1])

            result = await lookup_func(word, dict_config)
            return result or {}
        except Exception as e:
            raise RuntimeError(f"Failed to load custom dictionary {module_name}: {e}") from e

    async def _lookup_oxford(self, word: str, dict_config: DictionaryConfig) -> dict[str, Any]:
        """Look up word in Oxford dictionary.

        Args:
            word: Word to look up.
            dict_config: Oxford configuration.

        Returns:
            Dictionary with translation, definition, example.
        """
        import requests

        api_key = dict_config.api_key
        if not api_key:
            return {}

        url = f"https://api.dictionaryapi.dev/api/v2/entries/{word.lower()}"

        headers = {
            "app_id": api_key.split(":")[0],
            "app_key": api_key.split(":")[1],
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        if not data:
            return {}

        # Parse Oxford API response
        result = {"translation": None, "definition": None, "example": None}

        entry = data[0]

        # Get definition
        senses = entry.get("senses", [])
        if senses and "definitions" in senses[0]:
            defs = senses[0]["definitions"]
            if defs:
                result["definition"] = defs[0].get("definitions", [{}])[0].get("value", "")

        # Get example
        if senses and "examples" in senses[0]:
            examples = senses[0]["examples"]
            if examples:
                result["example"] = examples[0].get("text", "")

        # Translation not typically in monolingual Oxford API
        # Would need bilingual dictionary for translations

        return result

    async def _lookup_youdao(self, word: str, dict_config: DictionaryConfig) -> dict[str, Any]:
        """Look up word in Youdao dictionary.

        Args:
            word: Word to look up.
            dict_config: Youdao configuration.

        Returns:
            Dictionary with translation, definition, example.
        """
        import requests

        api_key = dict_config.api_key
        if not api_key:
            return {}

        url = "https://openapi.youdao.com/api"
        params: dict[str, Any] = {
            "q": word,
            "from": "auto",
            "to": "zh",
            "appKey": api_key,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if not data or "errorCode" in data:
            return {}

        # Parse Youdao API response
        result = {"translation": None, "definition": None, "example": None}

        translation = data.get("translation", [])
        if translation and len(translation) > 0:
            result["translation"] = translation[0]

        # Examples in web translation
        web_trans = data.get("web", [])
        if web_trans and len(web_trans) > 0:
            examples = web_trans[0].get("value", [])
            if examples and len(examples) > 0:
                result["example"] = examples[0]

        return result
