from datetime import date, datetime


from sqlalchemy import String, Date, func, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.conf.constants import NAME_MAX_LENGTH, NAME_MIN_LENGTH, MAX_PHONE_LENGTH


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False)
    last_name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False)
    email: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH), nullable=False, unique=True
    )
    phone: Mapped[str] = mapped_column(
        String(MAX_PHONE_LENGTH), nullable=False, unique=True
    )
    birthday: Mapped[date] = mapped_column(
        Date, default=func.current_date(), nullable=False
    )
    additional_data: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH))

    created_at: Mapped[date] = mapped_column(Date, default=func.current_date())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hash_password: Mapped[str] = mapped_column(nullable=False)

    avatar: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")
