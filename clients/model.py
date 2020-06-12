from bson import ObjectId
from pydantic import BaseModel


class ClientDB(BaseModel):
    id: str
    name: str
    phone: str
    user_id: str


class ClientChange(BaseModel):
    name: str
    phone: str
