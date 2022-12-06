from os import getenv

from api_analytics.fastapi import Analytics
from fastapi import FastAPI, HTTPException

from src.api.util import get_features, load_location_data
from src.lib.generate import gen_api_samples
from src.lib.util import clean_location

app = FastAPI()

api_key = getenv('API_KEY')
app.add_middleware(Analytics, api_key=api_key)

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
    location = clean_location(location)
    if location not in data:
        raise HTTPException(status_code=404, detail="Location not found")
    return get_features(location, data)


@app.get("/v1/{location}/")
async def gen_personas(location: str, count: int = 1):
    location = clean_location(location)
    if location not in data:
        raise HTTPException(status_code=404, detail="Location not found")
    return gen_api_samples(location, data, N=count)
