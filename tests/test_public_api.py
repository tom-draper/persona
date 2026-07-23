"""
Tests for the public `persona` package API.

These pin the surface that library users import, so anything asserted here is
a compatibility promise. Run with: pytest
"""

import json

import pytest

import persona


def test_top_level_exports():
    for symbol in persona.__all__:
        assert hasattr(persona, symbol), symbol


def test_version_is_populated():
    assert persona.__version__
    assert persona.__version__ != "0.0.0"


def test_generate_returns_a_single_persona():
    p = persona.generate("wales")
    assert isinstance(p, dict)
    assert p, "persona should not be empty"
    assert "age" in p


def test_generate_many_returns_the_requested_count():
    people = persona.generate_many("wales", 25)
    assert isinstance(people, list)
    assert len(people) == 25
    assert all(isinstance(p, dict) for p in people)


def test_generate_many_rejects_non_positive_counts():
    for n in (0, -1):
        with pytest.raises(ValueError, match="at least 1"):
            persona.generate_many("wales", n)


def test_features_argument_restricts_output():
    p = persona.generate("wales", features={"age", "sex"})
    assert set(p) <= {"age", "sex"}
    assert "religion" not in p


def test_seed_makes_output_reproducible():
    assert persona.generate("england", seed=7) == persona.generate("england", seed=7)
    assert persona.generate_many("england", 10, seed=7) == persona.generate_many(
        "england", 10, seed=7
    )


def test_different_seeds_differ():
    runs = {json.dumps(persona.generate_many("england", 5, seed=s)) for s in range(5)}
    assert len(runs) > 1


def test_aliases_are_accepted():
    for name in ("uk", "UK", "usa", "United States of America", "Northern Ireland"):
        assert persona.generate(name)


def test_unknown_location_raises():
    with pytest.raises(persona.UnknownLocationError) as excinfo:
        persona.generate("atlantis")
    assert excinfo.value.location == "atlantis"
    assert "wales" in excinfo.value.available


def test_unknown_feature_raises_and_reports_alternatives():
    with pytest.raises(persona.UnknownFeatureError) as excinfo:
        persona.generate("canada", features={"sexuality"})
    assert excinfo.value.invalid == ["sexuality"]
    assert "age" in excinfo.value.available


def test_errors_share_a_base_class():
    for exc in (persona.UnknownLocationError, persona.UnknownFeatureError):
        assert issubclass(exc, persona.PersonaError)
        # kept for callers written against the older bare-ValueError behaviour
        assert issubclass(exc, ValueError)


def test_locations_are_all_generatable():
    places = persona.locations()
    assert places == sorted(places)
    for place in places:
        assert persona.generate(place), place


def test_features_for_a_location_matches_what_is_generated():
    for place in ("wales", "canada", "australia"):
        available = persona.features(place)
        produced = set(persona.generate_many(place, 30)[0])
        assert produced <= available, place


def test_features_without_location_is_the_union():
    everything = persona.features()
    assert persona.features("wales") <= everything
    assert persona.features("canada") <= everything


def test_features_rejects_unknown_location():
    with pytest.raises(persona.UnknownLocationError):
        persona.features("atlantis")


def test_output_is_json_serialisable():
    json.dumps(persona.generate_many("united_kingdom", 5))


def test_composite_location_features_union_sublocations():
    uk = persona.features("united_kingdom")
    assert persona.features("wales") <= uk
    assert persona.features("scotland") <= uk
