#!/bin/bash

if [ $# -eq 1 ]; then
  imageId=$1
  echo "[image Id] ${imageId}\n"

# 1. scan/start_reservation_process
# 2. scan/result
# 3. save result of scan/result, check critical vulnerability count of scanResult
# 4. siging image according to diagnosis
# 5. return result of each step

