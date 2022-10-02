from fastapi import APIRouter, Depends, HTTPException
from schemas.container_schema import Container
import service.container_service as manage

router = APIRouter()

@router.get("/")
def read_item():
    containers_json = manage.print_list()
    return {"containers" :containers_json}

@router.post("/start")
def start_container(container: Container):
    print(container.container_id)
    container = manage.start_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return container.attrs

@router.post("/stop")
def read_item(container: Container):
    print(container.container_id)
    container = manage.stop_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    container.stop()
    return container.attrs

@router.post("/restart")
def read_item(container: Container):
    print(container.container_id)
    container = manage.restart_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    container.restart()
    return container.attrs

@router.post("/delete")
def read_item(container: Container):
    print(container.container_id)
    container = manage.delete_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    container.remove()
    return container.attrs