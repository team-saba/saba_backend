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

    
@router.post("/signing_image")
def signing_image(image: Image):
    print(image.image_id)
    result = manage.signing_image(image.image_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Image signing fail")
    return result


@router.post("/verify_image")
def verify_image(image: Image):
    print(image.image_id)
    result = manage.verify_image(image.image_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Image verify fail")
    return result


@router.post("/pull_image")
def verify_image(image: str, tag: str):
    result = manage.pull_image(image, tag)
    if result is None:
        raise HTTPException(status_code=404, detail="Image pull fail")
    return result


@router.post("/push_image")
def push_image(image_id: str, registry: str, repo: str, tag: str):
    result = manage.push_image(image_id, registry, repo, tag)
    if result is None:
        raise HTTPException(status_code=404, detail="Image push fail")
    return result


@router.post("/keygen")
def key_gen(password: str):
    result = manage.key_gen(password)
    if result is None:
        raise HTTPException(status_code=404, detail="Key does not found")
    return result


@router.post("/keydel")
def key_del(password: str):
    result = manage.key_del(password)
    if result is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return result


@router.post("/docker_login")
def docker_login(id: str, pw: str):
    result = manage.docker_login(id, pw)
    if result is None:
        raise HTTPException(status_code=404, detail="Docker login fail")
    return result


@router.post("/docker_logout")
def docker_logout():
    result = manage.docker_logout()
    if result is None:
        raise HTTPException(status_code=404, detail="Docker logout fail")
    return result


@router.post("/docker_login_check")
def docker_login_check():
    result = manage.docker_login_check()
    return result


@router.post("/docker_login_id_check")
def docker_login_id_check(user_id: str):
    result = manage.docker_login_id_check(user_id)
    return result