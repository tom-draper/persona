from fastapi import FastAPI
from src.main import gen_samples

app = FastAPI()


@app.get("/")
async def test():
    return {"Hello": "World"}

@app.get("/{location}")
async def gen_persona(location: str):
    return gen_samples(location)

@app.get("/{location}/{N}")
async def gen_multiple_personas(location: str, N: int):
    print(location, N)
    return gen_samples(location, N=N)