# saba_backend_ajax

## File Structure

```
.
├── dependencies.py     # Dependency Injection
├── docker-compose.yml  # Docker Compose
├── Dockerfile          # Dockerfile
├── entry.sh            # Entrypoint
├── __init__.py
├── main.py             # FastAPI
├── README.md
├── requirements.txt
├── routers             # Routers Directory
│   ├── container       # Docker Container Router Directory
│   │     ├── container.py  # Docker Container Router
│   │     └── __init__.py
│   ├── __init__.py
│   └── router.py       # FastAPI Router
│
├── schemas             # Schemas Directory
│   ├── container_schema.py # Docker Container Schema
│   └── __init__.py
│       
├── service             # Service Directory
│   ├── container_service.py    # Docker Container Service
│   ├── image_service.py        # Docker Image Service
│   └── __init__.py
│   
├── static              # Static Directory (Frontend Temprary)
│   ├── css
│   │   └── 
│   ├── index.html
│   ├── index.js
│   ├── LICENSE
│   ├── package.json
│   └── README.md
```

## Using as independent Python script

`/service` 디렉토리에 있는 파이썬 스크립트는 독립적으로 실행할 수 있습니다.

* `service/container_service.py`

* `service/image_service.py`

### Dependency

* [trivy](https://github.com/aquasecurity/trivy)

  ```bash
  brew install trivy

  # if you use nix
  nix-shell -p trivy
  ```
  
  For Nix package manager users, it is recommended to use **unstable** nixpkgs channel (See [issue #016](https://github.com/team-saba/saba_backend_ajax/issues/16))

* docker

  ```bash
  python

  # if you use Nix
  nix-shell -p python310Packages.docker
  ```


## Troubleshoot

* entry.sh: No such file (...)

  Dockerfile에서 `ENTRYPOINT ./entry.sh` 부분을 `ENTRYPOINT /app/entry.sh`로 변경해보세요.
  
  Docker Compose로 사용한다면 docker-compose.yml를 수정해서 docker compose를 수정해 이미지를 직접 빌드합니다.
  
  ```bash
  # Comment this line not to use pre-built image
  #image: .../saba:latest
  ...
  # Uncommnt or add a build option to build the image
  # from modified Dockerfile
  build: .

  # now build and up the container in one-line command
  $ docker-compose up --build
  ```
* entry.sh: Permission Denied

  ```bash
  $ chmod 755 ./entry.sh
  ```
  
  Docker Compose를 사용한다면 docker-compose.yml를 위와 같이 수정해서 이미지를 직접 빌드합니다.

* Docker Compose에서 Volume 설정해서 소스 코드 변경한 것 핫 리로드하기

  uvicorn은 FastAPI 소스 코드가 변경되는걸 감지해서 바로 반영하는 기능(핫 리로드)을 갖추고 있습니다.
  
  docker-compose.yml에 아래 내용을 추가한 후, Docker Compose 환경에서 작업하면 핫 리로드를 사용할 수 있습니다.
  
  ```yaml
  ...
  volumes:
    - .:/app/    # 이 줄을 추가해서 현재 작업 중인 소스 코드와 도커 내부가 연결되도록 합니다.
    - ...
  ...
  ```

