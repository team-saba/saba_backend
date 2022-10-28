import docker
import subprocess
import json
import requests
import os.path

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

# 키 생성
def key_gen():
    key_gen_result = subprocess.run(["cosign","generate-key-pair"],stdout=subprocess.PIPE)
    #key_gen_parsed = json.loads(key_gen_result.stdout)['Results']
    #password : ubnutu

    return {'key_gen_result' : key_gen_parsed}


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
    elif sys.argv[1] == "keygen":
        try:
            result = key_gen(sys.argv[2])
            print(result)
        except IndexError:
            print("Error")
    else:
        help(sys.argv)