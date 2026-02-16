"""Custom exceptions for Sprachspiel."""


class SprachspielError(Exception):
    """Base exception for Sprachspiel."""

    pass


class ConfigurationError(SprachspielError):
    """Raised when configuration is invalid."""

    pass


class ServiceError(SprachspielError):
    """Raised when a service fails."""

    pass


class DictionaryError(ServiceError):
    """Raised when dictionary lookup fails."""

    pass


class TTSError(ServiceError):
    """Raised when TTS synthesis fails."""

    pass


class AIError(ServiceError):
    """Raised when AI service fails."""

    pass


class AnkiError(SprachspielError):
    """Raised when Anki integration fails."""

    pass


class AnkiConnectError(AnkiError):
    """Raised when AnkiConnect fails."""

    pass


class AnkiExportError(AnkiError):
    """Raised when file export fails."""

    pass


class SourceError(SprachspielError):
    """Raised when data source fails."""

    pass


class ParseError(SprachspielError):
    """Raised when parsing fails."""

    pass
