from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse

from persona.api.handler import get_features, load_location_data
from persona.lib.format import clean_location
from persona.lib.generate import gen_api_samples

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
            "available": sorted(data.keys()),
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
        "name": "Persona API (v1)",
        "description": "A REST API for probabilistically generating character profiles using real-world demographic data.",
        "github": "https://github.com/tom-draper/persona",
        "locations": sorted(data.keys()),
        "example": "https://persona-api.vercel.app/v1/united_kingdom",
        "example_response": _EXAMPLE_RESPONSE,
    }


@app.get("/v1/countries/")
@app.get("/v1/locations/")
async def locations(request: Request, response: Response) -> list[str]:
    response.headers["Cache-Control"] = "public, max-age=3600"
    return sorted(request.app.state.data.keys())


@app.get("/v1/{location}/features/")
async def features(location: str, request: Request, response: Response) -> dict:
    data = request.app.state.data
    location = clean_location(location)
    if location not in data:
        raise _location_not_found(data)
    elif location == 'global':
        raise HTTPException(status_code=404, detail="Features not found")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return get_features(location, data)


@app.get("/v1/{location}/")
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
    location = clean_location(location)
    if location not in data:
        raise _location_not_found(data)
    enabled_features = {f.strip() for f in features.split(',')} if features else None
    return gen_api_samples(location, data, enabled_features=enabled_features, N=count, seed=seed)
