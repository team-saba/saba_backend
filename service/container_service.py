import docker
import json

client = docker.from_env()
docketAPI = docker.APIClient()

#컨테이너 리스트 보기위한 test code 
def run_container_list():
    containers = client.containers.list()
    containers = [container.attrs for container in containers]
    return containers

def print_list():
    containers = client.containers.list(all)
    containers_json = [container.attrs for container in containers]
    containers_result=[]
    for container in containers_json:
        containers_result.append(
            {
                'idx' : containers_json.index(container),
                'CONTAINER_ID' : container['Id'],
                'Stack' : container['Path'],
                'Name' : container['Name'],
                'Created Time' : container['Created'],
                'Status' : container['State']['Status'],
                'IPAddress' : container['NetworkSettings']['IPAddress'],
                'Port' : container['NetworkSettings']['Ports'], 
                'Image' : container['Image']

            }
        )
    return containers_result

def get_container(container_id):
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        return None
    return container

# 개별 컨테이너에 대한 info
def container_info(container_id):
    container = get_container(container_id)
    if container is None:
        return None
    container_info_result=[]
    container_info_result.append(
        {
            'ID': container.attrs['Id'],
            'Name': container.attrs['Name'],
            'Status': container.attrs['State']['Status'],
            'Created': container.attrs['Created']
        }
    )
    #container_info_result=container.attrs['Id']
    return container_info_result

def print_log(container_id):
    container = get_container(container_id)
    if container is None:
        return None
    container_log_result=[]
    container_log_result=container.attrs['State']['Health']['Log']
    return container_log_result

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
  help     Show this help
    """

    print(help_string)

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1 or sys.argv[1] == "help":
        help(sys.argv)

    #테스트 코드
    elif sys.argv[1] == "test_list":
        container_test_list = test_container_list()
        print(container_test_list)

    elif sys.argv[1] == "list":
        container_list = print_list()
        print(container_list)

    elif sys.argvs[1] == "printlog":
        try:
            result = print_log(sys.argv[2])
            print(result)
        except IndexError:
            print("Error: No CONTAINER_ID was given\n")
            help(sys.argv)
    
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

    else:
        help(sys.argv)

