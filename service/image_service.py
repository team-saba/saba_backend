import docker
import subprocess
import json
import requests

client = docker.from_env()

def print_list():
    images = client.images.list()
    images_json = [image.attrs for image in images]
    images_result = []
    for image in images_json:
        if image['Id'] in [container.image.id for container in client.containers.list()]:
            used = True
        else:
            used = False

        images_result.append(
            {
                'Id': image['Id'],
                'RepoTags': image['RepoTags'][0],
                'Created': image['Created'],
                'Size': image['Size'],
                'VirtualSize': image['VirtualSize'],
                'Used': used
            }
        )
    return images_result

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
    scan_result = subprocess.run(["trivy", "image", "--security-checks", "vuln", image_id, "--quiet", "--format=json"], stdout=subprocess.PIPE)
    scan_result_parsed = json.loads(scan_result.stdout)['Results']
    return {'scan_result': scan_result_parsed}

def delete_image(image_id):
    #TODO: delete_image
    image = get_image(image_id)
    if image is None:
        return None
    client.images.remove(image_id)
    return image

def search_dockerhub(keyword):
    url = "https://hub.docker.com/api/content/v1/products/search?image_filter=official%2Cstore%2Copen_source&q={}".format(keyword)
    headers = {'Search-Version': 'v3'}
    response = requests.get(url, headers=headers)
    result = response.json()['summaries']
    if len(result) == 0:
        return None
    return result

def docker_login(id, pw):
    login_result = subprocess.run(["docker", "login", "-u", id, "-p", pw], stdout=subprocess.PIPE)
    if login_result.returncode == 0:
        return {'login_result': 1}
    return None
    
# Required for CLI integration
# Codes below will be ignored when this file is imported by others,
# but will be work when solely executed as python script
# 
# Whenever a new funciton is added, be sure it is added in below
#
# Author: Ch1keen
def help(argv):
    help_string = "Usage: {} [COMMAND] [IMAGE_ID]\n".format(argv[0])
    help_string += """
Available Commands:
  list     List images
  scan     Scan an image
  delete   Delete an image
  help     Show this help
    """

    print(help_string)
    
def help_login():
    help_string = "Usage: login [COMMAND] [ID] [Password]\n"
    print(help_string)

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1 or sys.argv[1] == "help":
        help(sys.argv)

    elif sys.argv[1] == "list":
        image_list = print_list()
        print(image_list)
    
    elif sys.argv[1] == "scan":
        try:
            result = scan_image(sys.argv[2])
            print(result)
        except IndexError:
            print("Error: No IMAGE_ID was given\n")
            help(sys.argv)

    elif sys.argv[1] == "delete":
        try:
            result = delete_image(sys.argv[2])
            print(result)
        except IndexError:
            print("Error: No IMAGE_ID was given\n")
            help(sys.argv)
            
        elif sys.argv[1] == "login":
        try:
            result = docker_login(sys.argv[2], sys.argv[3])
            print(result)
        except IndexError:
            print("Error: No ID or  Password was given\n")
            help_login()
            
    else:
        help(sys.argv)