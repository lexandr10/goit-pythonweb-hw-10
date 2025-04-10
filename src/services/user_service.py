from sqlalchemy.ext.asyncio import AsyncSession

from src.controlllers.user_conrollers import UserController
from src.schemas.user_schemas import UserCreateSchema
from src.services.auth_service import AuthService, oauth2_scheme
from src.models.models_contacts import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_controller = UserController(self.db)
        self.auth_service = AuthService(self.db)

    async def create_user(self, user: UserCreateSchema) -> User | None:
        user = await self.auth_service.register_user(user)
        return user

    async def get_user_by_username(self, username: str) -> User | None:
        user = await self.user_controller.get_by_username(username=username)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        user = await self.user_controller.get_user_email(email=email)
        return user

    async def confirmed_email(self, email: str) -> None:
        user = await self.user_controller.confirmed_email(email=email)
        return user

    async def update_avatar(self, email: str, url: str) -> User:
        return await self.user_controller.update_avatar(email=email, url=url)
