from sqlalchemy import (
    Float, 
    Integer, 
    String, 
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

import uuid
from app.infrastructure.database import Base


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    public_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
        default= lambda: str(uuid.uuid4()),
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )