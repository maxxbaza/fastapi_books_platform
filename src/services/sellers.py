__all__ = ["SellerService"]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.sellers import Seller
from src.schemas.sellers import IncomingSeller, UpdateSeller


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_seller(self, seller_data: IncomingSeller) -> Seller:
        seller = Seller(
            first_name=seller_data.first_name,
            last_name=seller_data.last_name,
            e_mail=seller_data.e_mail,
            password=seller_data.password,
        )
        self.session.add(seller)
        await self.session.flush()
        return seller

    async def get_all_sellers(self) -> list[Seller]:
        query = select(Seller)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_single_seller(self, seller_id: int) -> Seller | None:
        query = (
            select(Seller)
            .options(selectinload(Seller.books))
            .where(Seller.id == seller_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_seller(self, seller_id: int, seller_data: UpdateSeller) -> Seller | None:
        seller = await self.session.get(Seller, seller_id)
        if seller is None:
            return None

        seller.first_name = seller_data.first_name
        seller.last_name = seller_data.last_name
        seller.e_mail = seller_data.e_mail
        await self.session.flush()
        return seller

    async def delete_seller(self, seller_id: int) -> bool:
        seller = await self.session.get(Seller, seller_id)
        if seller is None:
            return False

        await self.session.delete(seller)
        return True