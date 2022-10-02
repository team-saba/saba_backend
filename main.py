import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from routers.router import api_router

app = FastAPI(
    title='Saba API',
    description='BoB11기 프로젝트 Saba의 API 서버입니다.',
    version='0.1.0',
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router)

@app.get("/7qy38tiejfkdnojiwgu9eyhijdfk")
def server_checker():
    return {"Hello": "World"}

@app.get("/")
def root():
    return RedirectResponse(url='/static/index.html')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)