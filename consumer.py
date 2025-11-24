import asyncio
import aio_pika
import json
from tasks import process_batch
from logging_config import setup_logger
import logging


setup_logger()

logger = logging.getLogger(__name__)

import tasks, publisher

async def main():

    connection = await aio_pika.connect_robust("amqp://user:password@rabbitmq/")
    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            "audio_exchange", aio_pika.ExchangeType.DIRECT, durable=True
        )

        queue = await channel.declare_queue("audio_batches", durable=True)

        await queue.bind(exchange, routing_key="audio_batches")

        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                batch = json.loads(message.body)
                logger.info(f"Got a batch of {len(batch['files'])} files from RabbitMQ")

                process_batch.delay(batch)
                logger.info("Sent batch to Celery for processing.")

        await queue.consume(on_message)
        logger.info(f"Listening for new messages")

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
