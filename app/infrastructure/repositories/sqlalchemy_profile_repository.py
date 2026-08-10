from sqlalchemy.orm import Session

from app.domain.entities.profile import Profile
from app.domain.repositories.profile_repository import (
    ProfileRepository,
)
from app.infrastructure.models.profile_model import (
    ProfileModel,
)


class SQLAlchemyProfileRepository(ProfileRepository):
    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    def create(
        self,
        profile: Profile,
    ) -> Profile:
        profile_model = ProfileModel(
            user_id = profile.user_id,
            first_name = profile.first_name,
            last_name = profile.last_name,
            bio = profile.bio,
        )

        self.db.add(profile_model)
        self.db.commit()
        self.db.refresh(profile_model)

        return self._to_entity(
            profile_model
        )

    def get_by_user_id(
        self,
        user_id: int,
    ) -> Profile | None:
        profile_model = (
            self.db.query(ProfileModel)
            .filter(
                ProfileModel.user_id
                == user_id
            )
            .first()
        )

        if profile_model is None:
            return None

        return self._to_entity(profile_model)

    def update(
        self,
        profile: Profile,
    ) -> Profile | None:
        profile_model = (
            self.db.query(ProfileModel)
            .filter(
                ProfileModel.user_id
                == profile.user_id
            )
            .first()
        )

        if profile_model is None:
            return None

        profile_model.first_name = (
            profile.first_name
        )

        profile_model.last_name = (
            profile.last_name
        )

        profile_model.bio = (
            profile.bio
        )

        self.db.commit()
        self.db.refresh(profile_model)

        return self._to_entity(profile_model)


    @staticmethod
    def _to_entity(
        profile_model: ProfileModel,
    ) -> Profile:
        return Profile(
            id=profile_model.id,
            user_id=profile_model.user_id,
            first_name=profile_model.first_name,
            last_name=profile_model.last_name,
            bio=profile_model.bio,
        )