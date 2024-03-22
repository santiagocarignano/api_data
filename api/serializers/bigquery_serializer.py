from pydantic import BaseModel


class ResponseSerializer(BaseModel):
    id: str
    message: str
    source: str
