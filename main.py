from cgitb import enable
import os
import sys
import json
import numpy as np
from colorama import Fore


def pprint(data):
    for sample in data:
        for k, v in sample.items():
            print(Fore.YELLOW + k.title() + ': ' + Fore.WHITE + str(v))


def get_file_path(target):
    target_file = f'{target.lower()}.json'
    target_path = None
    for _dir in os.walk('data'):
        files = _dir[2]
        if len(files) > 0 and target_file == files[0]:
            target_path = f'{_dir[0]}\\{target_file}'

    return target_path


def gen_age(age_data) -> int:
    ages = list(age_data.keys())
    probabilities = np.array(list(age_data.values()))
    if probabilities.sum() == 0.0:
        return None
    probabilities /= probabilities.sum()
    age = np.random.choice(ages, p=probabilities)
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


def gen_feature(data) -> str:
    collapsed = collapsed_dict(data, [], [])
    options = [', '.join(reversed(x[0])) for x in collapsed]
    probabilities = np.array([x[1] for x in collapsed], dtype=np.float64)

    if probabilities.sum() == 0.0:
        return None

    probabilities /= probabilities.sum()
    selected = np.random.choice(options, p=probabilities)
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
                else:
                    sample[feature] = gen_feature(_data)
        samples.append(sample)
    return samples

alias = {
    'uk': 'united_kingdom',
    'usa': 'united_states',
    'uae': 'united_arab_emirates'
}

def get_subcountry(target):
    target_path = get_file_path(target)
    if target_path:
        with open(target_path, 'r') as f:
            data = json.load(f)
            countries = list(data.keys())
            probabilities = list(data.values())
            selected = np.random.choice(countries, p=probabilities)
            return selected.lower().replace(' ', '_')
    return None

def has_subcountries(target):
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

def run():
    if len(sys.argv) == 1:
        return
    target = sys.argv[1].replace('-', '_')
    
    if target in alias:
        target = alias[target]
        
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
            samples = gen_samples(data, enabled_features)
            if subcountries:
                for sample in samples:
                    sample['location'] += f', {target.title()}'
            pprint(samples)
    else:
        print('Location not found')


if __name__ == '__main__':
    run()
