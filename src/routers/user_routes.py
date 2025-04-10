import logging

from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
    UploadFile,
    File,
    BackgroundTasks,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.conf.config import settings
from src.core.email_token import get_email_token
from src.database.db import get_db
from src.schemas.email_schema import RequestEmailSchema
from src.schemas.user_schemas import UserResponseSchema
from src.services.auth_service import AuthService, oauth2_scheme
from src.models.models_contacts import User
from src.services.service_email import send_email
from src.services.user_service import UserService
from src.services.upload_file_service import UploadFileService


router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger("uvicorn.error")


async def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)


async def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
@limiter.limit("10/minute")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    request: Request = None,
):
    return await auth_service.get_current_user(token)


@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str, user_service: UserService = Depends(get_user_service)
):
    email = get_email_token(token)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.confirmed:
        return {"message": "Email already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmailSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_email(str(body.email))

    if user.confirmed:
        return {"message": "Email already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, body.email, user.username, str(request.base_url)
        )

    return {"message": "Email sent"}


@router.post("/avatar", response_model=UserResponseSchema)
async def update_avatar(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    avatar_url = UploadFileService(
        settings.cloud_name, settings.api_key, settings.api_secret
    ).upload_file(file, user.username)

    current_user = await user_service.update_avatar(user.email, avatar_url)

    return current_user
