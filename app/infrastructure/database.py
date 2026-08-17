from datetime import datetime, timezone

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine,
)

Base = declarative_base()


def _build_migrated_deleted_email(
    email: str,
    public_id: str,
    deleted_at: datetime,
) -> str:
    local_part, separator, domain = (
        email.partition("@")
    )

    if separator == "":
        domain = "deleted.invalid"

    suffix = (
        "+deleted-"
        f"{deleted_at.strftime('%Y%m%d%H%M%S')}-"
        f"{public_id[:8]}"
    )
    max_local_length = max(
        1,
        254
        - len(domain)
        - 1
        - len(suffix),
    )

    return (
        f"{local_part[:max_local_length]}"
        f"{suffix}@{domain}"
    )


def ensure_user_lifecycle_schema() -> None:
    database_inspector = inspect(engine)

    if "users" not in (
        database_inspector
        .get_table_names()
    ):
        return

    existing_columns = {
        column["name"]
        for column in (
            database_inspector
            .get_columns("users")
        )
    }
    added_is_deleted = (
        "is_deleted"
        not in existing_columns
    )

    with engine.begin() as connection:
        if added_is_deleted:
            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN is_deleted BOOLEAN "
                    "NOT NULL DEFAULT 0"
                )
            )

        if "deleted_at" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN deleted_at DATETIME"
                )
            )

        if not added_is_deleted:
            return

        deleted_at = datetime.now(
            timezone.utc
        ).replace(tzinfo=None)
        legacy_deleted_users = (
            connection.execute(
                text(
                    "SELECT id, public_id, email "
                    "FROM users "
                    "WHERE is_active = 0"
                )
            )
            .mappings()
            .all()
        )

        for user in legacy_deleted_users:
            deleted_email = (
                _build_migrated_deleted_email(
                    email=user["email"],
                    public_id=user["public_id"],
                    deleted_at=deleted_at,
                )
            )
            connection.execute(
                text(
                    "UPDATE users "
                    "SET email = :email, "
                    "is_deleted = 1, "
                    "deleted_at = :deleted_at "
                    "WHERE id = :user_id"
                ),
                {
                    "email": deleted_email,
                    "deleted_at": deleted_at,
                    "user_id": user["id"],
                },
            )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
