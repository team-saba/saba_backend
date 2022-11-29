from fastapi import APIRouter

import routers.container.container as container
import routers.image.image as image
import routers.vulnerability.scan as scan
import routers.setting.setting as slack

api_router = APIRouter()

api_router.include_router(container.router, prefix='/container', tags=['container'])
api_router.include_router(image.router, prefix='/image', tags=['image'])
api_router.include_router(scan.router, prefix='/scan', tags=['scan'])
api_router.include_router(slack.router, prefix='/setting', tags=['setting'])
