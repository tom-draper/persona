from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse

from persona.api.handler import (
    get_available_features,
    get_features,
    load_location_data,
    resolve_path_key,
)
from persona.lib.generate import gen_api_samples

try:
    _VERSION = version("persona_generate")
except PackageNotFoundError:
    _VERSION = "0.1.2"


def _location_names(data: dict) -> list[str]:
    return sorted({v["name"] for v in data.values()})


_EXAMPLE_RESPONSE = [
    {
        "age": 34,
        "sex": "Female",
        "sexuality": "Heterosexual",
        "ethnicity": "British, White",
        "religion": "No religion",
        "language": "English",
        "location": "Trafford, North West",
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.data = load_location_data()
    yield


app = FastAPI(lifespan=lifespan)


def _location_not_found(data: dict) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={
            "message": "Location not found",
            "available": _location_names(data),
        },
    )


@app.get("/")
async def root():
    return RedirectResponse(url="/v1", status_code=308)


@app.get("/v1/")
@app.get("/v1/help")
async def help(request: Request) -> dict[str, str | list | dict]:
    data = request.app.state.data
    return {
        "name": "Persona",
        "version": _VERSION,
        "description": (
            "A REST API for probabilistically generating character profiles "
            "using real-world demographic data."
        ),
        "github": "https://github.com/tom-draper/persona",
        "locations": _location_names(data),
        "example": "https://persona-api.vercel.app/v1/united_kingdom",
        "example_response": _EXAMPLE_RESPONSE,
    }


@app.get("/v1/countries/")
@app.get("/v1/locations/")
async def locations(request: Request, response: Response) -> list[str]:
    response.headers["Cache-Control"] = "public, max-age=3600"
    return _location_names(request.app.state.data)


@app.get("/v1/{location:path}/features/")
async def features(location: str, request: Request, response: Response) -> dict:
    data = request.app.state.data
    if resolve_path_key(location, data) is None:
        raise _location_not_found(data)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return get_features(location, data)


@app.get("/v1/{location:path}/")
def gen_personas(
    location: str,
    request: Request,
    count: int = Query(default=1, ge=1, le=100),
    features: str | None = Query(
        default=None,
        description="Comma-separated features to include (e.g. age,sex,religion)",
    ),
    seed: int | None = Query(default=None, description="Random seed for reproducible output"),
) -> list[dict]:
    data = request.app.state.data
    if resolve_path_key(location, data) is None:
        raise _location_not_found(data)
    enabled_features = {f.strip() for f in features.split(",")} if features else None
    if enabled_features:
        available = get_available_features(location, data)
        invalid = enabled_features - available
        if invalid:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Invalid features requested",
                    "invalid": sorted(invalid),
                    "available": sorted(available),
                },
            )
    return gen_api_samples(location, data, enabled_features=enabled_features, N=count, seed=seed)
