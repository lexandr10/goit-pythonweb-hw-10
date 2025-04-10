from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DB_URL: str = (
        "postgres+asyncpg://postgres:alexandrenko2707@localhost:5432/contacts_db"
    )

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = "secret"
    # redis
    REDIS_URL: str = "redis://localhost"
    # email
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "Contacts App"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    # cloudinary
    CLD_NAME: str = "cloudinary_name"
    CLD_API_KEY: str = "cloudinary_api_key"
    CLD_API_SECRET: str = "cloudinary_api_secret"

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
