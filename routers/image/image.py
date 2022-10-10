from fastapi import APIRouter, Depends, HTTPException
from schemas.image_schema import Image
import service.image_service as manage

router = APIRouter()

@router.get("/")
def read_item():
    images_json = manage.print_list()
    return {"images": images_json}

@router.post("/scan")
def scan_image(image: Image):
    print(image.image_id)
    result = manage.scan_image(image.image_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return result
