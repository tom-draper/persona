all_features = {'age', 'sex', 'religion', 'sexuality', 'ethnicity', 'religion',
                'language', 'location', 'relationship'}

alias = {
    'uk': 'united kingdom',
    'usa': 'united states',
    'uae': 'united arab emirates'
}


def format_location(location: str) -> str:
    location = location.replace('-', '_').lower()
    if location in alias:
        location = alias
    return location
