import logging


from fastapi import APIRouter, Depends, Request, status, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.token_schemas import TokenResponseSchema, RefreshTokenResponseSchema
from src.services.auth_service import AuthService, oauth2_scheme
from src.schemas.user_schemas import UserCreateSchema, UserResponseSchema
from src.services.service_email import send_email


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("uvicorn.error")


def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)


@router.post(
    "/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def register_user(
    data: UserCreateSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register_user(data)

    background_tasks.add_task(
        send_email, data.email, data.username, str(request.base_url)
    )

    return user


@router.post("/login", response_model=TokenResponseSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate(form_data.username, form_data.password)
    access_token = auth_service.create_access_token(user.username)
    refresh_token = await auth_service.create_refresh_token(
        int(user.id),
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )

    return TokenResponseSchema(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh_token(
    refresh_token_data: RefreshTokenResponseSchema,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.validate_refresh_token(refresh_token_data.refresh_token)

    access_token = auth_service.create_access_token(user.username)
    refresh_token = await auth_service.create_refresh_token(
        int(user.id),
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    await auth_service.revoke_refresh_token(refresh_token_data.refresh_token)

    return TokenResponseSchema(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token_data: RefreshTokenResponseSchema,
    auth_service: AuthService = Depends(get_auth_service),
    token=Depends(oauth2_scheme),
):
    await auth_service.revoke_refresh_token(refresh_token_data.refresh_token)
    await auth_service.revoke_access_token(token)
    return None
