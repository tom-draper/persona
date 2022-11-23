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
                except json.decoder.JSONDecodeError as e:
                    print(e)
    return data

    
def format_location(location: str) -> str:
    location = location.replace('-', '_').lower()
    return location


def get_features(location: str, data: dict[dict]) -> list[str]:
    if data[location]['composite']:
        return {subloc: list(subloc_data.keys())
                for subloc, subloc_data in data[location]['data'].items()}
    else:
        return {location: list(data[location]['data'].keys())}