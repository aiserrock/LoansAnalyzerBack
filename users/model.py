from pydantic import BaseModel


class UserDB(BaseModel):
    _id: str
    name: str
    username: str
    password: str
    disabled: bool = 0


class UserResponse(BaseModel):
    _id: str
    name: str
    username: str
