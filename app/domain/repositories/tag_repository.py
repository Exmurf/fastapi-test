from abc import ABC, abstractmethod

from app.domain.entities.tag import Tag


class TagRepository(ABC):
    @abstractmethod
    def create(
        self,
        tag: Tag,
    ) -> Tag:
        pass

    @abstractmethod
    def get_all(
        self,
    ) -> list[Tag]:
        pass

    @abstractmethod
    def get_by_name(
        self,
        name: str,
    ) -> Tag | None:
        pass

    @abstractmethod
    def get_by_names(
        self,
        names: list[str],
    ) -> list[Tag]:
        pass
