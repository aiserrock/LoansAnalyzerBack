from pydantic import BaseModel
from datetime import datetime


class reportAnswer(BaseModel):
    loan_id: str
    issued_at: datetime
    expiration_at: datetime
    client_name: str
    user_name: str
    amount: float
    rate: float
    increase_rate: float
    status: str
    #history_loan: {}
