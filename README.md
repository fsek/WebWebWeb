# <em>Web<sup>3</sup></em>

This repo uses VSCode's Dev Containers extension to standardize the development environment and avoid headache-inducing installation. All development will happen inside a Docker container which installs the same dependencies and versions on every developer's machine.

## Installation
0. Using Windows? First set up WSL 2.
    - Press Windows `⊞` -> "Turn Windows features on or off". Enable "Windows Subsystem for Linux", might need to enable "Virtual Machine Platform" also.
    - Open Powershell as admin.
    - `wsl --install`  
    - `wsl --set-default-version 2`
    - `wsl --install -d Ubuntu-22.04`
    - `wsl --set-default Ubuntu-22.04`
    -  For more info: [Microsoft documentation](https://learn.microsoft.com/en-us/windows/wsl/install)


1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/). 

    - Windows users: Make sure you select Use WSL 2 instead of Hyper-V if the option is presented.

1. Open a new VSCode window and install Dev Containers extension from the Extensions menu.
 
1. Open the Command Palette (`Ctrl + Shift + P` / `Cmd + Shift + P`) and select `Dev Containers: Clone Repository in Container Volume...`. Select `GitHub`, then enter `fsek/WebWebWeb.git`.

1. After configuration has finished in the open terminal, it should say `Done. Press any key to close the terminal`. Open `main.py` and make sure VSCode has selected our Python interpreter from `.venv` folder: In the bottom right corner of VSCode it should say approximately `Python 3.11.2 ('.venv': venv)`. Otherwise, open Command Palette -> `Python: Select Interpreter` and choose `./.venv/bin/python`. 

1. Open a new Bash terminal (`Ctrl + Shift + Ö`) and run `uvicorn main:app --reload`. Terminal should have (.env), otherwise run `source .venv/bin/activate`.

1. Go to http://127.0.0.1:8000/docs for the Swagger page automatically generated by FastAPI 🎉

1. From now on, whenever you want to open this project: Open a new VSCode window and in Recent, find `WebWebWeb in a unique volume [Dev Container]`. Don't re-run `Clone Repository...` from step 3.

## Play around
1. Try calling some routes. You will find some routes fail since you are not logged in. Find the "Authorize" button and login using boss@fsektionen.se `dabdab`. 

1. Call the GET `/users/me` route to view the logged in used. Change your last name to something creative by calling the PATCH `/users/me`.

1. Evidently, the database is already filled with some starting data. This was done in the `seed.py` file when the server started. Go check it out!

1. You can stop the FastAPI server anytime by entering `Ctrl+C` in the Bash terminal.

1. Run `python --version`. Every developer will run the same python version thanks to containers.

1. Run `pip list` to see all installed pip packages.


## Pip installing new packages
Our project will need packages not native to Python. FastAPI is one such dependency. The actual package files are not checked into Git. Instead, a file listing the required packages exists in the project.
The file `requirements.txt` lists all pip packages and versions needed. 

To add a new package, add a new line in `requirements.txt` specifiying package name and exact version. Then, in terminal, while in the `WebWebWeb` folder, run `pip install -r requirements.txt`.

