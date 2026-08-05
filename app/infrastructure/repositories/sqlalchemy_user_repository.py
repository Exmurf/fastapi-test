from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.models.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        user_model = UserModel(
            email=user.email,
            password_hash=user.password_hash,
            is_active=user.is_active,
        )

        self.db.add(user_model)
        self.db.commit()
        self.db.refresh(user_model)

        return self._to_entity(user_model)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        user_model = (
            self.db.query(UserModel)
            .filter(UserModel.email == email)
            .first()
        )

        if user_model is None:
            return None

        return self._to_entity(user_model)

    def get_by_public_id(
        self,
        public_id: str,
    ) -> User | None:
        user_model = (
            self.db.query(UserModel)
            .filter(UserModel.public_id == public_id)
            .first()
        )

        if user_model is None:
            return None

        return self._to_entity(user_model)

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        user_model = (
            self.db.query(UserModel)
            .filter(UserModel.id == user_id)
            .first()
        )

        if user_model is None:
            return None

        return self._to_entity(user_model)
        
    @staticmethod
    def _to_entity(
        user_model: UserModel,
    ) -> User:
        return User(
            id = user_model.id,
            public_id=user_model.public_id,
            email=user_model.email,
            password_hash=user_model.password_hash,
            is_active=user_model.is_active,
        )