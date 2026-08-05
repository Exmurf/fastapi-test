from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GeneratedRefreshToken:
    raw_token: str
    token_hash: str
    expires_at: datetime


class RefreshTokenService(ABC):
    @abstractmethod
    def generate_refresh_token(
        self,
    ) -> GeneratedRefreshToken:
        pass

    @abstractmethod
    def hash_token(
        self,
        raw_token: str,
    ) -> str:
        pass