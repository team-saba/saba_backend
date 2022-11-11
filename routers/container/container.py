from fastapi import APIRouter, Depends, HTTPException
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from schemas.container_schema import *
import service.container_service as manage

import chardet

router = APIRouter()

@router.get("/")
def read_item():
    containers_json = manage.print_list()
    return {"containers" :containers_json}

#컨테이너 테스트 코드
@router.post("/testlist")
def test_container_list():
    containers_json = manage.test_container_list()
    return {"containers" :containers_json}

#컨테이너 개별 info
@router.post("/info")
def print_log(container: Container):
    print(container.container_id)
    result = manage.container_info(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return result

@router.post("/printlog")
def print_log(container: Container):
    print(container.container_id)
    result = manage.print_log(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return result

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
    # container.stop()
    return container.attrs

@router.post("/restart")
def read_item(container: Container):
    print(container.container_id)
    container = manage.restart_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    # container.restart()
    return container.attrs

@router.post("/remove")
def read_item(container: Container):
    print(container.container_id)
    container = manage.delete_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    # container.remove()
    return {"remove" :True}

@router.post("/kill")
def kill_container(container: Container):
    print(container.container_id)
    container = manage.kill_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return {"kill" :True}

@router.post("/pause")
def pause_container(container: Container):
    print(container.container_id)
    container = manage.pause_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return {"pause" :True}

@router.post("/resume")
def resume_container(container: Container):
    print(container.container_id)
    container = manage.resume_container(container.container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return {"resume" :True}

@router.post("/rename")
def rename_container(container: Container, new_name: str):
    print(container.container_id)
    container = manage.rename_container(container.container_id, new_name)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return {"rename" :True}

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
    # sock 타임아웃 지정
    sock.settimeout(2)
    await websocket.accept()
    # await websocket.send_text(sock.recv(2048).decode('utf-8'))
    while True:
        print("recv 1")
        data = await websocket.receive_text()
        print("recv 2")
        
        if data == "\0":
            print("recv 3")
            # continue
            
        if data is not None:
            print("data is not none")
            sock.send(data.encode('utf-8'))
        

        print("docker stream stdout")
        try:
            dockerStreamStdout = sock.recv(2048)
            print("dcker stream stdout 1")
            
            dockerStreamStdout = dockerStreamStdout.decode('utf-8')

            if dockerStreamStdout is '?':
                await websocket.send_text("")
                continue

            if dockerStreamStdout is not None:
                print("dcker stream stdout is not none")
                # encoding = chardet.detect(dockerStreamStdout).get('encoding')
                print("websocket send text 1")
                # await websocket.send_text(str(dockerStreamStdout, encoding=encoding or "utf-8"))
                await websocket.send_text(dockerStreamStdout)
                print("websocket send text 2")
            else:
                print("docker daemon socket is close")
                await websocket.close()
                sock.close()
                break

        except Exception as e:
            print(e)
            print("docker daemon socket is close")
            await websocket.close()
            sock.close()
            break

    print("websocket close")

