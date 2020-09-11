# Get loans Function.
from datetime import datetime
import datetime
import logging

from bson import ObjectId
from fastapi import HTTPException

from database.mongodb import db
from database.mongodb_validators import validate_object_id, fix_id
from history_loans.model import HistoryLoanType
from loans.logic_calculate_money import _get_income_income_now_amount_of_dept
from loans.model import LoanStatus
from users.model import UserResponse


async def _get_loan(id: str):
    _id = validate_object_id(id)
    loan = await db.loans.find_one({"_id": _id})
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


async def _get_loan_by_status(current_user: UserResponse, status: LoanStatus = None, limit: int = 10,
                              skip: int = 0):
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
    l = list(map(fix_id, loans))
    for x in l:
        x.update(await _get_income_income_now_amount_of_dept(x))
    return l


async def _search_by_name_or_phone(current_user: UserResponse, search: str = None, limit: int = 10, skip: int = 0,
                                   status=None):
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
        if status is not None:
            tmp_cursor = db.loans.find({
                "clients_id": ObjectId(client["_id"]),
                "status": status.name,
                "users_id": ObjectId(current_user.id)
            }).skip(skip).limit(limit)
        else:
            tmp_cursor = db.loans.find({
                "clients_id": ObjectId(client["_id"]),
                "users_id": ObjectId(current_user.id)
            }).skip(skip).limit(limit)
        tmp = await tmp_cursor.to_list(length=limit)
        for i in tmp:
            loans.append(i)
    l = list(map(fix_id, loans))
    for x in l:
        x.update(await _get_income_income_now_amount_of_dept(x))
    return l


def validating_for_loans(loan):
    # validation

    loan.rate = float(loan.rate)
    loan.increased_rate = float(loan.increased_rate)
    try:
        loan.status = LoanStatus(loan.status)
    except:
        raise HTTPException(status_code=400,
                            detail="Invalid status name " + loan.status + ". Valid status: ACTIVE, OVERDUE, ARCHIVED")
    if not isinstance(loan.expiration_at, datetime) \
            or not isinstance(loan.created_at, datetime) \
            or not isinstance(loan.issued_at, datetime):
        raise HTTPException(status_code=400, detail="Invalid type datetime")
    if loan.amount < 0 \
            or loan.increased_rate < 0 \
            or loan.rate < 0:
        raise HTTPException(status_code=400, detail="amount or rate or increased_rate must be non-negative ")
    if loan.expiration_at <= loan.issued_at:
        raise HTTPException(status_code=400, detail="Date issued must be early then date expiration")


def validating_for_clients(client):
    client.name = str(client.name)
    client.phone = str(client.phone)



