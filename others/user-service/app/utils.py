from jose import jwt, JWTError
from datetime import datetime, timedelta

ALGORITHM = "HS256"
SECRET_KEY = "A Secure Secret Key"

def create_access_token(subject: str , expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(access_token: str):
    decoded_jwt = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    return decoded_jwt

async def send_user_authenticated_message(user_id: str):
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        message = json.dumps({"user_id": user_id}).encode("utf-8")
        await producer.send_and_wait("UserAuthenticated", message)
    finally:
        await producer.stop()