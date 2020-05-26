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
    if obj.get("_id", False):
        # change ObjectID to string
        obj["_id"] = str(obj.get("_id"))
        return obj
    else:
        raise ValueError(
            "No `_id` found! Unable to fix object ID: {obj}"
        )
