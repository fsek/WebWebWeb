"""Create an API for making tasks in TODO lists. Requrements:

There should be two different lists, fun_tasks and boring_tasks to add tasks to. Which one is choosen by a path parameter.

A task has a time and a description

You should be able to view either list using a GET-request"""


from fastapi import FastAPI
app = FastAPI()

fun_tasks : list[dict[str, str]] = []

boring_tasks : list[dict[str, str]] = []


email_list : list[str] = []

@app.post('/signup')
def signup(body: dict[str, str]):
    email_list.append(body["email"])
    return { 'message': 'User Added' }


@app.get("/get_tasks/{task_type}")
def get_tasks(task_type: str):
    if task_type == "fun_tasks":
        return fun_tasks
    elif task_type == "boring_tasks":
        return boring_tasks
    else:
        return {"error": "Invalid task type"}


@app.post("/add_task/{task_type}")
def add_task(task_type: str, task: dict[str, str]):
    task = {"time": task["time"], "description": task["description"]}
    if task_type == "fun_tasks":
        fun_tasks.append(task)
    elif task_type == "boring_tasks":
        boring_tasks.append(task)
    else:
        return {"error": "Invalid task type"}
    return {"message": "Task added"}
