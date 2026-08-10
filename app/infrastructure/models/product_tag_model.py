from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Table,
)

from app.infrastructure.database import Base


product_tags = Table(
    "product_tags",
    Base.metadata,

    Column(
        "product_id",
        Integer,
        ForeignKey("products.id"),
        primary_key=True,
    ),

    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id"),
        primary_key=True,
    ),
)