from __future__ import annotations

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.models import Address, Order, Product, User
from app.repositories import (
    AddressRepository,
    OrderRepository,
    ProductNotFoundError,
    ProductRepository,
    UserRepository,
)
from app.schemas import (
    OrderAddressPayload,
    OrderCreate,
    OrderItemPayload,
    OrderMessage,
    OrderStatus,
    OrderUserPayload,
    UserCreate,
)


class OrderService:
    """Business logic for handling orders."""

    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
        address_repository: AddressRepository,
    ) -> None:
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._user_repository = user_repository
        self._address_repository = address_repository

    async def get_order_by_id(self, order_id: UUID) -> Order | None:
        return await self._order_repository.get_by_id(order_id)

    async def list_orders(
        self,
        *,
        count: int = 10,
        page: int = 1,
        status: OrderStatus | None = None,
    ) -> tuple[list[Order], int]:
        filters: dict[str, OrderStatus] = {}
        if status:
            filters["status"] = status
        return await self._order_repository.get_by_filter(
            count=count, page=page, **filters
        )

    async def update_status(self, order_id: UUID, status: OrderStatus) -> Order:
        return await self._order_repository.update(order_id, status=status)

    async def create_order(self, order_data: OrderCreate) -> Order:
        user = await self._resolve_user(order_data.user_id, order_data.user)
        address = await self._resolve_address(
            order_data.address_id, order_data.address, user.id
        )
        items = await self._prepare_items(order_data.items)
        return await self._order_repository.create(
            user_id=user.id,
            address_id=address.id,
            items=items,
            status=order_data.status,
        )

    async def apply_message(self, message: OrderMessage) -> Order:
        if message.action == "create":
            order_data = OrderCreate(
                user_id=message.user_id,
                address_id=message.address_id,
                user=message.user,
                address=message.address,
                items=message.items,
                status=message.status,
            )
            return await self.create_order(order_data)

        if message.action == "update_status":
            if message.order_id is None:
                raise ValueError("order_id is required to update order status")
            return await self.update_status(message.order_id, message.status)

        raise ValueError(f"Unsupported order action: {message.action}")

    async def _resolve_user(
        self, user_id: UUID | None, payload: OrderUserPayload | None
    ) -> User:
        if user_id:
            user = await self._user_repository.get_by_id(user_id)
            if user is None:
                raise ValueError(f"User {user_id} not found")
            return user

        if payload is None:
            raise ValueError("User details are required to create an order")

        existing = await self._user_repository.get_by_email(payload.email)
        if existing:
            return existing

        try:
            return await self._user_repository.create(
                UserCreate(
                    username=payload.username,
                    email=payload.email,
                    description=payload.description,
                )
            )
        except IntegrityError as exc:
            # Fall back to fetching an existing user if a race condition occurs.
            user = await self._user_repository.get_by_email(payload.email)
            if user is not None:
                return user
            raise exc

    async def _resolve_address(
        self,
        address_id: UUID | None,
        payload: OrderAddressPayload | None,
        user_id: UUID,
    ) -> Address:
        if address_id:
            address = await self._address_repository.get_by_id(address_id)
            if address is None:
                raise ValueError(f"Address {address_id} not found")
            return address

        if payload is None:
            raise ValueError("Address details are required to create an order")

        existing = await self._address_repository.find_existing(
            user_id=user_id,
            street=payload.street,
            city=payload.city,
            state=payload.state,
            zip_code=payload.zip_code,
            country=payload.country,
        )
        if existing:
            return existing

        return await self._address_repository.create(
            user_id=user_id,
            street=payload.street,
            city=payload.city,
            state=payload.state,
            zip_code=payload.zip_code,
            country=payload.country,
            is_primary=payload.is_primary,
        )

    async def _prepare_items(
        self, payloads: list[OrderItemPayload]
    ) -> list[dict[str, object]]:
        items: list[dict[str, object]] = []
        for payload in payloads:
            product = await self._resolve_product(payload)
            if product.stock_quantity <= 0:
                raise ValueError(
                    f"Product '{product.name}' is out of stock and cannot be ordered"
                )
            if payload.quantity > product.stock_quantity:
                raise ValueError(
                    f"Not enough stock for '{product.name}' "
                    f"({payload.quantity} requested, {product.stock_quantity} available)"
                )

            unit_price = payload.unit_price or product.price
            product.stock_quantity -= payload.quantity
            items.append(
                {
                    "product_id": product.id,
                    "quantity": payload.quantity,
                    "unit_price": unit_price,
                }
            )
        return items

    async def _resolve_product(self, payload: OrderItemPayload) -> Product:
        product: Product | None = None
        if payload.product_id is not None:
            product = await self._product_repository.get_by_id(payload.product_id)
        if product is None and payload.product_name:
            product = await self._product_repository.get_by_name(payload.product_name)
        if product is None:
            raise ProductNotFoundError("Product not found for order creation")
        return product
