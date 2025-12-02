from __future__ import annotations

from uuid import UUID

from litestar import Controller, get, put
from litestar.exceptions import NotFoundException
from litestar.params import Parameter

from app.repositories import OrderNotFoundError
from app.schemas import (
    OrderListResponse,
    OrderResponse,
    OrderStatus,
    OrderStatusUpdate,
)
from app.services import OrderService


class OrderController(Controller):
    path = "/orders"

    @get()
    async def list_orders(
        self,
        order_service: OrderService,
        count: int = Parameter(default=10, ge=1, le=100),
        page: int = Parameter(default=1, ge=1),
        status: OrderStatus | None = Parameter(default=None),
    ) -> OrderListResponse:
        orders, total = await order_service.list_orders(
            count=count, page=page, status=status
        )
        return OrderListResponse(
            total=total,
            items=[OrderResponse.model_validate(order) for order in orders],
        )

    @get("/{order_id:uuid}")
    async def get_order(
        self,
        order_service: OrderService,
        order_id: UUID,
    ) -> OrderResponse:
        order = await order_service.get_order_by_id(order_id)
        if order is None:
            raise NotFoundException(detail=f"Order with ID {order_id} not found")
        return OrderResponse.model_validate(order)

    @put("/{order_id:uuid}/status")
    async def update_status(
        self,
        order_service: OrderService,
        order_id: UUID,
        data: OrderStatusUpdate,
    ) -> OrderResponse:
        try:
            order = await order_service.update_status(order_id, data.status)
        except OrderNotFoundError as exc:
            raise NotFoundException(detail=str(exc)) from exc
        return OrderResponse.model_validate(order)
