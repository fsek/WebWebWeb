# WebWebWeb

Install these VSCode extensions:
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
- [SQLite Viewer](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer)

VSCode should not inconsitently highlight errors on different machines. Therefore we have a `.vscode/settings.json` which tells these extensions how to behave having this project opened.

## 0. Python
Install Python 3.12: https://www.python.org/downloads/

Then make sure you have the right version. Open your terminal and run `python --version`. 

## 1. Virtual environment
We use virtual environments to have a reproducible environment to run our project in. Create your virtual environment: `python -m venv ./.venv`.

Always activate your virtual environment when working on the project by running: 
- Windows: `.venv/Scripts/Activate`
- MacOS: `source /venv/bin/activate`

You should now see (.venv) in your terminal.

## 2. Installing dependencies
Our project will need packages not native to Python. FastAPI is one such dependency. The actual package files are not checked into Git. Instead, a file listing the required packages exists in the project.
The file `requirements.txt` lists all pip packages and versions needed. Install these by running:

`pip install -r requirements.txt`

If pulling or switching branch changes `requirements.txt` you will have to re-run this command to update packages in your `.venv`.

## 3. Start server 
`uvicorn main:app --reload`

Go to http://127.0.0.1:8000/docs for the Swagger page automatically generated by FastAPI 🎉
