# Get loans Function.
import datetime
import logging

from bson import ObjectId
from fastapi import HTTPException

from database.mongodb import db
from database.mongodb_validators import validate_object_id, fix_id
from loans.model import LoanStatus
from users.model import UserResponse


async def _get_loan(id: str, current_user: UserResponse):
    _id = validate_object_id(id)
    loan = await db.loans.find_one({"$and": [{"_id": _id}, {"users_id": ObjectId(current_user.id)}]})
    if loan:
        return fix_id(loan)
    else:
        raise HTTPException(status_code=404, detail="Loan not found")


async def _update_loans_status():
    await db.loans.update_many({
        "expiration_at": {"$lt": datetime.datetime.now()},
        "status": {"$ne": "ARCHIVED"}
    },
        {"$set": {"status": LoanStatus.OVERDUE.name}}
    )


async def _get_loan_by_status(current_user: UserResponse, status: LoanStatus = None, limit: int = 10, skip: int = 0):
    if status is None:
        loans_cursor = db.loans.find({
            "users_id": ObjectId(current_user.id)
        }).skip(skip).limit(limit)
    else:
        loans_cursor = db.loans.find({
            "status": status.name,
            "users_id": ObjectId(current_user.id)
        }).skip(skip).limit(limit)
    loans = await loans_cursor.to_list(length=limit)
    return list(map(fix_id, loans))


async def _search_by_name_or_phone(current_user: UserResponse, search: str = None, limit: int = 10, skip: int = 0):
    regex = ".*" + search + ".*"
    clients_cursor = db.clients.find({
        "$or":
            [
                {
                    "name": {"$regex": regex, "$options": "i"}
                },
                {
                    "phone": {"$regex": regex, "$options": "i"}
                }
            ],
        "user_id": ObjectId(current_user.id)
    })
    clients = await clients_cursor.to_list(length=limit)
    loans = []
    for client in clients:
        tmp_cursor = db.loans.find({
            "clients_id": ObjectId(client["_id"]),
            "users_id": ObjectId(current_user.id)
        })
        tmp = await tmp_cursor.to_list(length=limit)
        for i in tmp:
            loans.append(i)
    return list(map(fix_id, loans))
