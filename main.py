import json
import os
import sys

import numpy as np
from colorama import Fore


def pprint(data):
    for i, sample in enumerate(data):
        if len(data) > 1:
            print(Fore.CYAN + f'Persona {i+1}')
        for k, v in sample.items():
            print(Fore.YELLOW + k.title() + ': ' + Fore.WHITE + str(v))
        print()


def get_file_path(target):
    target_file = f'{target.lower().replace(" ", "_")}.json'
    target_path = None
    for _dir in os.walk('data'):
        files = _dir[2]
        if len(files) > 0 and target_file == files[0]:
            target_path = f'{_dir[0]}\\{target_file}'
            
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


def collapsed_dict(d: dict, path: list[str],
                   collapsed: list[tuple[list[str], float]]) -> list[tuple[list[str], float]]:
    for k, v in d.items():
        new_path = path + [k]
        if type(v) is not dict:
            collapsed.append((new_path, v))
        else:
            collapsed_dict(v, new_path, collapsed)

    return collapsed


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


def gen_feature(data: list[tuple[str, float]]) -> str | None:
    collapsed = collapsed_dict(data, [], [])
    options = [', '.join(reversed(x[0])) for x in collapsed]
    p = probabilities_from_list(collapsed)
    selected = np.random.choice(options, p=p)
    return selected


def gen_samples(data, enabled_features, N=1) -> list[dict]:
    samples = []
    for _ in range(N):
        sample = {}
        for feature, _data in data.items():
            feature = feature.lower()
            if feature in enabled_features:
                if feature == 'age':
                    sample[feature] = gen_age(_data)
                elif feature != 'relationship' or sample['age'] >= 16:
                    sample[feature] = gen_feature(_data)
        samples.append(sample)
    return samples


alias = {
    'uk': 'united kingdom',
    'usa': 'united states',
    'uae': 'united arab emirates'
}


def get_subcountry(target):
    target_path = get_file_path(target)
    if target_path:
        with open(target_path, 'r') as f:
            data = json.load(f)
            countries = list(data.keys())
            p = probabilities_from_dict(data)
            selected = np.random.choice(countries, p=p)
            return selected.lower()
    raise ValueError('Location not found.')


def has_subcountries(target):
    target = target.replace(' ', '_')
    return target == 'united_kingdom' or target == 'united_states'


def get_enabled_features() -> set[str]:
    all_features = {'age', 'sex', 'religion', 'sexuality', 'ethnicity', 'religion',
                    'language', 'location', 'relationship'}
    enabled_features = set()
    for arg in sys.argv:
        arg = arg.replace('-', '')
        if arg in all_features:
            enabled_features.add(arg)
    if len(enabled_features) == 0:
        enabled_features = all_features
    return enabled_features


def get_target_country():
    target = sys.argv[1].replace('-', ' ').replace('_', ' ')
    if target in alias:
        target = alias[target]
    return target


def run():
    if len(sys.argv) == 1:
        return
    target = get_target_country()

    enabled_features = get_enabled_features()

    print(Fore.CYAN + '> ' + target.title() + Fore.WHITE)

    subcountries = False
    if has_subcountries(target):
        target = get_subcountry(target)
        subcountries = True

    target_path = get_file_path(target)

    if target_path:
        with open(target_path, 'r') as f:
            data = json.load(f)
            samples = gen_samples(data, enabled_features, 500)
            if subcountries:
                for sample in samples:
                    sample['location'] += f', {target.title()}'
            pprint(samples)
    else:
        print('Location not found')


if __name__ == '__main__':
    run()