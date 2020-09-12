import logging
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from auth.auth_utils import get_current_active_user
from database.mongodb import db
from database.mongodb_validators import fix_id, validate_object_id
from history_loans.model import HistoryLoansDB, HistoryLoansCreate, HistoryLoansChange, HistoryLoanType
from loans.loans_utils import _get_loan
from users.model import UserResponse

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
async def get_history_loan_row_by_id(history_loan_row_id: str,
                                     current_user: UserResponse = Depends(get_current_active_user)):
    row = await _get_history_loan_row_id(history_loan_row_id)
    return row


@history_loans_router.get("/", status_code=HTTP_200_OK)
async def get_all_history_loans_by_loans_id(loans_id: str, limit: int = 10, skip: int = 0,
                                            current_user: UserResponse = Depends(get_current_active_user)):
    history_loans_cursor = db.history_loans.find(
        {
            "loans_id": ObjectId(loans_id)
        }
    ).skip(skip).limit(limit)
    history_loans = await history_loans_cursor.to_list(length=limit)
    return list(map(fix_id, history_loans))


@history_loans_router.put("/{history_loan_row_id}", response_model=HistoryLoansDB)
async def update_client_by_id(history_loan_row_id: str, history_loan_row: HistoryLoansChange,
                              current_user: UserResponse = Depends(get_current_active_user)):
    # # valid
    history_loan_row.amount = float(history_loan_row.amount)
    if history_loan_row.amount < 0:
        raise HTTPException(status_code=400, detail="amount must be non-negative ")

    try:
        history_loan_row.type = HistoryLoanType(history_loan_row.type)
    except:
        raise HTTPException(status_code=400,
                            detail="Invalid type name " + history_loan_row.type + ". Valid status: DEPT, PROCENT")
    if not isinstance(history_loan_row.date, datetime):
        raise HTTPException(status_code=400, detail="Invalid type datetime")
    history_loan_roww = await _get_history_loan_row_id(history_loan_row_id)
    loans_id = history_loan_roww["loans_id"]
    loan = await _get_loan(loans_id)
    loan_date = loan['issued_at']
    if history_loan_row.date.isocalendar() < loan_date.isocalendar():
        raise HTTPException(status_code=400, detail="Date pay must be older then date issued")
    #############################
    result = await db.history_loans.update_one({"_id": ObjectId(history_loan_row_id)}, {"$set": {
        "amount": history_loan_row.amount,
        "date": history_loan_row.date,
        "type": history_loan_row.type
    }})
    if result:
        row = await db.history_loans.find_one({"_id": ObjectId(history_loan_row_id)})
        return fix_id(row)
    else:
        raise HTTPException(status_code=500, detail="Payment hasn't been changed")


@history_loans_router.delete("/{history_loan_row_id}", status_code=HTTP_200_OK)
async def delete_history_loan_row_by_id(history_loan_row_id,
                                        current_user: UserResponse = Depends(get_current_active_user)):
    await db.history_loans.delete_one({"_id": ObjectId(history_loan_row_id)})


@history_loans_router.post('/', status_code=HTTP_201_CREATED, response_model=HistoryLoansDB)
async def create_history_loan_row(history_loan_row: HistoryLoansCreate,
                                  current_user: UserResponse = Depends(get_current_active_user)):
    # valid
    history_loan_row.amount = float(history_loan_row.amount)
    if history_loan_row.amount < 0:
        raise HTTPException(status_code=400, detail="amount must be non-negative ")

    try:
        history_loan_row.type = HistoryLoanType(history_loan_row.type)
    except:
        raise HTTPException(status_code=400,
                            detail="Invalid type name " + history_loan_row.type + ". Valid status: DEPT, PROCENT")
    if not isinstance(history_loan_row.date, datetime):
        raise HTTPException(status_code=400, detail="Invalid type datetime")
    loan = await _get_loan(history_loan_row.loans_id)
    loan_date = loan['issued_at']
    if history_loan_row.date.isocalendar() < loan_date.isocalendar():
        raise HTTPException(status_code=400, detail="Date pay must be older then date issued")
    ######################
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



