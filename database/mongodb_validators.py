from bson.objectid import ObjectId
from fastapi import HTTPException
import logging

from users.model import UserDB


def validate_object_id(id: str):
    try:
        _id = ObjectId(id)
    except Exception:
        logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400, detail="Invalid Object ID")
    return _id


def fix_id(obj):
    for attr in obj:
        if isinstance(obj[attr], ObjectId):
            obj[attr] = str(obj[attr])
    if obj.get("_id", False):
        obj["id"] = obj.pop("_id")
    return obj
