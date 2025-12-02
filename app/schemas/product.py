from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    price: float = Field(gt=0)
    stock_quantity: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    """Schema for creating a product."""


class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class ProductListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    items: list[ProductResponse]


class ProductMessage(BaseModel):
    """Payload accepted from RabbitMQ for product updates."""

    model_config = ConfigDict(extra="forbid")

    action: Literal["create", "update", "mark_out_of_stock"] = "create"
    product_id: UUID | None = None
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_action(self) -> "ProductMessage":
        if self.action == "create":
            if self.name is None or self.price is None:
                raise ValueError("name and price are required to create a product")
            if self.stock_quantity is None:
                self.stock_quantity = 0
        if self.action in {"update", "mark_out_of_stock"}:
            if self.product_id is None and self.name is None:
                raise ValueError("product_id or name is required to update a product")
        return self
