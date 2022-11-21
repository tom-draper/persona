import json
import os


def get_countries() -> list[str]:
    countries = []
    for _dir in os.walk('data'):
        files = _dir[2]
        for f in files:
            if f.endswith('.json'):
                countries.append(f.replace('.json', ''))

    return countries


def _get_features(path: str) -> list[str]:
    with open(path, 'r') as f:
        data = json.load(f)
        return list(data.keys())


def get_features(country: str) -> list[str]:
    target_file = f'{country}.json'
    for _dir in os.walk('data'):
        files = _dir[2]
        for f in files:
            if f == target_file:
                return _get_features(os.path.join(_dir[0], target_file))

    return None


if __name__ == '__main__':
    print(get_countries())
