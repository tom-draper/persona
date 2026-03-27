import json
import warnings
from pathlib import Path

from persona.lib.format import clean_location
from persona.lib.generate import preprocess_location_data

DATA_DIR = Path(__file__).parent.parent / 'data'


def load_location_data() -> dict:
    data = {}
    for path in DATA_DIR.rglob('*.json'):
        location = path.parent.name
        composite = path.name == 'composite.json'
        try:
            with open(path) as f:
                data[location] = {
                    'composite': composite,
                    'data': json.load(f)
                }
        except json.JSONDecodeError:
            warnings.warn(f"Skipping {path}: invalid JSON", stacklevel=2)
    return preprocess_location_data(data)


def get_features(location: str, data: dict) -> dict:
    if location == 'global':
        return {}
    elif data[location]['composite']:
        features: set[str] = set()
        for subloc in data[location]['data']:
            subloc_key = clean_location(subloc)
            features.update(k for k in data[subloc_key]['data'].keys() if k != '_meta')
        return {location: sorted(features)}
    else:
        return {
            location: [
                k for k in data[location]['data'].keys()
                if k != '_meta'
            ]
        }


def get_available_features(location: str, data: dict) -> set[str]:
    features_dict = get_features(location, data)
    result: set[str] = set()
    for feature_list in features_dict.values():
        result.update(feature_list)
    return result
