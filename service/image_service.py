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
    scan_result = subprocess.run(["trivy", "image", "--security-checks", "vuln", image_id, "--quiet", "--format=json"], stdout=subprocess.PIPE)
    return {'scan_result': json.loads(scan_result.stdout)}

def delete_image(image_id):
    #TODO: delete_image
    image = get_image(image_id)
    if image is None:
        return None
    client.images.remove(image_id)
    return image


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

    else:
        help(sys.argv)

