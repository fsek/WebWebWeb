from fastapi import FastAPI
app = FastAPI()

@app.get('/beans')
def eat_beans():
  print('Nom nom')
  return { 'message': 'I love beans!' }

