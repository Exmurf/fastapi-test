from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> str:
        pass

    @abstractmethod
    def verify(
        self,
        plain_password: str,
        password_hash: str,
    ) -> bool:
        pass