from fastapi import APIRouter, Depends, HTTPException
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from schemas.container_schema import *
import service.container_service as manage
import service.exec_service as exec_manage

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

@router.post("/remove")
def read_item(container: Container):
    print(container.container_id)
    container = manage.delete_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    container.remove()
    return {"remove" :True}

@router.post("/exec")
def exec_container(container: ContainerExec):
    print(container.container_id)
    print("command: " + container.command)
    result = manage.exec_container(container.container_id, container.command)
    return {"output": result}

@router.websocket("/ws/{container_id}")
async def websocket_endpoint(websocket: WebSocket, container_id: str):
    exec_id = manage.exec_creat_container(container_id)
    sock = manage.exec_start_container(exec_id)
    data = sock.recv(2048)
    send = exec_manage.threadSend(websocket, sock)
    send.start()
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if data == "close":
            break
        sock.send(data.encode('utf-8'))
        # sock.send(data.encode())



