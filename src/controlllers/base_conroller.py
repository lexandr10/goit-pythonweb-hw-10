from typing import List,  TypeVar, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.models_contacts import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseController:
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.model = model
        self.db = db

    async def get_all(self) -> List[ModelType]:
        stmt = select(self.model)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, _id: int) -> ModelType:
        stmt = select(self.model).filter_by(id=_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: ModelType) -> ModelType:
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.db.delete(instance)
        await self.db.commit()