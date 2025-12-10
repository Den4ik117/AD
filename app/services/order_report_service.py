from __future__ import annotations

from datetime import date

from app.models import OrderReport
from app.repositories import OrderReportRepository


class OrderReportService:
    def __init__(self, order_report_repository: OrderReportRepository) -> None:
        self._order_report_repository = order_report_repository

    async def generate_report(self, report_at: date | None = None) -> list[OrderReport]:
        target_date = report_at or date.today()
        return await self._order_report_repository.upsert_for_date(target_date)

    async def get_report(self, report_at: date) -> list[OrderReport]:
        return await self._order_report_repository.get_by_date(report_at)
