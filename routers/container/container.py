from fastapi import APIRouter, Depends, HTTPException
from schemas.container_schema import Container

import docker
import json

client = docker.from_env()
router = APIRouter()

def get_container(container_id):
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        return None
    return container

@router.get("/")
def read_item():
    containers = client.containers.list(all)
    containers = [container.attrs for container in containers]
    return {"containers" : containers}

@router.post("/start")
def start_container(container: Container):
    container = get_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    container.start()
    return container.attrs

@router.post("/stop")
def read_item(container: Container):
    container = get_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    container.stop()
    return container.attrs