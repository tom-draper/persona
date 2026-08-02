"""
Structural checks over the bundled demographic datasets.

These guard the data itself rather than the generation logic: every dataset
must parse, attribute all of its features to a source, and carry probability
distributions that actually look like distributions. Run with: pytest
"""

import itertools
import json

import pytest

from persona.lib.format import alias, clean_location
from persona.lib.generate import DATA_DIR

DATASETS = sorted(p for p in DATA_DIR.rglob("*.json") if p.name != "composite.json")
COMPOSITES = sorted(DATA_DIR.rglob("composite.json"))
ALL_FILES = sorted(DATA_DIR.rglob("*.json"))

# Every feature name any dataset is allowed to expose. Adding a feature here is
# deliberate: it should mean the same thing in every dataset that carries it.
CANONICAL_FEATURES = {
    "age",
    "country of birth",
    "education",
    "ethnicity",
    "housing tenure",
    "language",
    "location",
    "marital status",
    "occupation",
    "religion",
    "residence",
    "sex",
    "sexuality",
}

# Spellings that must never reappear, mapped to the label to use instead.
# Datasets may still carry extra categories their source reports (Canada's
# "Living common law", France's "Civil partnership (PACS)"); what they may not
# do is spell a shared category a second way.
FORBIDDEN_LABELS = {
    "sex": {"male": "Male", "female": "Female"},
    "marital status": {
        "Never married": "Single (never married)",
        "Single": "Single (never married)",
        "Married or in civil partnership": "Married",
    },
    "religion": {
        "Christian": "Christianity or Other Christianity",
        "Catholic": "Roman Catholicism",
        "Roman Catholic": "Roman Catholicism",
        "Protestant": "Protestantism",
        "Hindu": "Hinduism",
        "Buddhist": "Buddhism",
        "Orthodox": "Eastern Orthodoxy",
        "Orthodox Church": "Eastern Orthodoxy",
        "No religious affiliation": "No religion",
    },
    "housing tenure": {
        "Owner": "Owned",
        "Renter": "Rented",
        "Owner occupied": "Owned",
        "Owner-occupied": "Owned",
        "Renter occupied": "Rented",
        "Owner-occupied (outright)": "Owned outright",
        "Owner with mortgage": "Owned with mortgage",
        "Social rented (HLM)": "Social rented",
    },
    # A persona from Wales should be born in "Wales", not the uninformative
    # "UK". UK datasets name the constituent country; lumped labels are out.
    "country of birth": {
        "UK": "England, Wales, Scotland or Northern Ireland",
        "Rest of UK": "England, Wales, Scotland or Northern Ireland",
        "USA": "United States",
        "Ireland": "Republic of Ireland",
    },
}

# Datasets covering a UK nation must name the constituent countries of birth
# rather than collapsing them into a single "UK" bucket.
UK_BIRTH_COUNTRIES = {"England", "Wales", "Scotland", "Northern Ireland"}

# Long tails are routinely truncated, so distributions may fall short of 1.0.
# They must never exceed it by more than rounding, which would mean
# double-counted or mis-scaled categories.
MIN_MASS = 0.75
MAX_MASS = 1.01


def name(path):
    return str(path.relative_to(DATA_DIR))


def leaves(d):
    for v in d.values():
        if isinstance(v, dict):
            yield from leaves(v)
        else:
            yield v


def features(data):
    return {k: v for k, v in data.items() if k != "_meta"}


@pytest.fixture(scope="module")
def loaded():
    return {p: json.loads(p.read_text()) for p in ALL_FILES}


@pytest.mark.parametrize("path", ALL_FILES, ids=name)
def test_parses_as_json(path):
    json.loads(path.read_text())


@pytest.mark.parametrize("path", ALL_FILES, ids=name)
def test_has_at_least_one_source(path, loaded):
    sources = loaded[path].get("_meta", {}).get("sources", [])
    assert sources, f"{name(path)} has no _meta.sources"


@pytest.mark.parametrize("path", ALL_FILES, ids=name)
def test_sources_are_fully_specified(path, loaded):
    for source in loaded[path]["_meta"]["sources"]:
        for field in ("features", "name", "url", "year"):
            assert field in source, f"{name(path)}: source {source.get('name')!r} lacks {field}"
        assert source["url"].startswith("https://")
        assert isinstance(source["year"], int)


