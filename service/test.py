import image_service as service
import image_id as iamgeFile 


def test():
    imageId =iamgeFile.image_id
    result = service.scan_image(imageId)
    
    print(imageId)
    print(result)

test()