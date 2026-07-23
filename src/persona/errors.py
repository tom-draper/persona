"""Exceptions raised by the public API."""


class PersonaError(Exception):
    """Base class for every error this package raises."""


class UnknownLocationError(PersonaError, ValueError):
    """Raised when a location has no bundled dataset.

    Subclasses ValueError so that callers written against the pre-1.0
    behaviour, which raised a bare ValueError, keep working.
    """

    def __init__(self, location: str, available: list[str] | None = None):
        self.location = location
        self.available = available or []
        message = f"Unknown location: {location!r}"
        if self.available:
            message += f". Available locations: {', '.join(self.available)}"
        super().__init__(message)


class UnknownFeatureError(PersonaError, ValueError):
    """Raised when features are requested that a location does not provide."""

    def __init__(self, location: str, invalid: set[str], available: set[str]):
        self.location = location
        self.invalid = sorted(invalid)
        self.available = sorted(available)
        super().__init__(
            f"Location {location!r} has no feature(s): {', '.join(self.invalid)}. "
            f"Available features: {', '.join(self.available)}"
        )
