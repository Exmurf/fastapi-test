from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import (
    UserRepository,
)
from app.domain.security.authorization import (
    UserRole,
)
from app.infrastructure.models.user_model import (
    UserModel,
)


class SQLAlchemyUserRepository(
    UserRepository
):
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        user: User,
    ) -> User:
        user_model = UserModel(
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            is_active=user.is_active,
        )

        self.db.add(
            user_model
        )

        self.db.commit()

        self.db.refresh(
            user_model
        )

        return self._to_entity(
            user_model
        )

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        user_model = (
            self.db
            .query(UserModel)
            .filter(
                UserModel.email == email
            )
            .first()
        )

        if user_model is None:
            return None

        return self._to_entity(
            user_model
        )

    def get_by_public_id(
        self,
        public_id: str,
    ) -> User | None:
        user_model = (
            self.db
            .query(UserModel)
            .filter(
                UserModel.public_id
                == public_id
            )
            .first()
        )

        if user_model is None:
            return None

        return self._to_entity(
            user_model
        )

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        user_model = (
            self.db
            .query(UserModel)
            .filter(
                UserModel.id
                == user_id
            )
            .first()
        )

        if user_model is None:
            return None

        return self._to_entity(
            user_model
        )

    def get_all(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        query = self.db.query(
            UserModel
        )

        if search is not None:
            query = query.filter(
                UserModel.email.ilike(
                    f"%{search}%"
                )
            )

        if role is not None:
            query = query.filter(
                UserModel.role == role
            )

        if is_active is not None:
            query = query.filter(
                UserModel.is_active
                == is_active
            )

        total_items = (
            query.count()
        )

        offset = (
            page - 1
        ) * page_size

        user_models = (
            query
            .order_by(
                UserModel.id.asc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        users = [
            self._to_entity(
                user_model
            )
            for user_model
            in user_models
        ]

        return (
            users,
            total_items,
        )

    @staticmethod
    def _to_entity(
        user_model: UserModel,
    ) -> User:
        return User(
            id=user_model.id,
            public_id=(
                user_model.public_id
            ),
            email=user_model.email,
            password_hash=(
                user_model.password_hash
            ),
            role=user_model.role,
            is_active=(
                user_model.is_active
            ),
            created_at=(
                user_model.created_at
            ),
        )