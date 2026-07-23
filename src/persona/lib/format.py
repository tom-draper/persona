# Only aliases that resolve to a dataset belong here. `usa` and `uae` were
# removed: there is no United States composite (only three states) and no
# United Arab Emirates data at all.
alias = {
    "uk": "united_kingdom",
    "world": "global",
}


def clean_location(location: str) -> str:
    location = location.replace("-", "_").replace(" ", "_").lower()
    if location in alias:
        location = alias[location]
    return location
