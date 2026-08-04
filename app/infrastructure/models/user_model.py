import uuid

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True,
        index = True,
    )

    public_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
        default= lambda: str(uuid.uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )