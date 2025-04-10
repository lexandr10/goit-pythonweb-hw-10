import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models_contacts import User
from src.schemas.user_schemas import UserCreateSchema
from src.controlllers.base_conroller import BaseController

logger = logging.getLogger("uvicorn.error")


class UserController(BaseController):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(self.model).filter_by(username=username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_email(self, email: str) -> User | None:
        stmt = select(self.model).filter_by(email=email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self, user: UserCreateSchema, hash_password: str, avatar: str
    ) -> User:
        new_user = User(
            **user.model_dump(exclude_unset=True, exclude={"password"}),
            hash_password=hash_password,
            avatar=avatar,
        )
        self.db.add(new_user)
        return await self.create(new_user)

    # func confirmed_email
    async def confirmed_email(self, email: str):
        user = await self.get_user_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar(self, email: str, url: str) -> User:
        user = await self.get_user_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
