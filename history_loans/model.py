from enum import Enum

from pydantic import BaseModel
from datetime import datetime


class HistoryLoansDB(BaseModel):
    id: str
    amount: float
    date: datetime
    type: str
    loans_id: str

class HistoryLoansCreate(BaseModel):
    amount: float
    date: datetime
    type: str
    loans_id: str


class HistoryLoanType(str, Enum):
    PROCENT = "PROCENT"
    DEPT = "DEPT"
