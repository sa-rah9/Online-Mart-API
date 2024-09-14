from sqlmodel import SQLModel, Field, Relationship

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: str
    product_id: int # Should be list
    total: float
    status: str
    # product: Product = Relationship(back_populates="order")


class OrderUpdate(SQLModel):
    date: str | None = None
    total: float | None = None
    status: str | None = None

    

    


