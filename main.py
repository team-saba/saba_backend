import multiprocessing
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from routers.router import api_router

from typing import List, Dict
from DTO.VulnerabilityRequest import VulnerabilityRequest
from DTO.VulnerabilityProcessElement import VulnerabilityProcessElement

WORKER_PROCESS: Dict[str, VulnerabilityProcessElement] = dict()

app = FastAPI(
    title='Saba API',
    description='BoB11기 프로젝트 Saba의 API 서버입니다.',
    version='0.1.0',
)
# app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router)

@app.get("/7qy38tiejfkdnojiwgu9eyhijdfk")
def server_checker():
    return {"Hello": "World"}

@app.get("/")
def root():
    return RedirectResponse(url='/static/index.html')

@app.get("/console")
def root():
    return RedirectResponse(url='/static/console.html')

if __name__ == "__main__":
    multiprocessing.freeze_support()
    uvicorn.run(app, host="0.0.0.0", port=8001)