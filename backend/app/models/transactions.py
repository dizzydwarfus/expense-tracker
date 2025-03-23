# backend/app/models/transactions.py

from pydantic import BaseModel, Field, field_validator, BeforeValidator
from typing import Annotated, Optional
from datetime import date


PyObjectId = Annotated[str, BeforeValidator(str)]


class TransactionAmount(BaseModel):
    amount: float
    currency: str


class DebtorAccount(BaseModel):
    iban: str


class CreditorAccount(BaseModel):
    iban: str


class GoCardlessTransaction(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    transactionId: Optional[str] = None
    endToEndId: Optional[str] = None
    bookingDate: Optional[date] = None  # ISODate or None if pending
    transactionAmount: TransactionAmount  # mandatory
    debtorName: Optional[str] = None
    debtorAccount: Optional[DebtorAccount] = None
    creditorName: Optional[str] = None
    creditorAccount: Optional[CreditorAccount] = None
    remittanceInformationUnstructured: Optional[str] = None
    proprietaryBankTransactionCode: Optional[str] = None
    internalTransactionId: Optional[str] = None
    transactionType: Optional[str] = Field(
        ..., pattern="^(expense|income)$"
    )  # Transaction type must be 'expense' or 'income'
    category: Optional[str]
    sub_category: Optional[str]
    username: str

    # If you want to ensure bookingDate is not in future:
    @field_validator("bookingDate")
    def check_booking_date(cls, v):
        if v and v > date.today():
            raise ValueError("bookingDate cannot be in the future")
        return v
