import logging
from datetime import datetime

from bson import ObjectId

from database.mongodb import db
from database.mongodb_validators import fix_id
from loans.model import LoansDB
from users.model import UserResponse

DAY_IN_YEAR = 365


def find_procent(dept: int, procent_year: int, date_count: int):
    if date_count <= DAY_IN_YEAR:
        return (dept * procent_year * date_count) / (DAY_IN_YEAR * 100)
    else:
        # проценты в деньгах которые я ищу
        procent_dept = 0
        while date_count - DAY_IN_YEAR > DAY_IN_YEAR:
            date_count -= DAY_IN_YEAR
            procent_dept += (dept * procent_year * date_count) / (DAY_IN_YEAR * 100)
        procent_dept += (dept * procent_year * date_count) / (DAY_IN_YEAR * 100)
        return procent_dept


async def _get_dept_obj(loan_id):
    dept_history_loans_cursor = db.history_loans.find({
        "loans_id": ObjectId(loan_id),
        "type": "DEPT"
    }).sort("date")
    dept_history_loans = await dept_history_loans_cursor.to_list(length=100)
    return list(map(fix_id, dept_history_loans))


async def _get_procent_obj(loan_id):
    procent_history_loans_cursor = db.history_loans.find({
        "loans_id": ObjectId(loan_id),
        "type": "PROCENT"
    }).sort("date")
    procent_history_loans = await procent_history_loans_cursor.to_list(length=100)
    return list(map(fix_id, procent_history_loans))


def _get_dept_and_procent_include_last_date(loan, dept_obj):
    init_dept = loan["amount"]
    issued_at_date = loan["issued_at"]
    expiration_at = loan["expiration_at"]
    last_date = dept_obj[0]["date"]
    # деньги которые заплатит клиент за пользование моими деньгами
    my_income = 0
    if expiration_at >= dept_obj[0]["date"]:
        rate = loan["rate"]
    else:
        rate = loan["increased_rate"]
    # init step
    delta = (dept_obj[0]["date"] - issued_at_date).days
    # проценты за пользование деньгами
    find_procent_for_gap = find_procent(init_dept, rate, delta)
    my_income += find_procent_for_gap
    # сумма к возврату
    dept = init_dept - dept_obj[0]["amount"]
    if len(dept_obj)>1:
        for x in range(1, len(dept_obj)):
            if last_date < dept_obj[x]["date"]:
                last_date = dept_obj[x]["date"]
            delta = (dept_obj[x]["date"] - dept_obj[x - 1]["date"]).days
            if dept > 0:
                if expiration_at >= dept_obj[x]["date"]:
                    rate = loan["rate"]
                else:
                    rate = loan["increased_rate"]
                find_procent_for_gap = find_procent(dept, rate, delta)
                my_income += find_procent_for_gap
            dept -= dept_obj[x]["amount"]
    return {
        "dept": dept,
        "my_income": my_income,
        "last_date": last_date
    }


def _get_my_incom(procent_obj):
    my_income = 0
    for x in range(0, len(procent_obj)):
        my_income += procent_obj[x]["amount"]
    return my_income


def _get_my_income_now(dept_and_procent_before_last_date, loan, my_income):
    if loan["expiration_at"] >= datetime.now():
        rate = loan["rate"]
    else:
        rate = loan["increased_rate"]
    delta = (datetime.now() - dept_and_procent_before_last_date["last_date"]).days
    my_income_between_last_day_and_now = find_procent(dept_and_procent_before_last_date["dept"], rate, delta)
    my_income_now = dept_and_procent_before_last_date["my_income"] - my_income + my_income_between_last_day_and_now
    return my_income_now


async def _get_income_income_now_amount_of_dept(loan):
    loan = loan
    dept_obj = await _get_dept_obj(loan["id"])
    procent_obj = await _get_procent_obj(loan["id"])

    # получаю обьект в котором содержится задолженность по долгу и долг который должен отдать клиент
    # за пользование деньгами
    dept_and_procent_before_last_date = _get_dept_and_procent_include_last_date(loan, dept_obj)
    my_income = _get_my_incom(procent_obj)
    my_incom_now = _get_my_income_now(dept_and_procent_before_last_date, loan, my_income)
    if dept_and_procent_before_last_date["dept"] <= 0 and my_incom_now <= 0:
        await db.loans.update_one({"_id": ObjectId(loan["id"])},
                                  {"$set": {
                                      "status": "ARCHIVED"
                                  }})
    return {
        "my_income_now": my_incom_now,
        "my_income": my_income,
        "amount_of_dept": dept_and_procent_before_last_date["dept"]
    }


async def _get_all_my_income(current_user: UserResponse):
    loans_cursor = db.loans.find({
        "users_id": ObjectId(current_user.id)
    })
    loans = await loans_cursor.to_list(length=100)
    l = list(map(fix_id, loans))
    all_my_income = 0
    all_my_income_now = 0
    for loan in l:
        tmp = await _get_income_income_now_amount_of_dept(loan)
        if tmp["my_income"] > 0:
            all_my_income += tmp["my_income"]
        if tmp["my_income_now"] > 0:
            all_my_income_now += tmp["my_income_now"]
    loans_cursor = db.loans.find({
        "users_id": ObjectId(current_user.id),
        "status": "OVERDUE"
    })
    loans = await loans_cursor.to_list(length=100)
    l = list(map(fix_id, loans))
    all_overdue_amount = 0
    for loan in l:
        tmp = await _get_income_income_now_amount_of_dept(loan)
        all_overdue_amount += tmp["dept"]
    return {
        "all_my_income": all_my_income,
        "all_my_income_now": all_my_income_now,
        "all_overdue_amount": all_overdue_amount
    }
