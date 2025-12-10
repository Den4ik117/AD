from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrderReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_at: date
    order_id: UUID
    count_product: int


class OrderReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_at: date
    total: int
    items: list[OrderReportItem]
