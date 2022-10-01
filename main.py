import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from pydantic import BaseModel

from typing import Union

from core import docker_manage

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class Container(BaseModel):
    container_id: str

@app.get("/test")
def read_root():
    return {"Hello": "World"}

@app.get("/")
def root():
    return RedirectResponse(url='/static/index.html')

@app.get("/container")
def read_item():
    containers_json = docker_manage.print_list()
    return {"containers" :containers_json}

@app.post("/container/start")
def start_container(container: Container):
    print(container.container_id)
    container = docker_manage.start_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return container.attrs

@app.post("/container/stop")
def read_item(container: Container):
    print(container.container_id)
    container = docker_manage.stop_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    container.stop()
    return container.attrs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)