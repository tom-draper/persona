from os import getenv

from api_analytics.fastapi import Analytics
from fastapi import FastAPI, HTTPException

from src.api.handler import get_features, load_location_data
from src.lib.generate import gen_api_samples
from src.lib.format import clean_location

app = FastAPI()

api_key = getenv('API_KEY')
app.add_middleware(Analytics, api_key=api_key)

data = load_location_data()


@app.get("/v1/")
@app.get("/v1/help")
async def test() -> dict[str, str | dict]:
    return {
        "name": "Persona API (v1)",
        "description": "A REST API for probabilistically generating character profiles using real-world demographic data.",
        "github": "https://github.com/tom-draper/persona",
        "countries": await countries(),
        "example": "https://persona-api.vercel.app/v1/united_kingdom",
        "example_response": await gen_personas("united_kingdom")
    }


@app.get("/v1/countries/")
@app.get("/v1/locations/")
async def countries() -> list[dict]:
    return list(data.keys())


@app.get("/v1/{location}/features/")
async def features(location: str) -> list[str]:
    location = clean_location(location)
    if location not in data:
        raise HTTPException(status_code=404, detail="Location not found")
    elif location == 'global':
        raise HTTPException(status_code=404, detail="Features not found")
    return get_features(location, data)


@app.get("/v1/{location}/")
async def gen_personas(location: str, count: int = 1) -> list[dict]:
    location = clean_location(location)
    if location not in data:
        raise HTTPException(status_code=404, detail="Location not found")
    return gen_api_samples(location, data, N=count)
