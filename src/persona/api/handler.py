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
        return {
            clean_location(subloc): [
                k for k in data[clean_location(subloc)]['data'].keys()
                if k != '_meta'
            ]
            for subloc in data[location]['data']
        }
    else:
        return {
            location: [
                k for k in data[location]['data'].keys()
                if k != '_meta'
            ]
        }
