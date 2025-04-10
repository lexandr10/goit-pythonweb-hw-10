from typing import List, Sequence, Optional
import logging
from datetime import date, timedelta


from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.models.models_contacts import Contact
from src.schemas.contact_schemas import (
    ContactResponseSchema,
    ContactUpdateSchema,
    ContactSchema,
)
from src.models.models_contacts import User

logger = logging.getLogger("uvicorn.error")


class ContactController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_contacts(
        self, limit: int = 10, offset: int = 0, user: User = None
    ) -> Sequence[Contact]:
        stmt = select(Contact).filter_by(user_id=user.id).limit(limit).offset(offset)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact:
        stmt = select(Contact).filter_by(id=contact_id, user_id=user.id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, contact: ContactSchema, user: User) -> Contact:
        new_contact = Contact(**contact.model_dump(), user=user)
        self.db.add(new_contact)
        await self.db.commit()
        await self.db.refresh(new_contact)
        return new_contact

    async def update_contact(
        self, contact_id: int, contact: ContactUpdateSchema, user: User
    ) -> Contact:
        db_contact = await self.get_contact_by_id(contact_id, user)

        if not db_contact:
            raise HTTPException(status_code=404, detail="Contact not found")

        update_data = contact.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contact, key, value)

        await self.db.commit()
        await self.db.refresh(db_contact)
        return db_contact

    async def remove_contact(self, contact_id: int, user: User) -> None:
        contact = await self.get_contact_by_id(contact_id, user)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        await self.db.delete(contact)
        await self.db.commit()

    async def search_contacts(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        user: User = None,
    ) -> Sequence[Contact]:
        if not any([first_name, last_name, email, user]):
            raise HTTPException(
                status_code=400, detail="At least one search parameter must be provided"
            )
        filters = []

        if last_name:
            filters.append(Contact.last_name.ilike(f"%{last_name.lower()}%"))
        if first_name:
            filters.append(Contact.first_name.ilike(f"%{first_name.lower()}%"))
        if email:
            filters.append(Contact.email == email)

        stmt = select(Contact).where(*filters, Contact.user_id == user.id)
        print(f"Generated SQL: {stmt}")
        print(f"Last name filter: {last_name}")
        result = await self.db.execute(stmt)
        contacts = result.scalars().all()

        if not contacts:
            raise HTTPException(status_code=404, detail="Contacts not found")
        return contacts

    async def get_contact_by_birthday(self, user: User) -> Sequence[Contact]:
        today = date.today()
        next_week = today + timedelta(days=7)

        stmt = select(Contact).where(
            and_(
                func.to_char(Contact.birthday, "MM-DD") >= today.strftime("%m-%d"),
                func.to_char(Contact.birthday, "MM-DD") <= next_week.strftime("%m-%d"),
                Contact.user_id == user.id,
            )
        )
        result = await self.db.execute(stmt)
        contacts = result.scalars().all()
        return contacts
