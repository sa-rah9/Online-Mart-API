from sqlmodel import SQLModel, Field, Relationship
import random

# Inventory Microservice Models
class Payment(SQLModel, table=True):
    receipt_id: int = Field(default_factory=lambda: random.randint(1, 1000000), primary_key=True)
    order_id: int
    username: str
    email: str
    date: str
    total: float
    product_id: int
    payment_status: str = Field(default="unpaid")



class PaymentUpdate(SQLModel):
    payment_status: str | None = None
