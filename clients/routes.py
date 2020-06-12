import logging

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from auth.auth_utils import get_current_active_user
from clients.model import ClientDB, ClientChange
from database.mongodb import db
from database.mongodb_validators import fix_id, validate_object_id
from users.model import UserResponse

clients_router = APIRouter()


# Get User Function.
async def _get_client(id: str, current_user: UserResponse):
    _id = validate_object_id(id)
    client = await db.clients.find_one({"$and": [{"_id": _id}, {"user_id": ObjectId(current_user.id)}]})
    if client:
        return fix_id(client)
    else:
        raise HTTPException(status_code=404, detail="Client not found")


@clients_router.get("/", status_code=HTTP_200_OK)
async def get_all_clients(current_user: UserResponse = Depends(get_current_active_user), limit: int = 10,
                          skip: int = 0):
    clients_cursor = db.clients.find({
        "user_id": ObjectId(current_user.id)
    }).skip(skip).limit(limit)
    clients = await clients_cursor.to_list(length=limit)
    return list(map(fix_id, clients))


@clients_router.get("/{client_id}", status_code=HTTP_200_OK)
async def get_client_by_id(client_id: str, current_user: UserResponse = Depends(get_current_active_user)):
    client = await _get_client(client_id, current_user)
    return client


@clients_router.put("/{client_id}", response_model=ClientDB)
async def update_client_by_id(client_id: str, client: ClientChange,
                              current_user: UserResponse = Depends(get_current_active_user)):
    result = await db.clients.update_one(
        {"$and": [{"_id": ObjectId(client_id)}, {"user_id": ObjectId(current_user.id)}]},
        {"$set": {
            "name": client.name,
            "phone": client.phone,
        }})
    if result:
        client = await db.clients.find_one({"_id": ObjectId(client_id)})
        return fix_id(client)
    else:
        raise HTTPException(status_code=500, detail="Сlient hasn't been changed")


@clients_router.delete('/', status_code=HTTP_200_OK)
async def delete_client(client_id, current_user: UserResponse = Depends(get_current_active_user)):
    await db.clients.delete_one({"$and": [{"_id": ObjectId(client_id)}, {"user_id": ObjectId(current_user.id)}]})


@clients_router.post('/', status_code=HTTP_201_CREATED, response_model=ClientDB)
async def create_user(name: str, phone: str, current_user: UserResponse = Depends(get_current_active_user)):
    # unic client?
    phone_count = await db.clients.count_documents({
        "phone": phone
    })
    if phone_count > 0:
        raise HTTPException(status_code=409, detail="This phone already exist. Try to use another one")
    # insert
    result = await db.clients.insert_one({
        "name": name,
        "phone": phone,
        "user_id": ObjectId(current_user.id)
    })
    if result:
        client = await db.clients.find_one({"_id": result.inserted_id})
        return fix_id(client)
    else:
        raise HTTPException(status_code=500, detail="Сlient hasn't been created")
