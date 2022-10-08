from pydantic import BaseModel

class Container(BaseModel):
    container_id: str

class ContainerExec(BaseModel):
    container_id: str
    command: str
