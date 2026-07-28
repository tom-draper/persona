import functools
import json
from collections.abc import Iterable
from pathlib import Path

import numpy as np

from persona.lib.format import clean_location

DATA_DIR = Path(__file__).parent.parent / "data"

# Features only assigned to samples aged 16 or over.
ADULT_ONLY_FEATURES = ("marital status", "occupation")


def normalise_weights(weights: Iterable[float]) -> np.ndarray:
    p = np.array(list(weights), dtype=np.float64)
    if p.sum() == 0.0:
        raise ValueError("Probabilities sum to 0")
    return p / p.sum()


def select_sublocation(composite_path: Path, rng: np.random.Generator) -> str:
    with open(composite_path) as f:
        data = json.load(f)
    weights = {k: v for k, v in data.items() if k != "_meta"}
    keys = np.array(list(weights.keys()))
    p = normalise_weights(weights.values())
    return str(rng.choice(keys, p=p)).lower()


def resolve_location(location: str, rng: np.random.Generator) -> tuple[list[str], list[str]]:
    """
    Recursively resolve composite locations into the chain of data-bearing
    nodes to draw from and the sublocation labels to append.

    Returns (leaf_chain, location_labels):
      - leaf_chain: node names that carry a leaf dataset, outermost first and
        innermost last. A persona is generated from their merged features,
        with inner nodes overriding outer ones (feature inheritance). An
        interior node that keeps its own leaf therefore acts as a baseline
        that a carved-out sublocation refines.
      - location_labels: sublocation names traversed (innermost first) to
        append to the persona's location field.

    Examples (uk→england composite; england→london composite with an England
    self/remainder branch):
        resolve_location('england')        → (['england'], [])                       # self branch
        resolve_location('england')        → (['england', 'london'], ['london'])
        resolve_location('united_kingdom') → (['england', 'london'], ['london', 'england'])
    """
    chain = [location] if get_file_path(location) is not None else []
    composite_path = get_composite_path(location)
    if composite_path is None:
        return chain, []
    sublocation = select_sublocation(composite_path, rng)
    # Self/remainder branch: a composite may list its own node as a weighted
    # option, letting an interior node keep its own leaf dataset alongside
    # carved-out sublocations. Resolving it stops at this node's leaf and adds
    # no extra label (we are already "in" this location).
    if clean_location(sublocation) == clean_location(location):
        return chain, []
    sub_chain, sub_labels = resolve_location(sublocation, rng)
    return chain + sub_chain, [*sub_labels, sublocation]


def resolve_api_location(
    location: str,
    data: dict,
    rng: np.random.Generator,
) -> tuple[str, list[str]]:
    """
    Recursively resolve composite locations using preloaded data.
    Returns (leaf_chain, location_labels) — see resolve_location for details.
    """
    node = data[location]
    chain = [location] if node.get("leaf") else []
    if not node.get("composite"):
        return chain, []
    sublocation = str(rng.choice(node["subloc_keys"], p=node["subloc_probs"]))
    # Self/remainder branch — see resolve_location.
    if clean_location(sublocation) == clean_location(location):
        return chain, []
    if sublocation not in data:
        raise ValueError(f"Sublocation '{sublocation}' not found in preloaded data")
    sub_chain, sub_labels = resolve_api_location(sublocation, data, rng)
    return chain + sub_chain, [*sub_labels, sublocation]


@functools.cache
def list_all_features() -> set[str]:
    features: set[str] = set()
    for path in DATA_DIR.rglob("*.json"):
        if path.name == "composite.json":
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            features.update(k for k in data if k != "_meta")
        except (json.JSONDecodeError, OSError):
            pass
    return features


@functools.cache
def list_locations() -> list[str]:
    """Return all location names that have data (regular or composite)."""
    locations = set()
    for path in DATA_DIR.rglob("*.json"):
        name = path.parent.name
        if path.name in (f"{name}.json", "composite.json"):
            locations.add(name)
    return sorted(locations)


def get_file_path(target: str) -> Path | None:
    target = target.lower().replace(" ", "_")
    for path in DATA_DIR.rglob(f"{target}.json"):
        if path.parent.name == target:
            return path
    return None


def get_composite_path(target: str) -> Path | None:
    target = target.lower().replace(" ", "_")
    for path in DATA_DIR.rglob("composite.json"):
        if path.parent.name == target:
            return path
    return None


def collapsed_dict(d: dict, path: list[str] | None = None) -> list[tuple[list[str], float]]:
    if path is None:
        path = []
    result = []
    for k, v in d.items():
        new_path = [*path, k]
        if not isinstance(v, dict):
            result.append((new_path, v))
        else:
            result.extend(collapsed_dict(v, new_path))
    return result


def _parse_age_bucket(bucket: str, rng: np.random.Generator) -> int:
    if "-" in bucket:
        low, high = map(int, bucket.split("-"))
        return int(rng.integers(low, high + 1))
    elif "+" in bucket:
        low = int(bucket.replace("+", ""))
        return int(rng.integers(low, max(low + 1, 101)))  # cap at 100
    return int(bucket)


def gen_age(age_data: dict[str, float], rng: np.random.Generator) -> int:
    ages = np.array(list(age_data.keys()))
    p = normalise_weights(age_data.values())
    bucket = str(rng.choice(ages, p=p))
    return _parse_age_bucket(bucket, rng)


def gen_feature(data: dict, rng: np.random.Generator) -> str:
    collapsed = collapsed_dict(data)
    options = np.array([", ".join(reversed(x[0])) for x in collapsed])
    p = normalise_weights(x[1] for x in collapsed)
    return str(rng.choice(options, p=p))


