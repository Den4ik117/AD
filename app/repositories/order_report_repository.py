from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, OrderItem, OrderReport


class OrderReportRepository:
    """Async repository for reporting rows."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_date(self, report_at: date) -> list[OrderReport]:
        stmt = (
            select(OrderReport)
            .where(OrderReport.report_at == report_at)
            .order_by(OrderReport.order_id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def upsert_for_date(self, report_at: date) -> list[OrderReport]:
        aggregates = await self._session.execute(
            select(
                func.date(Order.created_at).label("report_at"),
                Order.id.label("order_id"),
                func.coalesce(func.sum(OrderItem.quantity), 0).label("count_product"),
            )
            .join(OrderItem, Order.items)
            .where(func.date(Order.created_at) == report_at)
            .group_by(Order.id)
        )
        rows = aggregates.all()
        if not rows:
            return []

        payload = [
            {
                "report_at": row.report_at,
                "order_id": row.order_id,
                "count_product": int(row.count_product),
            }
            for row in rows
        ]

        insert_stmt = insert(OrderReport).values(payload)
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[OrderReport.report_at, OrderReport.order_id],
            set_={"count_product": insert_stmt.excluded.count_product},
        ).returning(OrderReport)
        result = await self._session.execute(upsert_stmt)
        await self._session.commit()
        return result.scalars().all()
