import docker
import subprocess
import json
import requests
import os.path
import dotenv
from dotenv import load_dotenv
import diskcache


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
dotenv_file = dotenv.find_dotenv()

client = docker.from_env()
sign_result = diskcache.Cache(directory="./cache/sign_result")

def print_list():
    images = client.images.list()
    images_json = [image.attrs for image in images]
    images_result = []
    for image in images_json:
        if image['Id'] in [container.image.id for container in client.containers.list()]:
            used = "True"
        else:
            used = "False"

        if sign_result.get(image['Id']) is None:
            signed = False
        else:
            print(sign_result.get(image['Id']))
            signed = True

        images_result.append(
            {
                'id': images_json.index(image),
                'Name': image['Id'],
                'RepoTags': image['RepoTags'],
                'RepoDigests': image['RepoDigests'],
                'Created': image['Created'],
                'Size': image['Size'],
                'VirtualSize': image['VirtualSize'],
                'Used': used,
                'signed': signed
            }
        )
    return images_result


def get_image(image_id):
    try:
        image = client.images.get(image_id)
    except docker.errors.NotFound:
        return None
    return image


def push_image(image_id):
    try:
        image = client.images.push(image_id)
    except docker.errors.NotFound:
        return None
    return image


def scan_image(image_id):
    image = get_image(image_id)
    if image is None:
        return None
    scan_result = subprocess.run(["trivy", "image", "--security-checks", "vuln", image_id, "--quiet", "--format=json"], stdout=subprocess.PIPE)
    scan_result_parsed = json.loads(scan_result.stdout)['Results']
    return {'scan_result': scan_result_parsed[0]['Vulnerabilities']}


def delete_image(image_id):
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


def signing_image(user_id, repo_name, image_tag, password):
    dotenv.set_key(dotenv_file, "COSIGN_PASSWORD", str(password))

def signing_image(image_id):
    image = get_image(image_id)
    image.tag(f"regi.seungwook.me/{image_id}")
    push_image(f"regi.seungwook.me/{image_id}")
    signing_result = subprocess.run(
        [
            "cosign",
            "sign",
            "--key",
            "cosign.key",
            f"regi.seungwook.me/{image_id}",
        ],
        stdout=subprocess.PIPE,
    )
    sign_result.set(image_id, "", retry=True)
    if signing_result.returncode != 0:
        return None
    return signing_result.stdout


def verify_image(image_id):
    verify_result = subprocess.run(
        [
            "cosign",
            "verify",
            "--key",
            "cosign.pub",
            f"regi.seungwook.me/{image_id}",
        ],
        stdout=subprocess.PIPE,
    )
    sign_result.set(image_id, verify_result.stdout, retry=True)
    if verify_result.returncode != 0:
        return None
    return verify_result.stdout


def tag_image(image, repo, tag):
    try:
        result = image.tag(repository=repo, tag=tag)
    except docker.errors.APIError:
        return None
    return result


def pull_image(image, tag):
    try:
        image = client.images.pull(repository=image, tag=tag)
    except docker.errors.APIError:
        return None
    return image.attrs


def push_image(image_id, registry, repo, tag):
    image = get_image(image_id)
    if image is None:
        return None

    repo_name = registry + "/" + repo
    tag_result = tag_image(image, repo_name, tag)
    if tag_result is False:
        return None

    try:
        result = client.images.push(repository=repo_name, tag=tag)
    except docker.errors.APIError:
        return None
    return result


def key_gen(password):
    if os.path.isfile("./cosign.key") and os.path.isfile("./cosign.pub"):
        return "COSIGN KEY is exist."
    dotenv.set_key(dotenv_file, "COSIGN_PASSWORD", str(password))
    subprocess.run(["cosign", "generate-key-pair"], stdout=subprocess.PIPE)
    cosign_key_data = open("cosign.pub","r").read()
    return {'key_gen_result': cosign_key_data}


# 키 삭제
def key_del(password):
    if not os.path.isfile("./cosign.key") and not os.path.isfile("./cosign.pub"):
        return "COSIGN KEY is not exist"
    os.remove("./cosign.key")
    os.remove("./cosign.pub")
    return {'key_del result' : 'cosign key is deleted'}


def docker_login(id, pw):
    try:
        login_result = client.login(username=id, password=pw, reauth=True)
    except docker.errors.APIError:
        return None
    return login_result


def docker_logout():
    logout_result = subprocess.run(["docker", "logout"], stdout=subprocess.PIPE)
    return logout_result


def docker_login_check():
    try:
        check_result = subprocess.run(["docker", "login"], stdout=subprocess.PIPE,timeout=3)
    except:
        result = "timeout exception"
        return result
    return check_result.stdout


def docker_login_id_check(user_id):
    id_check_result = subprocess.run(["docker", "info"], stdout=subprocess.PIPE)
    if str(id_check_result).find("Username: "+user_id) == -1:
        return 0
    return 1

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
    help_string = "Usage: login [USER_ID] [PASSWORD]\n"
    print(help_string)

def help_sign():
    help_string = "Usage: sign [USER_ID] [REPOSITORY_NAME], [IMAGE_TAG]"
    print(help_string)

def help_verify():
    help_string = "Usage: verify [USER_ID] [REPOSITORY_NAME], [IMAGE_TAG]"
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
            help_login()

    elif sys.argv[1] == "logout":
        result = docker_logout()
        print(result)


    elif sys.argv[1] == "sign":
        try:
            result = signing_image(sys.argv[2], sys.argv[3], sys.argv[4])
            print(result)
        except IndexError:
            help_sign()

    elif sys.argv[1] == "verify":
        try:
            result = verify_image(sys.argv[2], sys.argv[3], sys.argv[4])
            print(result)
        except IndexError:
            help_verify()

    elif sys.argv[1] == "pull":
        try:
            result = pull_image(sys.argv[2], sys.argv[3])
            print(result)
        except IndexError:
            print("Error")

    elif sys.argv[1] == "push":
        try:
            result = push_image(sys.argv[2], sys.argv[3], sys.argv[4])
            print(result)
        except IndexError:
            print("Error")

    elif sys.argv[1] == "keygen":
        try:
            result = key_gen(sys.argv[2])
            print(result)
        except IndexError:
            print("Error")

    elif sys.argv[1] == "keydel":
        try:
            result = key_del(sys.argv[2])
            print(result)
        except IndexError:
            print("Error")

    else:
        help(sys.argv)
