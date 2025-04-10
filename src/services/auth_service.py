from datetime import datetime, timedelta, timezone
import secrets

import jwt
import redis.asyncio as redis
import bcrypt
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.conf.config import settings
from src.models.models_contacts import User
from src.schemas.user_schemas import UserCreateSchema
from src.controlllers.user_conrollers import UserController
from src.controlllers.refresh_token_controller import RefreshTokenController


redis_client = redis.from_url(settings.REDIS_URL)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_controller = UserController(self.db)
        self.refresh_token_controller = RefreshTokenController(self.db)

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def authenticate(self, username: str, password: str) -> User:
        user = await self.user_controller.get_by_username(username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        if not user.confirmed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not confirmed",
            )

        if not self._verify_password(password, user.hash_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        return user

    async def register_user(self, user: UserCreateSchema) -> User:
        checked_user = await self.user_controller.get_by_username(user.username)
        if checked_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )
        if await self.user_controller.get_user_email(str(user.email)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )

        avatar = None
        try:
            g = Gravatar(user.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        hashed_password = self._hash_password(user.password)
        user = await self.user_controller.create_user(user, hashed_password, avatar)

        return user

    def create_access_token(self, username: str) -> str:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode = {"exp": expire, "sub": username}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def create_refresh_token(
        self, user_id: int, ip_address: str | None, user_agent: str | None
    ) -> str:
        token = secrets.token_hex(16)
        token_hash = self._hash_token(token)
        expired_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self.refresh_token_controller.create_token(
            user_id, token_hash, expired_at, ip_address, user_agent
        )
        return token

    def decode_and_verify_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not valid"
            )

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        if await redis_client.exists(f"bl:{token}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not valid"
            )

        payload = self.decode_and_verify_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        user = await self.user_controller.get_by_username(username=username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    async def validate_refresh_token(self, token: str) -> User:
        token_hash = self._hash_token(token)
        current_time = datetime.now(timezone.utc)
        refresh_token = await self.refresh_token_controller.get_active_token(
            token_hash, current_time
        )
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
        if not refresh_token.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return refresh_token.user

    async def revoke_refresh_token(self, token: str) -> None:
        token_hash = self._hash_token(token)
        refresh_token = await self.refresh_token_controller.get_by_token_hash(
            token_hash
        )
        if refresh_token and not refresh_token.revoked_at:
            await self.refresh_token_controller.revoke_token(refresh_token)
        return None

    async def revoke_access_token(self, token: str) -> None:
        payload = self.decode_and_verify_access_token(token)
        exp = payload.get("exp")
        if exp:
            await redis_client.setex(
                f"bl:{token}", exp - datetime.now(timezone.utc).timestamp(), "1"
            )
