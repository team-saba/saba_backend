import image_service as service
import image_id as iamgeFile 
import sys

print(sys.argv[0])
print(sys.argv[1])


def test():
    imageId =iamgeFile.image_id
    result = service.scan_image(imageId)
    
    print(imageId)
    print(result)

test()