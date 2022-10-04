FROM python:alpine3.16

# install build-base(gcc) for uvicorn
RUN apk add build-base

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

RUN chmod +x entry.sh
ENTRYPOINT entry.sh
