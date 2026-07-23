"""
Generate realistic character profiles from real-world demographic data.

    >>> import persona
    >>> persona.generate("wales")
    {'age': 34, 'sex': 'Female', 'country of birth': 'Wales', ...}

Every feature is drawn independently from a published census or statistical
distribution for that location, so a large sample is representative of the
real population. See `persona.locations()` for what is available.
"""

from importlib.metadata import PackageNotFoundError, version

from persona.errors import PersonaError, UnknownFeatureError, UnknownLocationError
from persona.lib.format import clean_location
from persona.lib.generate import (
    gen_samples,
    list_all_features,
    list_location_features,
    list_locations,
)

try:
    __version__ = version("persona")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0.0.0"

#: A generated persona. Keys vary by location, so use .get() for anything
#: that is not present everywhere (only UK datasets carry "sexuality").
Persona = dict[str, str | int]

__all__ = [
    "Persona",
    "PersonaError",
    "UnknownFeatureError",
    "UnknownLocationError",
    "__version__",
    "features",
    "generate",
    "generate_many",
    "locations",
]


def _validate(location: str, requested: set[str] | None) -> tuple[str, set[str] | None]:
    target = clean_location(location)
    if target not in list_locations():
        raise UnknownLocationError(location, list_locations())
    if requested is None:
        return target, None
    requested = {f.lower().strip() for f in requested}
    available = list_location_features(target)
    invalid = requested - available
    if invalid:
        raise UnknownFeatureError(location, invalid, available)
    return target, requested


def generate(
    location: str,
    *,
    features: set[str] | None = None,
    seed: int | None = None,
) -> Persona:
    """
    Generate a single persona for `location`.

    Arguments
        location: Place to draw from, e.g. "wales". Aliases such as "uk" and
            "usa" are accepted, as are display forms like "Northern Ireland".
        features: Restrict output to these features. None means all available.
        seed: Seed for reproducible output.

    Raises
        UnknownLocationError: `location` has no bundled dataset.
        UnknownFeatureError: `features` names something this location lacks.

    >>> persona.generate("wales", features={"age", "sex"}, seed=42)
    {'age': 55, 'sex': 'Female'}
    """
    return generate_many(location, 1, features=features, seed=seed)[0]


def generate_many(
    location: str,
    n: int,
    *,
    features: set[str] | None = None,
    seed: int | None = None,
) -> list[Persona]:
    """
    Generate `n` personas for `location`.

    Takes the same arguments as `generate`, plus the count. Generating in one
    call is considerably faster than looping over `generate`, which re-reads
    the location's data each time.

    >>> len(persona.generate_many("wales", 100))
    100
    """
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    target, enabled = _validate(location, features)
    return gen_samples(target, enabled, n, seed=seed)


def locations() -> list[str]:
    """
    Return every location with a bundled dataset, sorted.

    >>> "wales" in persona.locations()
    True
    """
    return list_locations()


def features(location: str | None = None) -> set[str]:
    """
    Return the features available for `location`, or across every dataset
    when `location` is None.

    Coverage varies: UK datasets carry "sexuality", Canada does not.

    >>> sorted(persona.features("canada"))[:3]
    ['age', 'education', 'ethnicity']
    """
    if location is None:
        return list_all_features()
    target = clean_location(location)
    if target not in list_locations():
        raise UnknownLocationError(location, list_locations())
    return list_location_features(target)
