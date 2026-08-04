from abc import ABC, abstractmethod


class AccessTokenService(ABC):
    @abstractmethod
    def create_access_token(
        self,
        subject: str,
    ) -> str:
        pass

    @property
    @abstractmethod
    def expires_in_seconds(self) -> int:
        pass