from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Address


class AddressRepository:
    """Async repository for address persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, address_id: UUID) -> Address | None:
        return await self._session.get(Address, address_id)

    async def find_existing(
        self,
        *,
        user_id: UUID,
        street: str,
        city: str,
        state: str,
        zip_code: str,
        country: str,
    ) -> Address | None:
        stmt = select(Address).where(
            Address.user_id == user_id,
            Address.street == street,
            Address.city == city,
            Address.state == state,
            Address.zip_code == zip_code,
            Address.country == country,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        user_id: UUID,
        street: str,
        city: str,
        state: str,
        zip_code: str,
        country: str,
        is_primary: bool = False,
    ) -> Address:
        address = Address(
            user_id=user_id,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            is_primary=is_primary,
        )
        self._session.add(address)
        await self._session.commit()
        await self._session.refresh(address)
        return address
