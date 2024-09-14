from aiokafka import AIOKafkaConsumer
import json

from app.deps import get_session


async def consume_notification(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="notification-consumer-group",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW ADD STOCK CONSUMER MESSAGE")
            print(f"Received message on topic {message.topic}")
            # print(f"Message value: {message.value}")
            # msg = json.loads(message.value.decode())
            return json.loads(message.value.decode()) 
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()

