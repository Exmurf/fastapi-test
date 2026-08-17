from sqlalchemy.orm import Session

from app.domain.entities.tag import Tag
from app.domain.repositories.tag_repository import (
    TagRepository,
)
from app.infrastructure.models.tag_model import (
    TagModel,
)


class SQLAlchemyTagRepository(
    TagRepository
):
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        tag: Tag,
    ) -> Tag:
        model = TagModel(
            name=tag.name,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._to_entity(
            model
        )

    def get_all(
        self,
    ) -> list[Tag]:
        models = (
            self.db.query(
                TagModel
            )
            .order_by(
                TagModel.name.asc()
            )
            .all()
        )

        return [
            self._to_entity(model)
            for model in models
        ]

    def get_by_name(
        self,
        name: str,
    ) -> Tag | None:
        model = (
            self.db.query(
                TagModel
            )
            .filter(
                TagModel.name == name
            )
            .first()
        )

        if model is None:
            return None

        return self._to_entity(
            model
        )

    def get_by_public_id(
        self,
        public_id: str,
    ) -> Tag | None:
        model = (
            self.db.query(
                TagModel
            )
            .filter(
                TagModel.public_id == public_id
            )
            .first()
        )

        if model is None:
            return None

        return self._to_entity(
            model
        )

    def get_by_names(
        self,
        names: list[str],
    ) -> list[Tag]:
        if not names:
            return []

        models = (
            self.db.query(
                TagModel
            )
            .filter(
                TagModel.name.in_(
                    names
                )
            )
            .all()
        )

        return [
            self._to_entity(model)
            for model in models
        ]

    def delete(
        self,
        tag: Tag,
    ) -> None:
        model = (
            self.db.query(
                TagModel
            )
            .filter(
                TagModel.public_id == tag.public_id
            )
            .first()
        )

        if model is None:
            return

        self.db.delete(model)
        self.db.commit()

    @staticmethod
    def _to_entity(
        model: TagModel,
    ) -> Tag:
        return Tag(
            id=model.id,
            public_id=model.public_id,
            name=model.name,
        )
