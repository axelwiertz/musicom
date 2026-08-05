"""Custom exceptions for musicom."""


class MusicomAIException(Exception):
    """Base exception for all musicom exceptions."""

    pass


class InvalidPitchError(MusicomAIException):
    """Raised when a pitch value is invalid or out of range."""

    pass


class InvalidIntervalError(MusicomAIException):
    """Raised when an interval is invalid."""

    pass


class InvalidDurationError(MusicomAIException):
    """Raised when a duration value is invalid."""

    pass


class InvalidChordError(MusicomAIException):
    """Raised when a chord is invalid or cannot be constructed."""

    pass


class ConversionError(MusicomAIException):
    """Raised when format conversion between libraries fails."""

    pass


class ValidationError(MusicomAIException):
    """Raised when validation of musical data fails."""

    pass


class FileIOError(MusicomAIException):
    """Raised when file I/O operations fail."""

    pass


class AudioAnalysisError(MusicomAIException):
    """Raised when audio analysis operations fail."""

    pass
