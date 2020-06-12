from pydantic import BaseModel


class UserDB(BaseModel):
    id: str
    name: str
    username: str
    password: str
    disabled: bool = 0


class UserResponse(BaseModel):
    id: str
    name: str
    username: str


class UserChange(BaseModel):
    name: str
    password: str
