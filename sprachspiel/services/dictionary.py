"""Dictionary service for word lookups."""

from typing import Any

from sprachspiel.config import Config


class DictionaryService:
    """Service for dictionary lookups."""

    def __init__(self, config: Config):
        """Initialize dictionary service.

        Args:
            config: Configuration instance.
        """
        self.config = config
        self.dictionaries = config.get("dictionaries", [])

    def is_configured(self) -> bool:
        """Check if dictionary service is configured.

        Returns:
            True if at least one dictionary is configured.
        """
        return len(self.dictionaries) > 0

    async def lookup(self, word: str) -> dict[str, Any]:
        """Look up word in configured dictionaries.

        Args:
            word: Word to look up.

        Returns:
            Dictionary with translation, definition, example.
        """
        result = {"translation": None, "definition": None, "example": None}

        for dict_config in self.dictionaries:
            try:
                dict_result = await self._lookup_dictionary(word, dict_config)

                # Use first successful result
                if dict_result.get("translation"):
                    result.update(dict_result)
                    break
            except Exception as e:
                print(f"Dictionary lookup failed for {dict_config.get('name')}: {e}")

        return result

    async def _lookup_dictionary(
        self, word: str, dict_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Look up word in specific dictionary.

        Args:
            word: Word to look up.
            dict_config: Dictionary configuration.

        Returns:
            Dictionary with translation, definition, example.
        """
        module_name = dict_config.get("module")

        # Custom module support
        if module_name and "." in module_name:
            return await self._lookup_custom(word, dict_config)

        # Built-in dictionaries
        result = {"translation": None, "definition": None, "example": None}

        if module_name == "dicts.oxford_api":
            result = await self._lookup_oxford(word, dict_config)
        elif module_name == "dicts.youdao_api":
            result = await self._lookup_youdao(word, dict_config)

        return result

    async def _lookup_custom(
        self, word: str, dict_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Look up word using custom dictionary module.

        Args:
            word: Word to look up.
            dict_config: Dictionary configuration.

        Returns:
            Dictionary with translation, definition, example.
        """
        module_name = dict_config.get("module")

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

    async def _lookup_oxford(
        self, word: str, dict_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Look up word in Oxford dictionary.

        Args:
            word: Word to look up.
            dict_config: Oxford configuration.

        Returns:
            Dictionary with translation, definition, example.
        """
        import requests

        api_key = dict_config.get("api_key")
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

    async def _lookup_youdao(
        self, word: str, dict_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Look up word in Youdao dictionary.

        Args:
            word: Word to look up.
            dict_config: Youdao configuration.

        Returns:
            Dictionary with translation, definition, example.
        """
        import requests

        api_key = dict_config.get("api_key")
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
