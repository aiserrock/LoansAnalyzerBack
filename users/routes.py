from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from starlette.status import HTTP_200_OK

from auth.auth_utils import get_current_active_user
from database.mongodb import db
from database.mongodb_validators import fix_id, validate_object_id
from users.model import UserResponse, UserDB, UserChange

users_router = APIRouter()


# Get User Function.
async def _get_user(id: str):
    _id = validate_object_id(id)
    user = await db.users.find_one({"_id": _id})
    if user:
        return fix_id(user)
    else:
        raise HTTPException(status_code=404, detail="User not found")


@users_router.get("/{user_id}", status_code=HTTP_200_OK)
async def get_user_by_id(user_id: str, current_user: UserResponse = Depends(get_current_active_user)):
    user = await _get_user(user_id)
    if user and user["id"] == current_user.id:
        return user
    else:
        raise HTTPException(status_code=401, detail="Access deny")


@users_router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(user: UserChange, current_user: UserResponse = Depends(get_current_active_user)):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    result = await db.users.update_one({"_id": ObjectId(current_user.id)},
                                       {"$set": {
                                           "name": user.name,
                                           "password": pwd_context.hash(user.password)
                                       }})
    if result:
        user = await db.users.find_one({"_id": ObjectId(current_user.id)})
        return fix_id(user)
    else:
        raise HTTPException(status_code=500, detail="User hasn't been changed")

# @users_router.get("/", status_code=HTTP_200_OK)
# async def get_all_users(limit: int = 10, skip: int = 0):
#     users_cursor = db.users.find().skip(skip).limit(limit)
#     users = await users_cursor.to_list(length=limit)
#     return list(map(fix_id, users))
