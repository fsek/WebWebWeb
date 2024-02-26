from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Web web web"}


namn = ["Gustav", "Tobias", 2]


@app.get("/name/{id}")
def getName(id: int):
    return {"name": namn[id]}

dic={111: "Gustav", 222: "Harald", 333: "Erik"}

@app.get("/info/{id}")
def getInfo(id: int):
    return dic[id]

@app.get("/info")
def getAll():
    return dic