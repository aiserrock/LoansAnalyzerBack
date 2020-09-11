from datetime import datetime
import logging
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from auth.auth_utils import get_current_active_user
from database.mongodb import db
from database.mongodb_validators import fix_id
from loans.loans_utils import _update_loans_status, _search_by_name_or_phone, _get_loan_by_status, _get_loan
from loans.logic_calculate_money import _get_income_income_now_amount_of_dept, _get_all_my_income
from loans.model import LoansDB, LoanStatus, LoansCreate, LoansChange
from users.model import UserResponse

loans_router = APIRouter()


@loans_router.get("/", status_code=HTTP_200_OK)
async def get_loans(status: LoanStatus = None, search: str = None, statistics : bool = None,limit: int = 10, skip: int = 0,
                    current_user: UserResponse = Depends(get_current_active_user)):
    """
        status - статус займа (активный, просроченный, архивный)
        search - то что пишем в поле find (номер телефона или имя клиента)
        in: status, search, limit, skip
        out: если serach не пусто, то вернет выборку по search
             иначе если статус не пусто, то вернет выборку по статус
             иначе вернет все займы пользователя

        statistics -  если этот параметр true, то метод get_loans возвращает статистику, а именно 3 параметра 1. all_my_income, 2. all_my_income_now 3. all_overdue_amount

    """

    await _update_loans_status()
    if statistics:
        return await _get_all_my_income(current_user)
    if search is not None:
        return await _search_by_name_or_phone(current_user, search, limit, skip, status)
    else:
        return await _get_loan_by_status(current_user, status, limit, skip)


@loans_router.get("/{loan_id}", status_code=HTTP_200_OK)
async def get_loan_by_id(loan_id: str, current_user: UserResponse = Depends(get_current_active_user)):
    loan = await _get_loan(loan_id)
    income_income_now_amount_of_dept = await _get_income_income_now_amount_of_dept(loan)
    if loan and current_user.id == loan["users_id"]:
        return {
            "id": loan["id"],
            "amount": loan["amount"],
            "rate": loan["rate"],
            "increased_rate": loan["increased_rate"],
            "goal": loan["goal"],
            "clients_id": loan["clients_id"],
            "users_id": loan["users_id"],
            "created_at": loan["created_at"],
            "issued_at": loan["issued_at"],
            "expiration_at": loan["expiration_at"],
            "status": loan["status"],
            "my_income_now": income_income_now_amount_of_dept["my_income_now"],
            "my_income": income_income_now_amount_of_dept["my_income"],
            "amount_of_dept": income_income_now_amount_of_dept["amount_of_dept"]
        }
    else:
        raise HTTPException(status_code=401, detail="Access deny")


# TODO валидация данных
@loans_router.post('/', status_code=HTTP_201_CREATED, response_model=LoansDB)
async def create_loan(loan: LoansCreate, current_user: UserResponse = Depends(get_current_active_user)):
    result = await db.loans.insert_one(
        {
            "amount": loan.amount,
            "rate": loan.rate,
            "increased_rate": loan.increased_rate,
            "goal": loan.goal,
            "clients_id": ObjectId(loan.clients_id),
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
async def update_loan_by_id(loan_id: str, loan: LoansChange,
                            current_user: UserResponse = Depends(get_current_active_user)):
    # validation

    loan.rate = float(loan.rate)
    loan.increased_rate = float(loan.increased_rate)
    try:
        loan.status = LoanStatus(loan.status)
    except:
        raise HTTPException(status_code=400, detail="Invalid status name " + loan.status + ". Valid status: ACTIVE, OVERDUE, ARCHIVED")
    if not isinstance(loan.expiration_at, datetime) \
            or not isinstance(loan.created_at, datetime) \
            or not isinstance(loan.issued_at, datetime):
        raise HTTPException(status_code=400, detail="Invalid type datetime")
    if loan.amount < 0 \
            or loan.increased_rate < 0 \
            or loan.rate < 0:
        raise HTTPException(status_code=400, detail="amount or rate or increased_rate must be non-negative ")

    result = await db.loans.update_one({"$and": [{"_id": ObjectId(loan_id)}, {"users_id": ObjectId(current_user.id)}]},
                                       {"$set": {
                                           "amount": loan.amount,
                                           "rate": loan.rate,
                                           "increased_rate": loan.increased_rate,
                                           "goal": loan.goal,
                                           "created_at": loan.created_at,
                                           "issued_at": loan.issued_at,## дата выдачи займа
                                           "expiration_at": loan.expiration_at,## срок выплаты по договору
                                           "status": loan.status
                                       }})
    if result:
        loan = await db.loans.find_one({"_id": ObjectId(loan_id)})
        return fix_id(loan)
    else:
        raise HTTPException(status_code=500, detail="Loan hasn't been changed")
