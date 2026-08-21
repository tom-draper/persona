"""HTTP contract tests for the public FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from persona.api.app import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root_redirects_to_api_help(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 308
    assert response.headers["location"] == "/v1"


def test_locations_are_cacheable(client):
    response = client.get("/v1/locations/")

    assert response.status_code == 200
    assert "england" in response.json()
    assert response.headers["cache-control"] == "public, max-age=3600"


def test_location_paths_include_canonical_nested_path(client):
    response = client.get("/v1/location-paths/")

    assert response.status_code == 200
    assert "united_states_of_america/georgia" in response.json()
    assert response.headers["cache-control"] == "public, max-age=3600"


def test_features_endpoint_returns_available_features(client):
    response = client.get("/v1/england/features/")

    assert response.status_code == 200
    assert {"age", "sex"} <= set(response.json()["england"])
    assert response.headers["cache-control"] == "public, max-age=3600"


def test_generation_honours_features_count_and_seed(client):
    response = client.get("/v1/england/?features=age,sex&count=2&seed=42")
    repeated = client.get("/v1/england/?features=age,sex&count=2&seed=42")

    assert response.status_code == 200
    assert response.json() == repeated.json()
    assert len(response.json()) == 2
    assert all(set(sample) == {"age", "sex"} for sample in response.json())


def test_generation_rejects_invalid_count_and_features(client):
    count_response = client.get("/v1/england/?count=0")
    feature_response = client.get("/v1/england/?features=not_a_feature")

    assert count_response.status_code == 422
    assert feature_response.status_code == 422
    assert feature_response.json()["detail"]["invalid"] == ["not_a_feature"]


def test_unknown_location_includes_discovery_information(client):
    response = client.get("/v1/not_a_location/")

    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "Location not found"
    assert "england" in response.json()["detail"]["available"]
