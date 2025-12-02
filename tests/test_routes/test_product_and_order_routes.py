from __future__ import annotations

import asyncio
from uuid import UUID

import pytest
from litestar.status_codes import HTTP_200_OK

from app.repositories import (
    AddressRepository,
    OrderRepository,
    ProductRepository,
    UserRepository,
)
from app.schemas import UserCreate


async def _seed_data(async_session_factory) -> tuple[UUID, UUID]:
    async with async_session_factory() as session:
        product_repo = ProductRepository(session)
        user_repo = UserRepository(session)
        address_repo = AddressRepository(session)
        order_repo = OrderRepository(session)

        product = await product_repo.create(
            name="API-visible product",
            description="Created for route tests",
            price=10.0,
            stock_quantity=3,
        )
        user = await user_repo.create(
            UserCreate(
                username="route_user",
                email="route_user@example.com",
                description=None,
            )
        )
        address = await address_repo.create(
            user_id=user.id,
            street="Тестовая, 5",
            city="Москва",
            state="Московская область",
            zip_code="101000",
            country="Россия",
            is_primary=True,
        )
        order = await order_repo.create(
            user_id=user.id,
            address_id=address.id,
            status="pending",
            items=[
                {"product_id": product.id, "quantity": 1, "unit_price": product.price}
            ],
        )
        return product.id, order.id


@pytest.fixture
def seeded_product_and_order(async_session_factory) -> tuple[UUID, UUID]:
    return asyncio.run(_seed_data(async_session_factory))


def test_product_and_order_endpoints(seeded_product_and_order, api_client):
    product_id, order_id = seeded_product_and_order

    response = api_client.get("/products")
    assert response.status_code == HTTP_200_OK
    products = response.json()
    assert products["total"] == 1
    assert products["items"][0]["id"] == str(product_id)

    response = api_client.get(f"/products/{product_id}")
    assert response.status_code == HTTP_200_OK
    assert response.json()["id"] == str(product_id)

    response = api_client.get(f"/orders/{order_id}")
    assert response.status_code == HTTP_200_OK
    assert response.json()["id"] == str(order_id)
