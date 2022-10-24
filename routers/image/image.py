from fastapi import APIRouter, Depends, HTTPException
from schemas.image_schema import Image, Keyword
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

@router.post("/search")
def search_image(keyword: Keyword):
    result = manage.search_dockerhub(keyword.key)
    if result is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return result

@router.post("/delete")
def delete_image(image: Image):
    result = manage.delete_image(image.image_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return result