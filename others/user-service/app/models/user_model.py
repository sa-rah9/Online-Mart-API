from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str


class UserUpdate(SQLModel):
    name: str | None = None
    email: float | None = None
    password: str | None = None

    

    


