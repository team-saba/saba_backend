from fastapi import APIRouter

import routers.container.container as container

api_router = APIRouter()

api_router.include_router(container.router, prefix='/container', tags=['container'])