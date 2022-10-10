import docker
import subprocess
import json

client = docker.from_env()

def print_list():
    images = client.images.list()
    return [image.attrs for image in images]

def get_image(image_id):
    try:
        image = client.images.get(image_id)
    except docker.errors.NotFound:
        return None
    return image

def scan_image(image_id):
    image = get_image(image_id)
    if image is None:
        return None
    scan_result = subprocess.run(["trivy", "image", image_id, "--quiet", "--format=json"], stdout=subprocess.PIPE)
    return {'scan_result': json.loads(scan_result.stdout)}
