from __future__ import annotations

import logging
import os
from datetime import date

from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

from app.db import async_session_factory
from app.repositories import OrderReportRepository
from app.services import OrderReportService

logger = logging.getLogger(__name__)

broker = AioPikaBroker(
    os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/local"),
    exchange_name="report",
    queue_name="cmd_order",
)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


@broker.task(
    schedule=[
        {
            "cron": "*/1 * * * *",
            "args": [],
            "schedule_id": "order_report_every_minute",
        }
    ]
)
async def my_scheduled_task() -> str:
    report_date = date.today()
    async with async_session_factory() as session:
        service = OrderReportService(OrderReportRepository(session))
        reports = await service.generate_report(report_date)

    message = (
        f"Generated {len(reports)} order report rows " f"for {report_date.isoformat()}"
    )
    logger.info(message)
    return message
