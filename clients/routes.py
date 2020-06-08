from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from auth.auth_utils import get_current_active_user
from clients.model import ClientDB
from database.mongodb import db
from database.mongodb_validators import fix_id, validate_object_id
from auth.model import LoginDB
from users.model import UserResponse

clients_router = APIRouter()


# Get User Function.
async def _get_client(id: str):
    _id = validate_object_id(id)
    client = await db.clients.find_one({"_id": _id})
    if client:
        return fix_id(client)
    else:
        raise HTTPException(status_code=404, detail="Client not found")


@clients_router.get("/", status_code=HTTP_200_OK)
async def get_all_clients(limit: int = 10, skip: int = 0,
                          current_user: UserResponse = Depends(get_current_active_user)):
    clients_cursor = db.clients.find().skip(skip).limit(limit)
    clients = await clients_cursor.to_list(length=limit)
    return list(map(fix_id, clients))


@clients_router.get("/{client_id}", status_code=HTTP_200_OK)
async def get_client_by_id(user_id: str):
    client = await _get_client(user_id)
    return client


@clients_router.put("/{client_id}", response_model=ClientDB)
async def update_client_by_id(client_id: str, client: ClientDB):
    result = await db.clients.update_one({"_id": ObjectId(client_id)}, {"$set": client.dict()})
    if result:
        return client.dict()


@clients_router.delete('/', status_code=HTTP_200_OK)
async def delete_client(client_id):
    await db.clients.delete_one({'_id': ObjectId(client_id)})


@clients_router.post('/', status_code=HTTP_201_CREATED, response_model=ClientDB)
async def create_user(name: str, phone: str, user_id: str):
    # TODO верификация что пользователь унеикальынй
    client = ClientDB(name=name, phone=phone, user_id=user_id)
    result = await db.clients.insert_one(client.dict())
    if result:
        return client
