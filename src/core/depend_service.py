from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.database.db import get_db
from src.services.auth_service import AuthService, oauth2_scheme
from src.services.user_service import UserService


def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)


async def get_current_user(
    auth_service: AuthService = Depends(get_user_service),
    token: str = Depends(oauth2_scheme),
):
    return await auth_service.get_current_user(token)
