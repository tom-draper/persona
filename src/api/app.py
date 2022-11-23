
from fastapi import FastAPI

from src.lib.api_helper import load_location_data, get_features, format_location
from src.lib.generate import gen_api_samples

app = FastAPI()


data = load_location_data()


@app.get("/v1/")
async def test():
    return "Persona v1 - Live"


@app.get("/v1/countries/")
@app.get("/v1/locations/")
async def countries():
    return list(data.keys())


@app.get("/v1/{location}/features/")
async def features(location: str):
    location = format_location(location)
    return get_features(location)


@app.get("/v1/{location}/")
async def gen_personas(location: str, count: int = 1):
    location = format_location(location)
    return gen_api_samples(location, data, N=count)
