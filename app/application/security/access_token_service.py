from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AccessTokenPayload:
    subject: str
    token_id: str

class AccessTokenService(ABC):
    @abstractmethod
    def create_access_token(
        self,
        subject: str,
    ) -> str:
        pass

    @abstractmethod
    def decode_access_token(
        self,
        token: str,
    ) -> AccessTokenPayload | None:
        pass

    @property
    @abstractmethod
    def expires_in_seconds(self) -> int:
        pass

