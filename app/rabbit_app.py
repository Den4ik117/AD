from __future__ import annotations

import asyncio
import logging
import os

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from app.db import async_session_factory
from app.repositories import (
    AddressRepository,
    OrderRepository,
    ProductRepository,
    UserRepository,
)
from app.schemas import OrderMessage, ProductMessage
from app.services import OrderService, ProductService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rabbit")

RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/local")

broker = RabbitBroker(RABBIT_URL)
app = FastStream(broker)


@broker.subscriber("product", parser="json")
async def subscribe_product(message: ProductMessage) -> None:
    async with async_session_factory() as session:
        service = ProductService(ProductRepository(session))
        try:
            product = await service.apply_message(message)
        except Exception:
            logger.exception(
                "Failed to handle product message: %s", message.model_dump()
            )
            raise
        logger.info(
            "Processed product message action=%s id=%s",
            message.action,
            product.id,
        )


@broker.subscriber("order", parser="json")
async def subscribe_order(message: OrderMessage) -> None:
    async with async_session_factory() as session:
        service = OrderService(
            OrderRepository(session),
            ProductRepository(session),
            UserRepository(session),
            AddressRepository(session),
        )
        try:
            order = await service.apply_message(message)
        except Exception:
            logger.exception("Failed to handle order message: %s", message.model_dump())
            raise
        logger.info(
            "Processed order message action=%s id=%s",
            message.action,
            getattr(order, "id", None),
        )


async def main() -> None:
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
