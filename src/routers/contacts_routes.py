import logging
from typing import Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.contacts_services import ContactService
from src.schemas.contact_schemas import (
    ContactSchema,
    ContactResponseSchema,
    ContactUpdateSchema,
)
from src.core.depend_service import get_current_user
from src.models.models_contacts import User


router = APIRouter(prefix="/contacts", tags=["contacts"])
logger = logging.getLogger("uvicorn.error")


@router.get("/", response_model=list[ContactResponseSchema])
async def get_contacts(
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.get_contacts(limit, offset, user)


@router.get("/{contact_id}", response_model=ContactResponseSchema)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.get_contact_by_id(contact_id, user)


@router.post(
    "/", response_model=ContactResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_contact(
    contact: ContactSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.create_contact(contact, user)


@router.put("/{contact_id}", response_model=ContactResponseSchema)
async def update_contact(
    contact_id: int,
    contact: ContactUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.update_contact(contact_id, contact, user)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.remove_contact(contact_id, user)


@router.get("/search/", response_model=list[ContactResponseSchema])
async def search_contacts(
    first_name: Optional[str] = Query(None, description="First name of the contact"),
    last_name: Optional[str] = Query(None, description="Last name of the contact"),
    email: Optional[str] = Query(None, description="Email of the contact"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    print("Services - print", f"first_name: {first_name}, last_name: {last_name}")
    return await contact_service.search_contacts(first_name, last_name, email, user)


@router.get("/birthday/", response_model=list[ContactResponseSchema])
async def get_contact_by_birthday(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    return await contact_service.get_contact_by_birthday(user)
