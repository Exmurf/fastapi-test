from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.entities.refresh_token import RefreshToken
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.infrastructure.models.refresh_token_model import (
    RefreshTokenModel,
)



class SQLAlchemyRefreshTokenRepository(
    RefreshTokenRepository
):
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        refresh_token_model = RefreshTokenModel(
            user_id = refresh_token.user_id,
            token_hash = refresh_token.token_hash,
            expires_at = refresh_token.expires_at,
            created_at = refresh_token.created_at,
            revoked_at = refresh_token.revoked_at,
        )

        self.db.add(refresh_token_model)
        self.db.commit()
        self.db.refresh(refresh_token_model)

        return self._to_entity(
            refresh_token_model
        )

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        refresh_token_model = (
            self.db.query(RefreshTokenModel)
            .filter(
                RefreshTokenModel.token_hash
                == token_hash
            )
            .first()
        )

        if refresh_token_model is None:
            return None

        return self._to_entity(
            refresh_token_model
        )

    def revoke(
        self,
        token_hash: str
    ) -> bool:
        refresh_token_model = (
            self.db.query(RefreshTokenModel)
            .filter(
                RefreshTokenModel.token_hash
                == token_hash,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .first()
        )

        if refresh_token_model is None:
            return False

        refresh_token_model.revoked_at = (
            datetime.now(timezone.utc)
        )

        self.db.commit()

        return True

    @staticmethod
    def _to_entity(
        refresh_token_model: RefreshTokenModel,
    ) -> RefreshTokenModel:
        return RefreshToken(
            id = refresh_token_model.id,
            user_id = refresh_token_model.user_id,
            token_hash = refresh_token_model.token_hash,
            expires_at = refresh_token_model.expires_at,
            created_at = refresh_token_model.created_at,
            revoked_at = refresh_token_model.revoked_at,
        )