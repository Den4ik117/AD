"""Shared application schemas."""

from .order import (
    OrderAddressPayload,
    OrderCreate,
    OrderItemPayload,
    OrderListResponse,
    OrderMessage,
    OrderResponse,
    OrderStatus,
    OrderStatusUpdate,
    OrderUserPayload,
)
from .product import (
    ProductCreate,
    ProductListResponse,
    ProductMessage,
    ProductResponse,
    ProductUpdate,
)
from .user import UserCreate, UserListResponse, UserResponse, UserUpdate

__all__ = [
    "UserCreate",
    "UserListResponse",
    "UserResponse",
    "UserUpdate",
    "ProductCreate",
    "ProductUpdate",
    "ProductMessage",
    "ProductResponse",
    "ProductListResponse",
    "OrderCreate",
    "OrderMessage",
    "OrderResponse",
    "OrderListResponse",
    "OrderStatus",
    "OrderStatusUpdate",
    "OrderItemPayload",
    "OrderAddressPayload",
    "OrderUserPayload",
]
