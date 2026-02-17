import functools
import json
from collections.abc import Iterable
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).parent.parent / 'data'


def normalise_weights(weights: Iterable[float]) -> np.ndarray:
    p = np.array(list(weights), dtype=np.float64)
    if p.sum() == 0.0:
        raise ValueError('Probabilities sum to 0')
    return p / p.sum()


def select_sublocation(composite_path: Path, rng: np.random.Generator) -> str:
    with open(composite_path) as f:
        data = json.load(f)
    keys = np.array(list(data.keys()))
    p = normalise_weights(data.values())
    return str(rng.choice(keys, p=p)).lower()


def resolve_location(location: str, rng: np.random.Generator) -> tuple[str, list[str]]:
    """
    Recursively resolve composite locations until a leaf data file is reached.

    Returns (leaf_name, location_labels) where location_labels is an ordered
    list of sublocation names traversed (innermost first) to append to the
    persona's location field.

    Examples (with uk→england composite, england→yorkshire composite):
        resolve_location('united_kingdom', rng) → ('yorkshire', ['yorkshire', 'england'])
        resolve_location('england', rng)        → ('yorkshire', ['yorkshire'])
        resolve_location('yorkshire', rng)      → ('yorkshire', [])
    """
    composite_path = get_composite_path(location)
    if composite_path is None:
        return location, []
    sublocation = select_sublocation(composite_path, rng)
    leaf, sub_labels = resolve_location(sublocation, rng)
    return leaf, sub_labels + [sublocation]


def resolve_api_location(
    location: str,
    data: dict,
    rng: np.random.Generator,
) -> tuple[str, list[str]]:
    """
    Recursively resolve composite locations using preloaded data.
    Returns (leaf_name, location_labels) — see resolve_location for details.
    """
    if not data[location]['composite']:
        return location, []
    sublocation = str(rng.choice(
        data[location]['subloc_keys'],
        p=data[location]['subloc_probs'],
    ))
    if sublocation not in data:
        raise ValueError(f"Sublocation '{sublocation}' not found in preloaded data")
    leaf, sub_labels = resolve_api_location(sublocation, data, rng)
    return leaf, sub_labels + [sublocation]


@functools.cache
def list_locations() -> list[str]:
    """Return all location names that have data (regular or composite)."""
    locations = []
    for path in DATA_DIR.rglob('*.json'):
        name = path.parent.name
        if path.name in (f'{name}.json', 'composite.json'):
            locations.append(name)
    return sorted(locations)


def get_file_path(target: str) -> Path | None:
    target = target.lower().replace(' ', '_')
    for path in DATA_DIR.rglob(f'{target}.json'):
        if path.parent.name == target:
            return path
    return None


def get_composite_path(target: str) -> Path | None:
    target = target.lower().replace(' ', '_')
    for path in DATA_DIR.rglob('composite.json'):
        if path.parent.name == target:
            return path
    return None


def collapsed_dict(d: dict, path: list[str] | None = None) -> list[tuple[list[str], float]]:
    if path is None:
        path = []
    result = []
    for k, v in d.items():
        new_path = path + [k]
        if not isinstance(v, dict):
            result.append((new_path, v))
        else:
            result.extend(collapsed_dict(v, new_path))
    return result


def _parse_age_bucket(bucket: str, rng: np.random.Generator) -> int:
    if '-' in bucket:
        low, high = map(int, bucket.split('-'))
        return int(rng.integers(low, high + 1))
    elif '+' in bucket:
        low = int(bucket.replace('+', ''))
        return int(rng.integers(low, max(low + 1, 101)))  # cap at 100
    return int(bucket)


def gen_age(age_data: dict[str, float], rng: np.random.Generator) -> int:
    ages = np.array(list(age_data.keys()))
    p = normalise_weights(age_data.values())
    bucket = str(rng.choice(ages, p=p))
    return _parse_age_bucket(bucket, rng)


def gen_feature(data: dict, rng: np.random.Generator) -> str:
    collapsed = collapsed_dict(data)
    options = np.array([', '.join(reversed(x[0])) for x in collapsed])
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
        if feature == '_meta':
            continue
        if enabled_features is None or feature in enabled_features:
            if feature == 'age':
                sample[feature] = gen_age(_data, rng)
            elif feature not in ('relationship', 'marital status', 'occupation') or sample.get('age', 16) >= 16:
                sample[feature] = gen_feature(_data, rng)
    return sample


def preprocess_location_data(data: dict) -> dict:
    """
    Precompute probability arrays and option lists for each feature in each
    location. Called once at API startup so per-request generation only needs
    to call rng.choice with already-normalised arrays.
    """
    for entry in data.values():
        if entry['composite']:
            keys = list(entry['data'].keys())
            entry['subloc_keys'] = np.array([k.lower().replace(' ', '_') for k in keys])
            entry['subloc_probs'] = normalise_weights(entry['data'].values())
        else:
            processed: dict[str, dict] = {}
            for feature, feature_data in entry['data'].items():
                if feature == '_meta':
                    continue
                if feature == 'age':
                    processed['age'] = {
                        'keys': np.array(list(feature_data.keys())),
                        'probs': normalise_weights(feature_data.values()),
                    }
                else:
                    col = collapsed_dict(feature_data)
                    processed[feature] = {
                        'options': np.array([', '.join(reversed(x[0])) for x in col]),
                        'probs': normalise_weights(x[1] for x in col),
                    }
            entry['processed'] = processed
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
        target, location_labels = resolve_api_location(location, data, rng)

        sample: dict[str, str | int] = {}
        for feature, proc in data[target]['processed'].items():
            if enabled_features is not None and feature not in enabled_features:
                continue
            if feature == 'age':
                bucket = str(rng.choice(proc['keys'], p=proc['probs']))
                sample['age'] = _parse_age_bucket(bucket, rng)
            elif feature not in ('relationship', 'marital status', 'occupation') or sample.get('age', 16) >= 16:
                sample[feature] = str(rng.choice(proc['options'], p=proc['probs']))

        for label in location_labels:
            if 'location' in sample:
                sample['location'] += f', {label.title()}'
            else:
                sample['location'] = label.title()

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
    for _ in range(N):
        target, location_labels = resolve_location(location, rng)

        location_path = get_file_path(target)
        if location_path is None:
            raise ValueError(f"Location '{target}' not found")
        if location_path in cache:
            file_data = cache[location_path]
        else:
            with open(location_path) as f:
                file_data = json.load(f)
            cache[location_path] = file_data

        sample = gen_sample(file_data, enabled_features, rng)
        for label in location_labels:
            if 'location' in sample:
                sample['location'] += f', {label.title()}'
            else:
                sample['location'] = label.title()
        samples.append(sample)

    return samples
