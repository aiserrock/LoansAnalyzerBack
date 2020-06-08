from bson import ObjectId
from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_200_OK
from database.mongodb import db
from database.mongodb_validators import fix_id, validate_object_id
from auth.model import LoginDB
from users.model import UserResponse, UserDB

users_router = APIRouter()


# Get User Function.
async def _get_user(id: str):
    _id = validate_object_id(id)
    user = await db.users.find_one({"_id": _id})
    if user:
        return fix_id(user)
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def _get_user_data_for_login(user_id: str):
    user = await _get_user(user_id)
    return LoginDB(login=user.get("auth"),password=user.get("password"))


@users_router.get("/", status_code=HTTP_200_OK)
async def get_all_users(limit: int = 10, skip: int = 0):
    users_cursor = db.users.find().skip(skip).limit(limit)
    users = await users_cursor.to_list(length=limit)
    return list(map(fix_id, users))


@users_router.get("/{user_id}", status_code=HTTP_200_OK)
async def get_user_by_id(user_id: str):
    user = await _get_user(user_id)
    return user



@users_router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(user_id: str, user: UserDB):
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user.dict()})
    if result:
        return user.dict()

# @users_router.delete('/', status_code=HTTP_200_OK)
# async def delete_user(user_id):
#     await db.users.delete_one({'_id': ObjectId(user_id)})

# @users_router.post('/', status_code=HTTP_201_CREATED, response_model=UserResponse)
# async def create_user(login: str, name: str, password: str):
#     # TODO верификация что пользователь унеикальынй
#     # TODO хэширование пароля
#     user = UserDB(name=name, login=login, password=password)
#     result = await db.users.insert_one(user.dict())
#     if result:
#         return user