from fastapi import FastAPI
from src.lib.generate import gen_samples
from src.lib.util import get_countries, get_features

app = FastAPI()


def format_location(county: str) -> str:
    location = location.replace('-', '_').lower()
    return location


@app.get("/")
async def test():
    return {"Hello": "World"}


@app.get("/{location}/")
async def gen_personas(location: str, count: int = 1):
    location = format_location(location)
    return gen_samples(location, N=count)


@app.get("/{location}/features")
async def gen_personas(location: str):
    location = format_location(location)
    return get_features(location)


@app.get("/countries/")
async def gen_personas():
    return get_countries()
