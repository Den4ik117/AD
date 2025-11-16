from __future__ import annotations

import pytest

from app.models import Address, User
from app.repositories import OrderNotFoundError, OrderRepository, ProductRepository


pytestmark = pytest.mark.asyncio


async def _create_user_and_address(session, idx: int = 0):
    user = User(
        username=f"user_{idx}",
        email=f"user_{idx}@example.com",
        description="Покупатель",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    address = Address(
        user_id=user.id,
        street=f"Улица {idx}",
        city="Москва",
        state="Московская область",
        zip_code="101000",
        country="Россия",
        is_primary=True,
    )
    session.add(address)
    await session.commit()
    await session.refresh(address)
    return user, address


async def test_order_repository_handles_multi_item_orders(async_session):
    order_repo = OrderRepository(async_session)
    product_repo = ProductRepository(async_session)

    user, address = await _create_user_and_address(async_session)
    milk = await product_repo.create(name="Молоко", description="1 л", price=80.0, stock_quantity=20)
    bread = await product_repo.create(name="Хлеб", description="500 г", price=50.0, stock_quantity=30)

    created = await order_repo.create(
        user_id=user.id,
        address_id=address.id,
        status="pending",
        items=[
            {"product_id": milk.id, "quantity": 2, "unit_price": milk.price},
            {"product_id": bread.id, "quantity": 1, "unit_price": bread.price},
        ],
    )
    assert created.total_price == pytest.approx(2 * milk.price + bread.price)
    assert len(created.items) == 2

    fetched = await order_repo.get_by_id(created.id)
    assert fetched is not None
    assert sorted(item.product_id for item in fetched.items) == sorted([milk.id, bread.id])

    orders, total = await order_repo.get_by_filter(count=5, page=1)
    assert total == 1
    assert orders[0].id == created.id

    cheese = await product_repo.create(name="Сыр", description="200 г", price=210.0, stock_quantity=15)
    updated = await order_repo.update(
        created.id,
        status="completed",
        items=[
            {"product_id": cheese.id, "quantity": 3, "unit_price": cheese.price},
        ],
    )
    assert updated.status == "completed"
    assert len(updated.items) == 1
    assert updated.total_price == pytest.approx(3 * cheese.price)

    await order_repo.delete(created.id)
    assert await order_repo.get_by_id(created.id) is None

    with pytest.raises(OrderNotFoundError):
        await order_repo.delete(created.id)
