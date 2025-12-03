from __future__ import annotations

from uuid import UUID

from redis.asyncio import Redis

from app.models import Product
from app.repositories import ProductNotFoundError, ProductRepository
from app.schemas import ProductCreate, ProductMessage, ProductResponse, ProductUpdate

PRODUCT_CACHE_TTL_SECONDS = 600


class ProductService:
    """Business logic for product operations."""

    def __init__(
        self, product_repository: ProductRepository, cache: Redis | None = None
    ) -> None:
        self._product_repository = product_repository
        self._cache = cache

    async def get_product_by_id(
        self, product_id: UUID
    ) -> Product | ProductResponse | None:
        cache_key = self._product_cache_key(product_id)
        if self._cache:
            cached_product = await self._cache.get(cache_key)
            if cached_product:
                return ProductResponse.model_validate_json(cached_product)

        product = await self._product_repository.get_by_id(product_id)
        await self._update_product_cache(product)
        return product

    async def list_products(
        self, *, count: int = 100, page: int = 1
    ) -> tuple[list[Product], int]:
        return await self._product_repository.list(count=count, page=page)

    async def create_product(self, payload: ProductCreate) -> Product:
        product = await self._product_repository.create(**payload.model_dump())
        await self._update_product_cache(product)
        return product

    async def update_product(self, product_id: UUID, payload: ProductUpdate) -> Product:
        update_fields = payload.model_dump(exclude_unset=True)
        product = await self._product_repository.update(product_id, **update_fields)
        await self._update_product_cache(product)
        return product

    async def mark_out_of_stock(self, product_id: UUID) -> Product:
        product = await self._product_repository.update(product_id, stock_quantity=0)
        await self._update_product_cache(product)
        return product

    async def apply_message(self, message: ProductMessage) -> Product:
        """Handle a product message from the queue."""
        if message.action == "create":
            assert message.name is not None
            assert message.price is not None

            existing = await self._product_repository.get_by_name(message.name)
            if existing:
                data = ProductUpdate(
                    name=message.name,
                    description=message.description,
                    price=message.price,
                    stock_quantity=message.stock_quantity,
                )
                return await self.update_product(existing.id, data)

            payload = ProductCreate(
                name=message.name,
                description=message.description,
                price=message.price,
                stock_quantity=message.stock_quantity or 0,
            )
            return await self.create_product(payload)

        product = await self._locate_product(message.product_id, message.name)
        if message.action == "update":
            data = ProductUpdate(
                name=message.name,
                description=message.description,
                price=message.price,
                stock_quantity=message.stock_quantity,
            )
            return await self.update_product(product.id, data)

        if message.action == "mark_out_of_stock":
            return await self.mark_out_of_stock(product.id)

        raise ValueError(f"Unsupported product action: {message.action}")

    async def _locate_product(
        self, product_id: UUID | None, name: str | None
    ) -> Product:
        product: Product | None = None
        if product_id is not None:
            product = await self._product_repository.get_by_id(product_id)
        if product is None and name:
            product = await self._product_repository.get_by_name(name)
        if product is None:
            raise ProductNotFoundError("Product not found for update")
        return product

    async def _update_product_cache(self, product: Product | None) -> None:
        if self._cache is None or product is None:
            return

        await self._cache.setex(
            self._product_cache_key(product.id),
            PRODUCT_CACHE_TTL_SECONDS,
            ProductResponse.model_validate(product).model_dump_json(),
        )

    @staticmethod
    def _product_cache_key(product_id: UUID) -> str:
        return f"product:{product_id}"