def gen_sample(
    data: dict,
    enabled_features: set[str] | None,
    rng: np.random.Generator,
) -> dict[str, str | int]:
    sample = {}
    for feature, _data in data.items():
        feature = feature.lower()
        if feature == "_meta":
            continue
        if enabled_features is None or feature in enabled_features:
            if feature == "age":
                sample[feature] = gen_age(_data, rng)
            elif feature not in ADULT_ONLY_FEATURES or sample.get("age", 16) >= 16:
                sample[feature] = gen_feature(_data, rng)
    return sample


def _merge_leaves(leaves: list[dict]) -> dict:
    """Overlay leaf datasets outermost→innermost (inner overrides outer) so a
    carved-out sublocation inherits its ancestors' features. The location
    feature comes only from the innermost leaf: when a sublocation was chosen
    its label supersedes any ancestor's location distribution."""
    merged: dict = {}
    for leaf in leaves:
        for feature, value in leaf.items():
            if feature in ("_meta", "location"):
                continue
            merged[feature] = value
    inner = leaves[-1]
    if "location" in inner:
        merged["location"] = inner["location"]
    return merged


def _merge_processed(chain: list[str], data: dict) -> dict:
    """Preprocessed-array equivalent of _merge_leaves for the API path."""
    merged: dict = {}
    for node in chain:
        for feature, proc in data[node].get("processed", {}).items():
            if feature == "location":
                continue
            merged[feature] = proc
    inner = data[chain[-1]].get("processed", {})
    if "location" in inner:
        merged["location"] = inner["location"]
    return merged


def preprocess_location_data(data: dict) -> dict:
    """
    Precompute probability arrays and option lists for each feature in each
    location. Called once at API startup so per-request generation only needs
    to call rng.choice with already-normalised arrays.
    """
    # A node may carry composite weights, a leaf dataset, or both (an interior
    # node that keeps its own data while also carving out sublocations).
    for entry in data.values():
        composite = entry.get("composite")
        if composite:
            weights = {k: v for k, v in composite.items() if k != "_meta"}
            keys = list(weights.keys())
            entry["subloc_keys"] = np.array([k.lower().replace(" ", "_") for k in keys])
            entry["subloc_probs"] = normalise_weights(weights.values())
        leaf = entry.get("leaf")
        if leaf:
            processed: dict[str, dict] = {}
            for feature, feature_data in leaf.items():
                if feature == "_meta":
                    continue
                if feature == "age":
                    processed["age"] = {
                        "keys": np.array(list(feature_data.keys())),
                        "probs": normalise_weights(feature_data.values()),
                    }
                else:
                    col = collapsed_dict(feature_data)
                    processed[feature] = {
                        "options": np.array([", ".join(reversed(x[0])) for x in col]),
                        "probs": normalise_weights(x[1] for x in col),
                    }
            entry["processed"] = processed
    return data


def gen_api_samples(
    location: str,
    data: dict,
    enabled_features: set[str] | None = None,
    N: int = 1,
    seed: int | None = None,
) -> list[dict]:
    """
    Returns randomly generated persona(s) for the given target location,
    constrained by any optional enabled features.
    Uses precomputed probability arrays (see preprocess_location_data).

    Arguments
        location: str - Target location.
        data: dict - Preloaded and preprocessed location data.
        enabled_features: set[str]|None - Features to include; None means all.
        N: int - Number of personas to generate. Defaults to 1.
        seed: int|None - Random seed for reproducible output. Defaults to None.
    """
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(N):
        chain, location_labels = resolve_api_location(location, data, rng)
        merged = _merge_processed(chain, data)

        sample: dict[str, str | int] = {}
        for feature, proc in merged.items():
            if enabled_features is not None and feature not in enabled_features:
                continue
            if feature == "age":
                bucket = str(rng.choice(proc["keys"], p=proc["probs"]))
                sample["age"] = _parse_age_bucket(bucket, rng)
            elif feature not in ADULT_ONLY_FEATURES or sample.get("age", 16) >= 16:
                sample[feature] = str(rng.choice(proc["options"], p=proc["probs"]))

        if enabled_features is None or "location" in enabled_features:
            for label in location_labels:
                if "location" in sample:
                    sample["location"] += f", {label.title()}"
                else:
                    sample["location"] = label.title()

        samples.append(sample)

    return samples


def gen_samples(
    location: str,
    enabled_features: set[str] | None = None,
    N: int = 1,
    seed: int | None = None,
) -> list[dict]:
    """
    Returns randomly generated persona(s) for the given target location,
    constrained by any optional enabled features.
    Loads data from disk with per-call caching; used by the CLI.

    Arguments
        location: str - Target location.
        enabled_features: set[str]|None - Features to include; None means all.
        N: int - Number of personas to generate. Defaults to 1.
        seed: int|None - Random seed for reproducible output. Defaults to None.
    """
    rng = np.random.default_rng(seed)
    samples = []
    cache: dict[Path, dict] = {}

    def load(node: str) -> dict:
        path = get_file_path(node)
        if path is None:
            raise ValueError(f"Location '{node}' not found")
        if path not in cache:
            with open(path) as f:
                cache[path] = json.load(f)
        return cache[path]

    # Idempotent, so callers that already normalised (the CLI, the API) are
    # unaffected, and direct library callers get alias resolution for free.
    location = clean_location(location)
    for _ in range(N):
        chain, location_labels = resolve_location(location, rng)
        if not chain:
            raise ValueError(f"Location '{location}' not found")
        merged = _merge_leaves([load(node) for node in chain])

        sample = gen_sample(merged, enabled_features, rng)
        if enabled_features is None or "location" in enabled_features:
            for label in location_labels:
                if "location" in sample:
                    sample["location"] += f", {label.title()}"
                else:
                    sample["location"] = label.title()
        samples.append(sample)

    return samples
