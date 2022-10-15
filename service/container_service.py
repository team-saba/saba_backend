import docker


client = docker.from_env()
docketAPI = docker.APIClient()

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

def restart_container(container_id):
    container = get_container(container_id)
    if container is None:
        return None
    container.restart()
    return container

def delete_container(container_id):
    container = get_container(container_id)
    if container is None:
        return None
    container.remove()
    return container

def exec_container(container_id, command: str):
    # in order to check weather container is present
    container = get_container(container_id)
    if container is None:
        return None
    result = client.api.exec_create(container_id, command)
    return client.api.exec_start(result['Id'])

def exec_creat_container(container_id):
    execCommand = [
        "/bin/sh",
        "-c",
        'TERM=xterm-256color; export TERM; [ -x /bin/bash ] && ([ -x /usr/bin/script ] && /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) || exec /bin/sh']
    execOptions = {
        "tty": True,
        'stdout':True,
        'stderr':True,
        'stdin':True,
    }
    execId = client.api.exec_create(container_id, execCommand, **execOptions)
    
    return execId['Id']

def exec_start_container(exec_id):
    sock = client.api.exec_start(exec_id, tty=True, stream=True, socket=True ,demux=True)
    client.api.exec_resize(exec_id,height=100,width=118)
    return sock._sock

