import logging

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_200_OK, HTTP_201_CREATED
from database.mongodb import db
from database.mongodb_validators import fix_id, validate_object_id
from history_loans.model import HistoryLoansDB, HistoryLoansCreate

history_loans_router = APIRouter()


# Get User Function.
async def _get_history_loan_row_id(id: str):
    _id = validate_object_id(id)
    row = await db.history_loans.find_one({"_id": _id})
    if row:
        return fix_id(row)
    else:
        raise HTTPException(status_code=404, detail="row not found")


@history_loans_router.get("/{history_loan_row_id}", status_code=HTTP_200_OK)
async def get_history_loan_row_by_id(history_loan_row_id: str):
    row = await _get_history_loan_row_id(history_loan_row_id)
    return row


@history_loans_router.get("/", status_code=HTTP_200_OK)
async def get_all_history_loans_by_loans_id(loans_id: str, limit: int = 10, skip: int = 0):
    history_loans_cursor = db.history_loans.find_one(
        {
            "loans_id": ObjectId(loans_id)
        }
    ).skip(skip).limit(limit)
    history_loans = await history_loans_cursor.to_list(length=limit)
    return list(map(fix_id, history_loans))

#TODO валидация данных
@history_loans_router.put("/{history_loan_row_id}", response_model=HistoryLoansDB)
async def update_client_by_id(history_loan_row_id: str, history_loan_row: HistoryLoansDB):
    result = await db.history_loans.update_one({"_id": ObjectId(history_loan_row_id)}, {"$set": history_loan_row_id})
    if result:
        return history_loan_row.dict()


@history_loans_router.delete('/', status_code=HTTP_200_OK)
async def delete_history_loan_row_by_id(history_loan_row_id):
    await db.history_loans.delete_one({'_id': ObjectId(history_loan_row_id)})


class HistoryLoanSCreate(object):
    pass

#TODO валидация данных
@history_loans_router.post('/', status_code=HTTP_201_CREATED, response_model=HistoryLoansDB)
async def create_history_loan_row(history_loan_row: HistoryLoansCreate):
    result = await db.history_loans.insert_one(
        {
            "amount": history_loan_row.amount,
            "date": history_loan_row.date,
            "type": history_loan_row.type,
            "loans_id": ObjectId(history_loan_row.loans_id)
        }
    )
    if result:
        row = await db.history_loans.find_one({"_id": result.inserted_id})
        return fix_id(row)
    else:
        raise HTTPException(status_code=500, detail="Payment hasn't been created")
