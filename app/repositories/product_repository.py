from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product


class ProductNotFoundError(LookupError):
    """Raised when a product cannot be located."""


class ProductRepository:
    """Async repository managing product persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, product_id: UUID) -> Product | None:
        return await self._session.get(Product, product_id)

    async def list(
        self,
        count: int = 100,
        page: int = 1,
        **filters: Any,
    ) -> tuple[list[Product], int]:
        query = self._apply_filters(select(Product), filters)
        total_query = self._apply_filters(select(func.count()).select_from(Product), filters)

        limited_query = query.order_by(Product.created_at.desc()).limit(count).offset((page - 1) * count)
        result = await self._session.execute(limited_query)
        products = result.scalars().all()

        total = await self._session.scalar(total_query)
        return products, int(total or 0)

    async def create(self, *, name: str, price: float, description: str | None = None, stock_quantity: int = 0) -> Product:
        product = Product(
            name=name,
            price=price,
            description=description,
            stock_quantity=stock_quantity,
        )
        self._session.add(product)
        await self._session.commit()
        await self._session.refresh(product)
        return product

    async def update(
        self,
        product_id: UUID,
        **fields: Any,
    ) -> Product:
        product = await self.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} not found")

        for field, value in fields.items():
            if value is not None and hasattr(product, field):
                setattr(product, field, value)

        await self._session.commit()
        await self._session.refresh(product)
        return product

    async def delete(self, product_id: UUID) -> None:
        product = await self.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} not found")

        await self._session.delete(product)
        await self._session.commit()

    @staticmethod
    def _apply_filters(query: Select[Any], filters: dict[str, Any]) -> Select[Any]:
        for field, value in filters.items():
            if value is None:
                continue
            column = getattr(Product, field, None)
            if column is not None:
                query = query.where(column == value)
        return query
