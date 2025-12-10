from __future__ import annotations

from datetime import date

from litestar import Controller, get
from litestar.params import Parameter

from app.schemas import OrderReportItem, OrderReportResponse
from app.services import OrderReportService


class ReportController(Controller):
    path = "/report"

    @get()
    async def get_report(
        self,
        order_report_service: OrderReportService,
        report_at: date = Parameter(
            title="Report date", description="Day to fetch order report for."
        ),
    ) -> OrderReportResponse:
        entries = await order_report_service.get_report(report_at)
        return OrderReportResponse(
            report_at=report_at,
            total=len(entries),
            items=[OrderReportItem.model_validate(entry) for entry in entries],
        )
