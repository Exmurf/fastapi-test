from abc import ABC, abstractmethod

from app.domain.entities.refresh_token import RefreshToken



class RefreshTokenRepository(ABC):
    @abstractmethod
    def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        pass

    @abstractmethod
    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        pass

    @abstractmethod
    def revoke(
        self,
        token_hash: str,
    ) -> bool:
        pass
    