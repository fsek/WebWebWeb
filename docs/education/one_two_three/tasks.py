from fastapi import FastAPI

app = FastAPI()

fun_tasks = [{"time": "Måndag 08:00", "description": "Kontinuerliga System föreläsning"}]
boring_tasks = [{"time": "Måndag 15:00", "description": "Codesprint"}]


@app.post("/addTask/{type}")
def addTask(task: dict[str, str], type: str):
    new_task = {"time": task["time"], "description": task["description"]}

    if type == "fun":
        fun_tasks.append(new_task)
    elif type == "boring":
        boring_tasks.append(new_task)

    return new_task


@app.get("/getTasks/{type}")
def getTasks(type: str):
    if type == "fun":
        return fun_tasks
    if type == "boring":
        return boring_tasks

    return {"message": "no such list"}
