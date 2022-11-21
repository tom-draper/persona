import json
import os
from typing import Union

import numpy as np


def has_subcountries(target: str) -> bool:
    target = target.replace(' ', '_')
    return target == 'united_kingdom' or target == 'united_states'


def probabilities_from_dict(d: dict[str, float]) -> np.array:
    probabilities = np.array(list(d.values()), dtype=np.float64)
    if probabilities.sum() == 0.0:
        raise ValueError('Probabilities sum to 0')
    probabilities /= probabilities.sum()
    return probabilities


def probabilities_from_list(l: list[tuple[str, float]]) -> np.array:
    probabilities = np.array([x[1] for x in l], dtype=np.float64)
    if probabilities.sum() == 0.0:
        raise ValueError('Probabilities sum to 0')
    probabilities /= probabilities.sum()
    return probabilities


def get_subcountry(target: str) -> str:
    target_path = get_file_path(target)
    if target_path:
        with open(target_path, 'r') as f:
            data = json.load(f)
            countries = list(data.keys())
            p = probabilities_from_dict(data)
            selected = np.random.choice(countries, p=p)
            return selected.lower()
    raise ValueError('Location not found.')


def get_file_path(target: str) -> str:
    target_file = f'{target.lower().replace(" ", "_")}.json'
    target_path = None
    for _dir in os.walk('data'):
        files = _dir[2]
        for f in files:
            if target_file == f:
                target_path = os.path.join(_dir[0], target_file)
                break

    return target_path


def gen_age(age_data: dict[str, float]) -> int:
    ages = list(age_data.keys())
    p = probabilities_from_dict(age_data)
    age = np.random.choice(ages, p=p)
    if '-' in age:
        low, high = map(int, age.split('-'))
        # Assume uniform likelihood within age range
        age = np.random.randint(low, high+1)
    elif '+' in age:
        age = int(age.replace('+', ''))
        age = np.random.randint(age, age+15)

    return int(age)


def collapsed_dict(d: dict, path: list[str], collapsed: list[tuple[list[str], float]]
                   ) -> list[tuple[list[str], float]]:
    for k, v in d.items():
        new_path = path + [k]
        if type(v) is not dict:
            collapsed.append((new_path, v))
        else:
            collapsed_dict(v, new_path, collapsed)

    return collapsed


def gen_feature(data: list[tuple[str, float]]) -> Union[str, None]:
    collapsed = collapsed_dict(data, [], [])
    options = [', '.join(reversed(x[0])) for x in collapsed]
    p = probabilities_from_list(collapsed)
    selected = np.random.choice(options, p=p)
    return selected


def gen_sample(data: dict[str, float], enabled_features: Union[set[str], None]) -> dict[str, str]:
    sample = {}
    for feature, _data in data.items():
        feature = feature.lower()
        if enabled_features is None or feature in enabled_features:
            if feature == 'age':
                sample[feature] = gen_age(_data)
            elif feature != 'relationship' or sample['age'] >= 16:
                sample[feature] = gen_feature(_data)

    return sample


def gen_samples(
    target: str,
    enabled_features: Union[set[str], None] = None,
    N: int = 1
):
    """
    Returns randomly generated persona(s) for the given target location, 
    constrained by any optional enabled features.

    Arguments
        target: str - Target location.
        enabled_features: set[str]|None - Set of features to include in the 
            persona. If None, all features are included. Defaults to None.
        N: int - The number of personas to generate from the given target 
            location. Defaults to 1.
    """
    original_target = target
    select_subcountry = has_subcountries(target)

    samples = []
    cache = {}
    for _ in range(N):
        if select_subcountry:
            target = get_subcountry(original_target)

        if target_path := get_file_path(target):
            if target_path in cache:  # If already read, take from cache
                data = cache[target_path]
            else:
                with open(target_path, 'r') as f:
                    data = json.load(f)
                    cache[target_path] = data  # Cache data to avoid re-reading

            sample = gen_sample(data, enabled_features)
            if select_subcountry:
                # Append original target location
                sample['location'] += f', {target.title()}'
            samples.append(sample)
        else:
            print('Location not found')

    return samples
