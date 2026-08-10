from abc import ABC, abstractmethod

from app.domain.entities.profile import Profile


class ProfileRepository(ABC):
    @abstractmethod
    def create(
        self,
        profile: Profile,
    ) -> Profile:
        pass

    @abstractmethod
    def get_by_user_id(
        self,
        user_id: int,
    ) -> Profile | None:
        pass

    @abstractmethod
    def update(
        self,
        profile: Profile
    ) -> Profile | None:
        pass
    