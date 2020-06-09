import datetime
import logging

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from auth.auth_utils import get_current_active_user
from database.mongodb import db
from database.mongodb_validators import fix_id, validate_object_id
from loans.model import LoansDB, LoanStatus,LoansCreate
from users.model import UserResponse

loans_router = APIRouter()


# Get loans Function.
async def _get_loan(id: str):
    _id = validate_object_id(id)
    loan = await db.loans.find_one({"_id": _id})
    if loan:
        return fix_id(loan)
    else:
        raise HTTPException(status_code=404, detail="Loan not found")


async def _update_loan_status():
    db.loans.update_many({
        "expiration_at": {"$lt": datetime.datetime.now()},
        "status": {"$ne": "ARCHIVED"}
    },
        {"$set": {"status": LoanStatus.OVERDUE.name}}
    )


@loans_router.get("/", status_code=HTTP_200_OK)
async def get_loans_by_status(status: LoanStatus, limit: int = 10, skip: int = 0,
                              current_user: UserResponse = Depends(get_current_active_user)):
    await _update_loan_status()
    loans_cursor = db.loans.find({
        "status": status.name,
        "users_id": ObjectId(current_user.id)
    }).skip(skip).limit(limit)
    loans = await loans_cursor.to_list(length=limit)
    return list(map(fix_id, loans))


@loans_router.get("/{loan_id}", status_code=HTTP_200_OK)
async def get_loan_by_id(loan_id: str):
    loan = await _get_loan(loan_id)
    return loan


# TODO валидация данных
@loans_router.post('/', status_code=HTTP_201_CREATED, response_model=LoansDB)
async def create_loan(loan: LoansCreate, current_user: UserResponse = Depends(get_current_active_user)):
    result = await db.loans.insert_one(
        {
            "amount": loan.amount,
            "rate": loan.rate,
            "increased_rate": loan.increased_rate,
            "goal": loan.goal,
            "clients_id": loan.clients_id,
            "users_id": ObjectId(current_user.id),
            "created_at": loan.created_at,
            "issued_at": loan.issued_at,
            "expiration_at": loan.expiration_at,
            "status": loan.status
        }
    )
    if result:
        loan = await db.loans.find_one({"_id": result.inserted_id})
        return fix_id(loan)
    else:
        raise HTTPException(status_code=500, detail="Loan hasn't been created")


# TODO надо валидировать данные
@loans_router.put("/{loan_id}", response_model=LoansDB)
async def update_loan_by_id(loan_id: str, loan: LoansDB):
    result = await db.loans.update_one({"_id": ObjectId(loan_id)}, {"$set": loan.dict()})
    if result:
        return loan.dict()


@loans_router.get("/", response_model=LoansDB)
async def find_loan_by_name_client(name: str, limit: int = 10, skip: int = 0,
                                   current_user: UserResponse = Depends(get_current_active_user)):
    loans_cursor = db.loans.find({
        "name": name,
        "user_id": ObjectId(current_user.id)
    }).skip(skip).limit(limit)
    loans = await loans_cursor.to_list(length=limit)
    return list(map(fix_id, loans))