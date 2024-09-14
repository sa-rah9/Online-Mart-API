from aiokafka import AIOKafkaConsumer
import json

from app.deps import get_session
from app.crud.payment_crud import add_new_payment
from app.models.payment_model import Payment

async def consume_payment(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="payment-consumer-group",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("Payment MESSAGE")
            print(f"Received message on topic {message.topic}")
            # print(f"Message value: {message.value}")
            # msg = json.loads(message.value.decode())
            return json.loads(message.value.decode()) 

        

            # inventory_data = json.loads(message.value.decode())
            # print("TYPE", (type(inventory_data)))
            # print(f"Inventory Data {inventory_data}")

            # with next(get_session()) as session:
            #     print("SAVING DATA TO DATABSE")
            #     # inventory_item_data: InventoryItem
            #     db_insert_product = add_new_inventory_item(
            #         inventory_item_data=InventoryItem(**inventory_data), 
            #         session=session)
                
            #     print("DB_INSERT_STOCK", db_insert_product)

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()

