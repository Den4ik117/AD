from __future__ import annotations

from uuid import UUID

from litestar import Controller, get
from litestar.exceptions import NotFoundException
from litestar.params import Parameter

from app.schemas import ProductListResponse, ProductResponse
from app.services import ProductService


class ProductController(Controller):
    path = "/products"

    @get()
    async def list_products(
        self,
        product_service: ProductService,
        count: int = Parameter(default=10, ge=1, le=100),
        page: int = Parameter(default=1, ge=1),
    ) -> ProductListResponse:
        products, total = await product_service.list_products(count=count, page=page)
        return ProductListResponse(
            total=total,
            items=[ProductResponse.model_validate(product) for product in products],
        )

    @get("/{product_id:uuid}")
    async def get_product(
        self,
        product_service: ProductService,
        product_id: UUID,
    ) -> ProductResponse:
        product = await product_service.get_product_by_id(product_id)
        if product is None:
            raise NotFoundException(detail=f"Product with ID {product_id} not found")
        return ProductResponse.model_validate(product)
