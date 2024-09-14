# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.payment_model import Payment, PaymentUpdate
from app.crud.payment_crud import add_new_payment, get_all_payments, get_payment_by_id, delete_payment_by_id, update_payment_by_id
from app.deps import get_session, get_kafka_producer
from app.consumers.payment_consumer import consume_payment


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating table...")
    create_db_and_tables()


    topic = "msg-events"
    topic2 = "order-events"
    bootstrap_server = 'broker:19092'

    try:

        login_msg, order_info = await asyncio.gather(
            consume_payment(topic, bootstrap_server),
            consume_payment(topic2, bootstrap_server),
            return_exceptions=True
        )
        

    except asyncio.CancelledError:
        print("Tasks were cancelled")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return
    
    # notification_info = {**login_msg, **order_info}
    # print('Notification_info:', notification_info)

    payment_info = {
        'username': login_msg['username'],
        'email': login_msg['email'],
        'order_id': order_info['id'],
        'date': order_info['date'],
        'total': order_info['total'],
        'product_id': order_info['product_id']
    }
    
    print('Payment_info:', payment_info)

    # Create a new Payment object
    print('Saving Payment...')
    with next(get_session()) as session:
        db_insert_payment = add_new_payment(
            payment_data=Payment(**payment_info), session=session)
        print("DB_INSERT_PAYMENT", db_insert_payment)
    yield



app = FastAPI(
    lifespan=lifespan,
    title="Payment Service",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "Payment Service"}

@app.post("/manage-payment/", response_model=Payment)
async def create_new_payment(payment: Payment, session: Annotated[Session, Depends(get_session)]): # , producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """ Create a new payment and send it to Kafka"""

    print(payment)

    # product_dict = {field: getattr(product, field) for field in product.dict()}
    # print(product_dict)
    # product_json = json.dumps(product_dict).encode("utf-8")
    # print("product_JSON:", product_json)
    # # Produce message
    # await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_json)
    new_payment = add_new_payment(payment, session)
    return payment


@app.get("/manage-payment/all", response_model=list[Payment])
def call_all_payments(session: Annotated[Session, Depends(get_session)]):
    """ Get all products from the database"""
    return get_all_payments(session)


@app.get("/manage-payment/{payment_id}", response_model=Payment)
def get_single_payment(payment_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Get a single product by ID"""
    try:
        return get_payment_by_id(payment_id=payment_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/manage-payment/{payment_id}", response_model=dict)
def delete_single_product(payment_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Delete a single product by ID"""
    try:
        return delete_payment_by_id(payment_id=payment_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/manage-payment/{payment_id}", response_model=Payment)
def update_payment(payment_id: int, payment: PaymentUpdate, session: Annotated[Session, Depends(get_session)]):
    """ Update a single product by ID"""
    try:
        return update_payment_by_id(payment_id=payment_id, to_update_payment_data=payment, session=session)
        print('Sending email...')
        # send_email(payment_info)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

