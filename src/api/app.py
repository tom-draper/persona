from fastapi import FastAPI
from src.lib.generate import gen_samples

app = FastAPI()


@app.get("/")
async def test():
    return {"Hello": "World"}


@app.get("/{location}/")
async def gen_personas(location: str, count: int = 1):
    location = location.replace('-', '_')
    return gen_samples(location, N=count)
