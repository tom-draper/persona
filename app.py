from fastapi import FastAPI
from main import gen_samples

app = FastAPI()


@app.get("/")
def root():
    return {"Hello": "World"}

@app.get("/{location}")
def gen_persona(location: str):
    print(location)
    return gen_samples(location)

@app.get("/{location}/{N}")
def gen_multiple_personas(location: str, N: int):
    print(location, N)
    return gen_samples(location, N=N)