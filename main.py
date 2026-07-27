from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "FastAPI çalışıyor"}

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Merhaba {name}"}