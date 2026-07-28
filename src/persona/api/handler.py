import json
import warnings
from pathlib import Path

from persona.lib.format import clean_location
from persona.lib.generate import preprocess_location_data

DATA_DIR = Path(__file__).parent.parent / "data"


def load_location_data() -> dict:
    # A directory may hold a leaf dataset ("<name>.json"), a "composite.json",
    # or both — an interior node that keeps its own data while also carving out
    # weighted sublocations. Merge both files under the one location key.
    data: dict = {}
    for path in DATA_DIR.rglob("*.json"):
        location = path.parent.name
        entry = data.setdefault(location, {"leaf": None, "composite": None})
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


def _subtree_features(location: str, data: dict, seen: set[str]) -> set[str]:
    """Union of every feature reachable from a node, recursing through
    composites (and self/remainder branches, guarded by ``seen``)."""
    if location in seen or location not in data:
        return set()
    seen.add(location)
    node = data[location]
    features: set[str] = set()
    if node.get("leaf"):
        features.update(k for k in node["leaf"] if k != "_meta")
    if node.get("composite"):
        for subloc in node["composite"]:
            if subloc == "_meta":
                continue
            features |= _subtree_features(clean_location(subloc), data, seen)
    return features


def get_features(location: str, data: dict) -> dict:
    if location == "global":
        return {}
    return {location: sorted(_subtree_features(location, data, set()))}


def get_available_features(location: str, data: dict) -> set[str]:
    features_dict = get_features(location, data)
    result: set[str] = set()
    for feature_list in features_dict.values():
        result.update(feature_list)
    return result
