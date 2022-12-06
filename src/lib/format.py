

alias = {
    'uk': 'united_kingdom',
    'usa': 'united_states',
    'uae': 'united_arab_emirates',
    'world': 'global',
}


def clean_location(location: str) -> str:
    location = location.replace('-', '_').lower()
    if location in alias:
        location = alias[location]
    return location