@pytest.mark.parametrize("path", DATASETS, ids=name)
def test_every_feature_is_attributed(path, loaded):
    data = loaded[path]
    covered = {f for s in data["_meta"]["sources"] for f in s["features"]}
    present = set(features(data))
    assert not (present - covered), f"{name(path)}: unattributed {sorted(present - covered)}"
    assert not (covered - present), (
        f"{name(path)}: source claims absent {sorted(covered - present)}"
    )


@pytest.mark.parametrize("path", DATASETS, ids=name)
def test_feature_names_are_canonical(path, loaded):
    unknown = set(features(loaded[path])) - CANONICAL_FEATURES
    assert not unknown, f"{name(path)}: non-canonical features {sorted(unknown)}"


@pytest.mark.parametrize("path", DATASETS, ids=name)
def test_distributions_have_plausible_mass(path, loaded):
    for feature, values in features(loaded[path]).items():
        mass = sum(leaves(values))
        assert MIN_MASS <= mass <= MAX_MASS, f"{name(path)} :: {feature} sums to {mass:.4f}"


@pytest.mark.parametrize("path", DATASETS, ids=name)
def test_weights_are_positive(path, loaded):
    for feature, values in features(loaded[path]).items():
        for weight in leaves(values):
            positive = isinstance(weight, int | float) and weight > 0
            assert positive, f"{name(path)} :: {feature} has a non-positive weight"


@pytest.mark.parametrize("path", DATASETS, ids=name)
def test_shared_labels_are_spelled_consistently(path, loaded):
    for feature, forbidden in FORBIDDEN_LABELS.items():
        values = loaded[path].get(feature)
        if values is None:
            continue
        for label in values:
            assert label not in forbidden, (
                f"{name(path)} :: {feature} uses {label!r}; use {forbidden[label]!r}"
            )


@pytest.mark.parametrize("path", DATASETS, ids=name)
def test_age_bands_are_contiguous_and_disjoint(path, loaded):
    bands = loaded[path].get("age")
    if bands is None:
        return
    bounds = []
    for band in bands:
        if band.endswith("+"):
            bounds.append((int(band[:-1]), None))
        else:
            low, high = band.split("-")
            bounds.append((int(low), int(high)))
    bounds.sort()
    assert bounds[0][0] == 0, f"{name(path)}: age does not start at 0"
    for (_, prev_high), (low, _) in itertools.pairwise(bounds):
        assert prev_high is not None, f"{name(path)}: open-ended band is not last"
        assert low == prev_high + 1, f"{name(path)}: gap or overlap at {prev_high}/{low}"


@pytest.mark.parametrize("path", DATASETS, ids=name)
def test_uk_datasets_name_the_country_of_birth(path, loaded):
    if "united_kingdom" not in str(path):
        return
    birth = loaded[path].get("country of birth")
    if birth is None:
        return
    named = UK_BIRTH_COUNTRIES & set(birth)
    assert len(named) >= 2, (
        f"{name(path)}: country of birth names only {sorted(named)}; "
        "UK nations should be listed individually"
    )


@pytest.mark.parametrize("path", COMPOSITES, ids=name)
def test_composite_weights_and_targets(path, loaded):
    weights = features(loaded[path])
    total = sum(weights.values())
    assert abs(total - 1.0) < 0.01, f"{name(path)} weights sum to {total}"
    for subloc in weights:
        target = clean_location(subloc)
        found = list(DATA_DIR.rglob(f"{target}/*.json"))
        assert found, f"{name(path)}: sublocation {subloc!r} resolves to no dataset"


def test_every_alias_resolves_to_a_dataset():
    for key, target in alias.items():
        found = list(DATA_DIR.rglob(f"{target}/*.json"))
        assert found, f"alias {key!r} -> {target!r} has no data"


def test_meta_never_leaks_into_generated_output():
    from persona.lib.generate import gen_samples

    for location in ("united_kingdom", "england", "australia"):
        for sample in gen_samples(location, N=20):
            assert "_meta" not in sample
            assert "_meta" not in sample.get("location", "")
