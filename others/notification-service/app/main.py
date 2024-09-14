# main.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
from app.deps import get_session, get_kafka_producer
from app.consumers.notification_consumer import consume_notification


# def create_db_and_tables() -> None:
#     SQLModel.metadata.create_all(engine)


def send_email(notification_info):
    # Set up the email server and login details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "kicsicrl@gmail.com"
    smtp_password = "379035"
    
    # Email content
    subject = "Thanks for your order!"
    sender_email = "kicsicrl@gmail.com"
    receiver_email = "kamran.it009@gmail.com" # notification_info.get("email")""
    
    # Create the email content
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    
    body = f"""
    Hello,

    Here are the product details:
    Product ID: {notification_info.get('product_id')}
    Price: {notification_info.get('price')}
    Username: {notification_info.get('username')}

    Regards,
    Zia-Mart
    """
    message.attach(MIMEText(body, "plain"))
    
    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")



# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating table...")

    topic = "msg-events"
    topic2 = "order-events"
    bootstrap_server = 'broker:19092'

    try:

        login_msg, order_info = await asyncio.gather(
            consume_notification(topic, bootstrap_server),
            consume_notification(topic2, bootstrap_server),
            return_exceptions=True
        )
        

    except asyncio.CancelledError:
        print("Tasks were cancelled")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    try:
        login_msg, order_info = await asyncio.gather(
            consume_notification(topic, bootstrap_server),
            consume_notification(topic2, bootstrap_server),
            return_exceptions=True
        )
        
        if isinstance(login_msg, dict) and isinstance(order_info, dict):
            notification_info = {**login_msg, **order_info}
            print('Notification_info:', notification_info)
            print('Sending email...')
            # send_email(notification_info)
        else:
            print('Error retrieving notification information')
        
    except asyncio.CancelledError:
        print("Tasks were cancelled")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    yield


app = FastAPI(
    lifespan=lifespan,
    title="Notfication Service",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "Notification Service"}

