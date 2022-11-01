import os
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
    age = np.random.choice(list(age_data.keys()), p=list(age_data.values()))
    if '-' in age:
        low, high = map(int, age.split('-'))
        age = np.random.randint(low, high+1)
    elif '+' in age:
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


def gen_samples(data, N=1) -> list[dict]:
    samples = []
    for _ in range(N):
        sample = {}
        for feature, _data in data.items():
            feature = feature.lower()
            if feature == 'age':
                sample[feature] = gen_age(_data)
            else:
                sample[feature] = gen_feature(_data)
        samples.append(sample)
        
    return samples

def run():
    target = 'england'
    print(Fore.CYAN + '> ' + target.title() + Fore.WHITE)
    target_path = get_file_path(target)
    
    if target_path:
        with open(target_path, 'r') as f:
            data = json.load(f)
            sample = gen_samples(data)
            pprint(sample)
    else:
        print('Location not found')




if __name__ == '__main__':
    run()
