from pydantic import BaseModel


class ResponseSerializer(BaseModel):
    id: str
    user: str
    role: str
