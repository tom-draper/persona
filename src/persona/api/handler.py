import json
import warnings
from pathlib import Path

from persona.lib.format import clean_location
from persona.lib.generate import preprocess_location_data

DATA_DIR = Path(__file__).parent.parent / "data"


def load_location_data() -> dict:
    # A directory may hold a leaf dataset ("<name>.json"), a "composite.json",
    # or both — an interior node that keeps its own data while also carving out
    # weighted sublocations. Datasets are keyed by their path relative to the
    # data directory so that names shared across the tree (e.g. the country
    # "georgia" and the US state "georgia") stay distinct.
    data: dict = {}
    for path in DATA_DIR.rglob("*.json"):
        key = path.parent.relative_to(DATA_DIR).as_posix()
        entry = data.setdefault(
            key, {"leaf": None, "composite": None, "name": path.parent.name, "key": key}
        )
        try:
            with open(path) as f:
                doc = json.load(f)
        except json.JSONDecodeError:
            warnings.warn(f"Skipping {path}: invalid JSON", stacklevel=2)
            continue
        if path.name == "composite.json":
            entry["composite"] = doc
        else:
            entry["leaf"] = doc
    return preprocess_location_data(data)


def resolve_key(name: str, data: dict) -> str | None:
    """Map a bare (already-normalised) location name to its canonical key.

    When a name is shared across the tree, the shallowest (top-level) dataset
    wins — so ``georgia`` is the country, while the US state is reached through
    the ``united_states_of_america`` composite's scoped child key.
    """
    candidates = [k for k, v in data.items() if v.get("name") == name]
    if not candidates:
        return None
    return min(candidates, key=lambda k: k.count("/"))


def resolve_path_key(location: str, data: dict) -> str | None:
    """Resolve a location path (one name, or a slash/space-separated path down
    the tree) to the key of its target node, without random descent. The first
    segment resolves to a top-level key; each subsequent one descends by scoped
    child key. Returns None if any segment does not resolve."""
    segments = [clean_location(p) for p in location.replace("/", " ").split()]
    if not segments:
        return None
    key = resolve_key(segments[0], data)
    if key is None:
        return None
    for seg in segments[1:]:
        child = f"{key}/{seg}"
        if child not in data:
            return None
        key = child
    return key


def _subtree_features(key: str, data: dict, seen: set[str]) -> set[str]:
    """Union of every feature reachable from a node, recursing through
    composites (and self/remainder branches, guarded by ``seen``)."""
    if key in seen or key not in data:
        return set()
    seen.add(key)
    node = data[key]
    features: set[str] = set()
    if node.get("leaf"):
        features.update(k for k in node["leaf"] if k != "_meta")
    for child_key in node.get("subloc_keys", []):
        features |= _subtree_features(str(child_key), data, seen)
    return features


def get_features(location: str, data: dict) -> dict:
    key = resolve_path_key(location, data)
    if key is None:
        return {}
    return {location: sorted(_subtree_features(key, data, set()))}


def get_available_features(location: str, data: dict) -> set[str]:
    features_dict = get_features(location, data)
    result: set[str] = set()
    for feature_list in features_dict.values():
        result.update(feature_list)
    return result
