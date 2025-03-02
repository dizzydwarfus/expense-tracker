from pydantic import BaseModel, Field, validator, BeforeValidator
from typing import Dict, Annotated, Optional
from datetime import datetime


PyObjectId = Annotated[str, BeforeValidator(str)]


def verify_split(amount: float, split: Dict[str, float]) -> bool:
    total = sum(split.values())
    if total != amount:
        return False
    return True


class Transaction(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    transactionDate: datetime
    transactionType: str = Field(
        ..., pattern="^(expense|income)$"
    )  # Transaction type must be 'expense' or 'income'
    description: str
    group: str
    paidBy: str
    amount: float = Field(..., gt=0)  # Amount must be greater than 0
    currency: str
    split: Dict[str, float] = Field(
        ...,
        min_items=1,
    )  # There must be at least one item in the split
    transactionId: str
    category: str
    sub_category: str

    @validator("split")
    def check_split(cls, split, values):
        if "amount" in values and sum(split.values()) != values["amount"]:
            raise ValueError("Total of split must equal amount")
        return split

    @validator("transactionDate")
    def check_date(cls, date):
        if date > datetime.now():
            raise ValueError("Date cannot be in the future")
        return date

    @validator("transactionId")
    def check_transaction_id(cls, transaction_id, values):
        date_present = "transactionDate" in values
        paid_by_present = "paidBy" in values
        amount_present = "amount" in values
        group_present = "group" in values
        required_fields_present = (
            date_present and paid_by_present and amount_present and group_present
        )

        if required_fields_present:
            expected_transaction_id = f"{datetime.strftime(values['transactionDate'], '%Y-%m-%d').replace('-', '')}{values['paidBy']}{values['amount']:.2f}{values['group']}"
            if transaction_id != expected_transaction_id:
                raise ValueError(
                    "Transaction ID must be a combination of transactionDate, paidBy, amount and group"
                )
        return transaction_id
