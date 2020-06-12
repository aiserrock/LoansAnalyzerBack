from enum import Enum

from pydantic import BaseModel
from datetime import datetime


class LoansDB(BaseModel):
    id: str
    amount: float
    rate: float
    increased_rate: float
    goal: str
    clients_id: str
    users_id: str
    created_at: datetime
    issued_at: datetime
    expiration_at: datetime
    status: str


class LoansChange(BaseModel):
    amount: float
    rate: float
    increased_rate: float
    goal: str
    created_at: datetime
    issued_at: datetime
    expiration_at: datetime
    status: str


class LoansCreate(BaseModel):
    amount: float
    rate: float
    increased_rate: float
    goal: str
    clients_id: str
    users_id: str
    created_at: datetime
    issued_at: datetime
    expiration_at: datetime
    status: str


class LoanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    ARCHIVED = "ARCHIVED"
