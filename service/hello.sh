#!/bin/bash

if [ $# -eq 1 ]; then
  greeting=$1
elif [ $# -eq 2 ]; then
  greeting=$1
  name=$2
fi

echo "[hello.sh] ${greeting} ${name}\n"