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

def kill_container(container_id):
    container = get_container(container_id)
    if container is None:
        return None
    container.kill()
    return container

def pause_container(container_id):
    container = get_container(container_id)
    if container is None:
        return None
    container.pause()
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
    sock = client.api.exec_start(exec_id, tty=True, stream=True, socket=True)
    # client.api.exec_resize(exec_id,height=100,width=100)
    return sock._sock



# Required for CLI integration
# Codes below will be ignored when this file is imported by others,
# but will be work when solely executed as python script
# 
# Whenever a new funciton is added, be sure it is added in below
#
# Author: Ch1keen
def help(argv):
    help_string = "Usage: {} [COMMAND] [CONTAINER_ID]\n".format(argv[0])
    help_string += """
Available Commands:
  list     List containers
  start    Start a container
  stop     Stop a container
  restart  Restart a container
  delete   Delete a container
  kill     Kill a container
  pasue    Pause a container
  help     Show this help
    """

    print(help_string)

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1 or sys.argv[1] == "help":
        help(sys.argv)

    elif sys.argv[1] == "list":
        container_list = print_list()
        print(container_list)
    
    elif sys.argv[1] == "start":
        try:
            result = start_container(sys.argv[2])
            print(result)
        except IndexError:
            print("Error: No CONTAINER_ID was given\n")
            help(sys.argv)

    elif sys.argv[1] == "stop":
        try:
            result = stop_container(sys.argv[2])
            print(result)
        except IndexError:
            print("Error: No CONTAINER_ID was given\n")
            help(sys.argv)

    elif sys.argv[1] == "restart":
        try:
            result = restart_container(sys.argv[2])
            print(result)
        except IndexError:
            print("Error: No CONTAINER_ID was given\n")
            help(sys.argv)

    elif sys.argv[1] == "delete":
        try:
            result = delete_container(sys.argv[2])
            print(result)
        except IndexError:
            print("Error: No CONTAINER_ID was given\n")
            help(sys.argv)
            
    elif sys.argv[1] == "kill":
        try:
            result = kill_container(sys.argv[2])
            print(result)
        except IndexError:
            print("Error: No CONTAINER_ID was given\n")
            help(sys.argv)
            
    elif sys.argv[1] == "pause":
        try:
            result = pause_container(sys.argv[2])
            print(result)
        except IndexError:
            print("Error: No CONTAINER_ID was given\n")
            help(sys.argv)

    else:
        help(sys.argv)

