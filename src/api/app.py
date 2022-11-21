from fastapi import FastAPI
from src.lib.generate import gen_samples
from src.lib.util import get_countries, get_features

app = FastAPI()


@app.get("/")
async def test():
    return "Live"


@app.get("/countries/")
@app.get("/locations/")
async def countries():
    return get_countries()


def format_location(location: str) -> str:
    location = location.replace('-', '_').lower()
    return location


@app.get("/{location}/features/")
async def features(location: str):
    location = format_location(location)
    return get_features(location)


@app.get("/{location}/")
async def gen_personas(location: str, count: int = 1):
    location = format_location(location)
    return gen_samples(location, N=count)
