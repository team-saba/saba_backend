FROM python:alpine3.16

# install build-base(gcc) for uvicorn
RUN apk add build-base &&\
    apk add cosign &&\
    
    # Trivy is only in testing repository
    apk add trivy --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt &&\
    chmod +x entry.sh

ENTRYPOINT ./entry.sh
