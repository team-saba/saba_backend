from pydantic import BaseModel

class Image(BaseModel):
    image_id: str

class Keyword(BaseModel):
    key: str
