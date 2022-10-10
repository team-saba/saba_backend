from fastapi import APIRouter

import routers.container.container as container
import routers.image.image as image

api_router = APIRouter()

api_router.include_router(container.router, prefix='/container', tags=['container'])
api_router.include_router(image.router, prefix='/image', tags=['image'])
