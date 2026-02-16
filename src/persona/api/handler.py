import json
import os
from pathlib import Path

from persona.lib.format import clean_location
from persona.lib.generate import preprocess_location_data

DATA_DIR = Path(__file__).parent.parent / 'data'


def load_location_data() -> dict:
    data = {}
    for _dir in os.walk(str(DATA_DIR)):
        files = _dir[2]
        _, location = os.path.split(_dir[0])
        for f in files:
            if f.endswith('.json'):
                try:
                    with open(os.path.join(_dir[0], f)) as _f:
                        composite = f == 'composite.json'
                        data[location] = {
                            'composite': composite,
                            'data': json.load(_f)
                        }
                except json.decoder.JSONDecodeError:
                    pass
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
