import docker

client = docker.from_env()

def print_list():
    containers = client.containers.list(all)
    containers = [container.attrs for container in containers]
    return containers

def get_container(container_id):
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        return None
    return container

def start_container(container_id):
    container = get_container(container_id)
    if container is None:
        return None
    container.start()
    return container

def stop_container(container_id):
    container = get_container(container_id)
    if container is None:
        return None
    container.stop()
    return container