import image_service as service
import image_id as imageId


def test():
    imageId =imageId.image_id
    result = service.scan_image(imageId)
    print(result)

test()