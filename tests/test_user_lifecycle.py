import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.exceptions import AuthenticationError
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.domain.entities.user import User
from app.domain.security.authorization import UserRole
from app.infrastructure.database import Base
from app.infrastructure.models.user_model import UserModel
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


class ActivityLogStub:
    def __init__(self):
        self.entries = []

    def log(self, **entry):
        self.entries.append(entry)


class PasswordHasherStub:
    def hash(self, password: str) -> str:
        return password

    def verify(
        self,
        plain_password: str,
        password_hash: str,
    ) -> bool:
        return plain_password == password_hash


class UserLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:"
        )
        Base.metadata.create_all(
            bind=self.engine,
            tables=[UserModel.__table__],
        )
        session_factory = sessionmaker(
            bind=self.engine
        )
        self.db = session_factory()
        self.repository = (
            SQLAlchemyUserRepository(
                self.db
            )
        )
        self.activity_log = (
            ActivityLogStub()
        )
        self.service = UserService(
            user_repository=(
                self.repository
            ),
            activity_log_service=(
                self.activity_log
            ),
        )
        self.admin = self._create_user(
            "admin@example.com",
            UserRole.ADMIN,
        )
        self.user = self._create_user(
            "user@example.com",
            UserRole.USER,
        )

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _create_user(
        self,
        email: str,
        role: UserRole,
    ) -> User:
        return self.repository.create(
            User(
                id=None,
                public_id=None,
                email=email,
                password_hash="password",
                role=role,
            )
        )

    def test_active_state_and_deletion_are_independent(self):
        inactive_user = (
            self.service
            .update_user_active(
                current_user=self.admin,
                user_public_id=(
                    self.user.public_id
                ),
                is_active=False,
            )
        )

        self.assertFalse(
            inactive_user.is_active
        )
        self.assertFalse(
            inactive_user.is_deleted
        )

        deleted_user = (
            self.service.delete_user(
                current_user=self.admin,
                user_public_id=(
                    self.user.public_id
                ),
            )
        )

        self.assertFalse(
            deleted_user.is_active
        )
        self.assertTrue(
            deleted_user.is_deleted
        )
        self.assertIsNotNone(
            deleted_user.deleted_at
        )
        self.assertIn(
            "+deleted-",
            deleted_user.email,
        )
        self.assertIsNone(
            self.repository.get_by_email(
                "user@example.com"
            )
        )

        replacement = self._create_user(
            "user@example.com",
            UserRole.USER,
        )
        self.assertEqual(
            replacement.email,
            "user@example.com",
        )

    def test_inactive_user_receives_explicit_login_error(self):
        self.service.update_user_active(
            current_user=self.admin,
            user_public_id=(
                self.user.public_id
            ),
            is_active=False,
        )
        auth_service = AuthService(
            user_repository=(
                self.repository
            ),
            profile_repository=None,
            password_hasher=(
                PasswordHasherStub()
            ),
            access_token_service=None,
            refresh_token_repository=None,
            refresh_token_service=None,
            activity_log_service=None,
        )

        with self.assertRaisesRegex(
            AuthenticationError,
            "pasif durumda",
        ):
            auth_service.login(
                "user@example.com",
                "password",
            )


if __name__ == "__main__":
    unittest.main()
