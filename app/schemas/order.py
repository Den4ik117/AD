from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

OrderStatus = Literal["pending", "completed", "cancelled", "processing"]


class OrderUserPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    email: str
    description: str | None = None


class OrderAddressPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    street: str
    city: str
    state: str
    zip_code: str
    country: str
    is_primary: bool = False


class OrderItemPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: UUID | None = None
    product_name: str | None = None
    quantity: int = Field(gt=0)
    unit_price: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_lookup(self) -> "OrderItemPayload":
        if self.product_id is None and self.product_name is None:
            msg = "Either product_id or product_name must be provided for an order item"
            raise ValueError(msg)
        return self


class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID | None = None
    address_id: UUID | None = None
    user: OrderUserPayload | None = None
    address: OrderAddressPayload | None = None
    items: list[OrderItemPayload] = Field(default_factory=list)
    status: OrderStatus = "pending"

    @model_validator(mode="after")
    def validate_payload(self) -> "OrderCreate":
        if not self.items:
            raise ValueError("Order must include at least one item")
        if self.user_id is None and self.user is None:
            raise ValueError("User details are required to create an order")
        if self.address_id is None and self.address is None:
            raise ValueError("Address details are required to create an order")
        return self


class OrderMessage(BaseModel):
    """Payload accepted from RabbitMQ for order actions."""

    model_config = ConfigDict(extra="forbid")

    action: Literal["create", "update_status"] = "create"
    order_id: UUID | None = None
    user_id: UUID | None = None
    address_id: UUID | None = None
    user: OrderUserPayload | None = None
    address: OrderAddressPayload | None = None
    items: list[OrderItemPayload] = Field(default_factory=list)
    status: OrderStatus = "pending"

    @model_validator(mode="after")
    def validate_action(self) -> "OrderMessage":
        if self.action == "create":
            if not self.items:
                raise ValueError("Order must contain at least one item")
            if self.user_id is None and self.user is None:
                raise ValueError("User info is required for order creation")
            if self.address_id is None and self.address is None:
                raise ValueError("Address info is required for order creation")
        if self.action == "update_status" and self.order_id is None:
            raise ValueError("order_id is required to update status")
        return self


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: UUID
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    address_id: UUID
    status: OrderStatus
    total_price: float
    items: list[OrderItemResponse]


class OrderListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    items: list[OrderResponse]


class OrderStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: OrderStatus
