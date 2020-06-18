from bson import ObjectId
from fastapi import Depends

from auth.auth_utils import get_current_active_user
from database.mongodb import db
from database.mongodb_validators import fix_id
from users.model import UserResponse


async def _get_all_history_loans_by_loans_id(loans_id: str, limit: int = 10, skip: int = 0,
                                            current_user: UserResponse = Depends(get_current_active_user)):
    history_loans_cursor = db.history_loans.find(
        {
            "loans_id": ObjectId(loans_id)
        }
    ).skip(skip).limit(limit)
    history_loans = await history_loans_cursor.to_list(length=limit)
    return list(map(fix_id, history_loans))