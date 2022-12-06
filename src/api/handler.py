import os
import json

def load_location_data() -> dict[dict]:
    data = {}
    for _dir in os.walk('data'):
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
    return data


def clean_location(location: str) -> str:
    return location.replace(' ', '_').lower()


def get_features(location: str, data: dict[dict]) -> list[str]:
    if location == 'global':
        return []
    elif data[location]['composite']:
        return {clean_location(subloc): list(data[clean_location(subloc)]['data'].keys()) for subloc in data[location]['data']}
    else:
        return {location: list(data[location]['data'].keys())}
