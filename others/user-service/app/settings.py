from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)

KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str, default = "user-topic")

KAFKA_USER_MSG = config("KAFKA_USER_MSG", cast=str, default = "user-msg")

BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)

KAFKA_CONSUMER_GROUP_ID_FOR_USER = config("KAFKA_CONSUMER_GROUP_ID_FOR_USER", cast=str, default="default_group_id")

TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

OPENAI_API_KEY = config("OPENAI_API_KEY", cast=Secret)