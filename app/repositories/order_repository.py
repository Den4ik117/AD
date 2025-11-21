from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Order, OrderItem


class OrderNotFoundError(LookupError):
    """Raised when an order does not exist."""


class OrderRepository:
    """Async repository managing orders and their items."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, order_id: UUID) -> Order | None:
        stmt = (
            select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_filter(
        self,
        count: int = 10,
        page: int = 1,
        **filters: Any,
    ) -> tuple[list[Order], int]:
        query = self._apply_filters(select(Order), filters).options(
            selectinload(Order.items)
        )
        total_query = self._apply_filters(
            select(func.count()).select_from(Order), filters
        )

        limited_query = (
            query.order_by(Order.created_at.desc())
            .limit(count)
            .offset((page - 1) * count)
        )
        result = await self._session.execute(limited_query)
        orders = result.scalars().all()

        total = await self._session.scalar(total_query)
        return orders, int(total or 0)

    async def create(
        self,
        *,
        user_id: UUID,
        address_id: UUID,
        items: Sequence[dict[str, Any]],
        status: str = "pending",
    ) -> Order:
        if not items:
            raise ValueError("Order must contain at least one item")

        order = Order(
            user_id=user_id,
            address_id=address_id,
            status=status,
            total_price=0,
        )

        for payload in items:
            order_item = OrderItem(
                product_id=payload["product_id"],
                quantity=payload["quantity"],
                unit_price=payload["unit_price"],
            )
            order.items.append(order_item)

        order.total_price = sum(item.quantity * item.unit_price for item in order.items)
        self._session.add(order)
        await self._session.flush()
        order_id = order.id
        await self._session.commit()
        return await self.get_or_raise(order_id)

    async def update(
        self,
        order_id: UUID,
        *,
        status: str | None = None,
        items: Sequence[dict[str, Any]] | None = None,
    ) -> Order:
        order = await self.get_or_raise(order_id)

        if status is not None:
            order.status = status

        if items is not None:
            order.items.clear()
            for payload in items:
                order.items.append(
                    OrderItem(
                        product_id=payload["product_id"],
                        quantity=payload["quantity"],
                        unit_price=payload["unit_price"],
                    )
                )
            order.total_price = sum(
                item.quantity * item.unit_price for item in order.items
            )

        await self._session.commit()
        return await self.get_or_raise(order.id)

    async def delete(self, order_id: UUID) -> None:
        order = await self.get_or_raise(order_id)
        await self._session.delete(order)
        await self._session.commit()

    async def get_or_raise(self, order_id: UUID) -> Order:
        order = await self.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return order

    @staticmethod
    def _apply_filters(query: Select[Any], filters: dict[str, Any]) -> Select[Any]:
        for field, value in filters.items():
            if value is None:
                continue
            column = getattr(Order, field, None)
            if column is not None:
                query = query.where(column == value)
        return query
