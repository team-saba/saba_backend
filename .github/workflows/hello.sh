#!/bin/bash
imageId=$1
echo "[image Id] ${imageId}\n"
python -c 'import service.image_service as service; 
result = service.scan_image(${imageId});
print(result)'