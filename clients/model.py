from pydantic import BaseModel


class ClientDB(BaseModel):
    id: str
    name: str
    phone: str
    user_id: str