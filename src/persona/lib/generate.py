import json
import os
from pathlib import Path
from typing import Union

import numpy as np

DATA_DIR = Path(__file__).parent.parent / 'data'


def probabilities_from_dict(d: dict[str, float]) -> np.ndarray:
    probabilities = np.array(list(d.values()), dtype=np.float64)
    if probabilities.sum() == 0.0:
        raise ValueError('Probabilities sum to 0')
    probabilities /= probabilities.sum()
    return probabilities


def probabilities_from_list(l: list[tuple[str, float]]) -> np.ndarray:
    probabilities = np.array([x[1] for x in l], dtype=np.float64)
    if probabilities.sum() == 0.0:
        raise ValueError('Probabilities sum to 0')
    probabilities /= probabilities.sum()
    return probabilities


def select_sublocation(composite_path: str, rng: np.random.Generator) -> str:
    with open(composite_path, 'r') as f:
        data = json.load(f)
    keys = np.array(list(data.keys()))
    p = probabilities_from_dict(data)
    return str(rng.choice(keys, p=p)).lower()


def list_locations() -> list[str]:
    """Return all location names that have data (regular or composite)."""
    locations = []
    for _dir in os.walk(str(DATA_DIR)):
        _, cur_dir = os.path.split(_dir[0])
        files = _dir[2]
        if f'{cur_dir}.json' in files or 'composite.json' in files:
            locations.append(cur_dir)
    return sorted(locations)


def get_file_path(target: str) -> Union[str, None]:
    target = target.lower().replace(' ', '_')
    target_file = f'{target}.json'
    for _dir in os.walk(str(DATA_DIR)):
        files = _dir[2]
        _, cur_dir = os.path.split(_dir[0])
        if cur_dir == target and target_file in files:
            return os.path.join(_dir[0], target_file)
    return None


def get_composite_path(target: str) -> Union[str, None]:
    target = target.lower().replace(' ', '_')
    for _dir in os.walk(str(DATA_DIR)):
        _, cur_dir = os.path.split(_dir[0])
        if cur_dir == target and 'composite.json' in _dir[2]:
            return os.path.join(_dir[0], 'composite.json')
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
    p = probabilities_from_dict(age_data)
    bucket = str(rng.choice(ages, p=p))
    return _parse_age_bucket(bucket, rng)


def gen_feature(data: dict, rng: np.random.Generator) -> str:
    collapsed = collapsed_dict(data)
    options = np.array([', '.join(reversed(x[0])) for x in collapsed])
    p = probabilities_from_list(collapsed)
    return str(rng.choice(options, p=p))


def gen_sample(
    data: dict,
    enabled_features: Union[set[str], None],
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
            elif feature != 'relationship' or sample.get('age', 16) >= 16:
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
            entry['subloc_probs'] = probabilities_from_dict(entry['data'])
        else:
            processed: dict[str, dict] = {}
            for feature, feature_data in entry['data'].items():
                if feature == '_meta':
                    continue
                if feature == 'age':
                    processed['age'] = {
                        'keys': np.array(list(feature_data.keys())),
                        'probs': probabilities_from_dict(feature_data),
                    }
                else:
                    col = collapsed_dict(feature_data)
                    processed[feature] = {
                        'options': np.array([', '.join(reversed(x[0])) for x in col]),
                        'probs': probabilities_from_list(col),
                    }
            entry['processed'] = processed
    return data


def gen_api_samples(
    location: str,
    data: dict,
    enabled_features: Union[set[str], None] = None,
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
    composite = data[location]['composite']

    samples = []
    for _ in range(N):
        if composite:
            target = str(rng.choice(
                data[location]['subloc_keys'],
                p=data[location]['subloc_probs'],
            ))
        else:
            target = location

        if target not in data:
            raise ValueError(f"Sublocation '{target}' not found in preloaded data")

        sample: dict[str, str | int] = {}
        for feature, proc in data[target]['processed'].items():
            if enabled_features is not None and feature not in enabled_features:
                continue
            if feature == 'age':
                bucket = str(rng.choice(proc['keys'], p=proc['probs']))
                sample['age'] = _parse_age_bucket(bucket, rng)
            elif feature != 'relationship' or sample.get('age', 16) >= 16:
                sample[feature] = str(rng.choice(proc['options'], p=proc['probs']))

        if composite:
            if 'location' in sample:
                sample['location'] += f', {target.title()}'
            else:
                sample['location'] = target.title()

        samples.append(sample)

    return samples


def gen_samples(
    location: str,
    enabled_features: Union[set[str], None] = None,
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
    composite_path = get_composite_path(location)
    composite = composite_path is not None

    samples = []
    cache: dict[str, dict] = {}
    for _ in range(N):
        target = select_sublocation(composite_path, rng) if composite else location

        location_path = get_file_path(target)
        if location_path is None:
            raise ValueError(f"Location '{target}' not found")
        if location_path in cache:
            file_data = cache[location_path]
        else:
            with open(location_path, 'r') as f:
                file_data = json.load(f)
            cache[location_path] = file_data

        sample = gen_sample(file_data, enabled_features, rng)
        if composite:
            if 'location' in sample:
                sample['location'] += f', {target.title()}'
            else:
                sample['location'] = target.title()
        samples.append(sample)

    return samples
