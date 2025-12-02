from __future__ import annotations

import pytest

from app.repositories import ProductRepository
from app.schemas import ProductCreate, ProductUpdate
from app.services import ProductService

pytestmark = pytest.mark.asyncio


async def test_product_service_handles_create_and_update(async_session):
    repo = ProductRepository(async_session)
    service = ProductService(repo)

    created = await service.create_product(
        ProductCreate(
            name="Service Product",
            description="Created through ProductService",
            price=100.0,
            stock_quantity=5,
        )
    )
    assert created.stock_quantity == 5

    updated = await service.update_product(
        created.id, ProductUpdate(price=125.5, stock_quantity=10)
    )
    assert updated.price == 125.5
    assert updated.stock_quantity == 10


async def test_product_service_marks_out_of_stock(async_session):
    repo = ProductRepository(async_session)
    service = ProductService(repo)
    created = await service.create_product(
        ProductCreate(
            name="Out of stock soon",
            description="",
            price=50.0,
            stock_quantity=2,
        )
    )

    depleted = await service.mark_out_of_stock(created.id)
    assert depleted.stock_quantity == 0
