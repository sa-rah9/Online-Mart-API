# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from jose import JWTError
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.user_model import User, UserUpdate
from app.crud.user_crud import add_new_user, get_all_users, get_user_by_id, delete_user_by_id, update_user_by_id, get_user_by_credentials, validate_user
from app.deps import get_session, get_kafka_producer
from app.utils import create_access_token, decode_access_token, send_user_authenticated_message
from app.consumers.user_consumer import consume_messages
from fastapi import Depends
from app.utils import decode_access_token
# from app.consumers.inventroy_consumer import consume_inventory_messages

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating ... ... ?? !!! ")

    task = asyncio.create_task(consume_messages(
        settings.KAFKA_USER_TOPIC, 'broker:19092'))
    

    create_db_and_tables()
    yield


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(
    lifespan=lifespan,
    title="User-Service",
    version="0.0.1",
)




@app.get("/")
def read_root():
    return {"Hello": "User Service"}


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)], 
session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """
    Understanding the login system
    -> Takes form_data that have username and password
    """
    user = get_user_by_credentials(form_data.username, form_data.password, session)
    print('USER:', user)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user_data = user.dict()
    user_msg = {
        "email": user_data.get("email"),
        "username": user_data.get("name")
    }
    user_json_msg = json.dumps(user_msg).encode("utf-8")
    print("USER_JSON:", user_json_msg)
    
    access_token_expires = timedelta(minutes=5)

    access_token = create_access_token(
        subject=user_data["name"], expires_delta=access_token_expires)
    # Produce message
    await producer.send_and_wait(settings.KAFKA_USER_MSG, user_json_msg)

    return {"access_token": access_token, "token_type": "bearer", "expires_in": access_token_expires.total_seconds() }


@app.post("/create-user")
async def create_new_user(user: User, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """ Create a new product and send it to Kafka"""

    user_dict = {field: getattr(user, field) for field in user.dict()}
    user_json = json.dumps(user_dict).encode("utf-8")
    print("USER_JSON:", user_json)
    # Produce message
    await producer.send_and_wait(settings.KAFKA_USER_TOPIC, user_json)
    # new_user = add_new_user(user, session)
    return {"message": "User Created Successfully"}


@app.get("/get-users", response_model=list[User])
def call_all_users(session: Annotated[Session, Depends(get_session)], token: Annotated[str, Depends(oauth2_scheme)]):
    user_token_data = decode_access_token(token)
    """ Get all users from the database"""
    print("TOKEN:", user_token_data)
    user = validate_user(user_token_data['sub'], session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return get_all_users(session)


@app.get("/get-user/{user_id}", response_model=User)
def get_single_user(user_id: int, session: Annotated[Session, Depends(get_session)], token: Annotated[str, Depends(oauth2_scheme)]):
    """ Get a single user by ID"""
    user_token_data = decode_access_token(token)
    user = validate_user(user_token_data['sub'], session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return get_user_by_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-user/{user_id}", response_model=dict)
def delete_single_user(user_id: int, session: Annotated[Session, Depends(get_session)], token: Annotated[str, Depends(oauth2_scheme)]):
    """ Delete a single user by ID"""
    user_token_data = decode_access_token(token)
    user = validate_user(user_token_data['sub'], session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return delete_user_by_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/update-user/{user_id}", response_model=User)
def update_single_user(user_id: int, user: UserUpdate, session: Annotated[Session, Depends(get_session)], token: Annotated[str, Depends(oauth2_scheme)]):
    """ Update a single product by ID"""
    user_token_data = decode_access_token(token)
    user = validate_user(user_token_data['sub'], session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return update_user_by_id(user_id=user_id, to_update_user_data=user, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))