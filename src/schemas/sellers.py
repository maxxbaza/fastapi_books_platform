from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .books import ReturnedSellerBook

__all__ = [
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedAllSellers",
    "ReturnedSellerWithBooks",
    "UpdateSeller",
]


class IncomingSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr
    password: str


class UpdateSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


class ReturnedSeller(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr = Field(validation_alias="e_mail")

    model_config = ConfigDict(from_attributes=True)

class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedSellerBook]