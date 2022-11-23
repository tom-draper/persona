from fastapi import FastAPI, HTTPException

from src.api.util import get_features, load_location_data
from src.lib.generate import gen_api_samples
from src.lib.util import format_location

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
    if location not in data:
        raise HTTPException(status_code=404, detail="Location not found")
    return get_features(location)


@app.get("/v1/{location}/")
async def gen_personas(location: str, count: int = 1):
    location = format_location(location)
    if location not in data:
        raise HTTPException(status_code=404, detail="Location not found")
    return gen_api_samples(location, data, N=count)
