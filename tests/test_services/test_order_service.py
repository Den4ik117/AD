from __future__ import annotations

import pytest

from app.repositories import (
    AddressRepository,
    OrderRepository,
    ProductRepository,
    UserRepository,
)
from app.schemas import (
    OrderAddressPayload,
    OrderCreate,
    OrderItemPayload,
    OrderUserPayload,
)
from app.services import OrderService

pytestmark = pytest.mark.asyncio


def build_order_service(async_session) -> OrderService:
    return OrderService(
        OrderRepository(async_session),
        ProductRepository(async_session),
        UserRepository(async_session),
        AddressRepository(async_session),
    )


async def test_order_service_creates_orders_and_updates_status(async_session):
    order_service = build_order_service(async_session)
    product_repo = ProductRepository(async_session)
    mouse = await product_repo.create(
        name="Test Mouse", description="For service tests", price=25.0, stock_quantity=5
    )

    order = await order_service.create_order(
        OrderCreate(
            user=OrderUserPayload(
                username="order_user_service",
                email="order_user_service@example.com",
                description="Service order",
            ),
            address=OrderAddressPayload(
                street="Service st. 1",
                city="Москва",
                state="Московская область",
                zip_code="101000",
                country="Россия",
                is_primary=True,
            ),
            items=[
                OrderItemPayload(product_id=mouse.id, quantity=2),
            ],
            status="pending",
        )
    )
    assert order.total_price == pytest.approx(mouse.price * 2)
    assert order.status == "pending"

    updated = await order_service.update_status(order.id, "completed")
    assert updated.status == "completed"


async def test_order_service_rejects_out_of_stock(async_session):
    order_service = build_order_service(async_session)
    product_repo = ProductRepository(async_session)
    keyboard = await product_repo.create(
        name="Zero stock keyboard",
        description="",
        price=80.0,
        stock_quantity=0,
    )

    with pytest.raises(ValueError):
        await order_service.create_order(
            OrderCreate(
                user=OrderUserPayload(
                    username="stock_user",
                    email="stock_user@example.com",
                    description=None,
                ),
                address=OrderAddressPayload(
                    street="Main street 10",
                    city="Санкт-Петербург",
                    state="Ленинградская область",
                    zip_code="190000",
                    country="Россия",
                    is_primary=False,
                ),
                items=[
                    OrderItemPayload(product_id=keyboard.id, quantity=1),
                ],
                status="pending",
            )
        )
