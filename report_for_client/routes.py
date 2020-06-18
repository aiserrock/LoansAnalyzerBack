import logging
from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from clients.routes import _get_client
from loans.loans_utils import _get_loan
from report_for_client.report_utils import _get_all_history_loans_by_loans_id
from users.routes import _get_user

report_for_client_router = APIRouter()


@report_for_client_router.get("/{loan_id}", status_code=HTTP_200_OK)
async def get_data_for_report(loan_id: str):
    loan = await _get_loan(loan_id)
    client = await _get_client(loan["clients_id"])
    history_loan = await _get_all_history_loans_by_loans_id(loan_id)
    user = await _get_user(loan["users_id"])
    report = {
        "loan_id": loan["id"],
        "status": loan["status"],
        "amount": loan["amount"],
        "rate": loan["rate"],
        "issued_at": loan["issued_at"],
        "expiration_at": loan["expiration_at"],
        "increased_rate": loan["increased_rate"],
        "user_name": user["name"],
        "client_name": client["name"],
        "history_loan": history_loan
    }
    return report
