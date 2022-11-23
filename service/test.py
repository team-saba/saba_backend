import image_service as service
import image_id as imageId

imageId =imageId.image_id

def test():
    result = service.scan_image(imageId)
    print(result)

test()