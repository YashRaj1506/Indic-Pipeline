import asyncio
import aio_pika
import json
import time
import os
import logging

logger = logging.getLogger(__name__)

OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")

with open(os.path.join(OUTPUTS_DIR, "batches.txt"), "r") as file:
    batches = json.load(file)


async def main():
    connection = await aio_pika.connect_robust("amqp://user:password@localhost/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("audio_batches", durable=True)

        exchange = await channel.declare_exchange(
            "audio_exchange", aio_pika.ExchangeType.DIRECT, durable=True
        )

        batch_no = 1

        for batch in batches:

            batch_start = time.perf_counter()

            message_body = json.dumps(batch).encode()
            message = aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            await exchange.publish(message, routing_key="audio_batches")

            batch_end = time.perf_counter()
            batch_time = batch_end - batch_start

            print(f"Batch {batch_no}: {len(batch)} files" f"{batch_time:.6f} sec")

            batch_no += 1

        logger.info("\n All batches published successfully.")


if __name__ == "__main__":
    asyncio.run(main())
