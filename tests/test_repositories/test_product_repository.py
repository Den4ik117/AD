from __future__ import annotations

import pytest

from app.repositories import ProductNotFoundError, ProductRepository

pytestmark = pytest.mark.asyncio


async def test_product_repository_crud(async_session):
    repo = ProductRepository(async_session)

    created = await repo.create(
        name="Тестовый продукт",
        description="Описание",
        price=199.99,
        stock_quantity=15,
    )
    assert created.stock_quantity == 15

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Тестовый продукт"

    products, total = await repo.list()
    assert total == 1
    assert products[0].id == created.id

    updated = await repo.update(created.id, stock_quantity=10, price=149.99)
    assert updated.stock_quantity == 10
    assert updated.price == 149.99

    await repo.delete(created.id)
    assert await repo.get_by_id(created.id) is None

    with pytest.raises(ProductNotFoundError):
        await repo.delete(created.id)
