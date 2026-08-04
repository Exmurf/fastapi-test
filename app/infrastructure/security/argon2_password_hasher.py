from argon2 import PasswordHasher as Argon2LibraryHasher
from argon2.exceptions import(
    InvalidHashError,
    VerificationError,
)

from app.application.security.password_hasher import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    def __init__(self):
        self._hasher = Argon2LibraryHasher()

    def hash(self, plain_password: str) -> str:
        return self._hasher.hash(plain_password)

    def verify(
        self,
        plain_password: str,
        password_hash: str,
    ) -> bool:
        try:
            return self._hasher.verify(
                password_hash,
                plain_password,
            )
        except (VerificationError, InvalidHashError):
            return False