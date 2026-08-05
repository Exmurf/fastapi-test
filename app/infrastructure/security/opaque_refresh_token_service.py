import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.application.security.refresh_token_service import (
    GeneratedRefreshToken,
    RefreshTokenService,
)


class OpaqueRefreshTokenService(
    RefreshTokenService
):
    def __init__(
        self,
        expire_days: int,
    ):
        self._expire_days = expire_days

    def generate_refresh_token(
        self,
    ) -> GeneratedRefreshToken:
        raw_token = secrets.token_urlsafe(64)

        token_hash = self.hash_token(
            raw_token
        )

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                days=self._expire_days
            )
        )

        return GeneratedRefreshToken(
            raw_token = raw_token,
            token_hash = token_hash,
            expires_at = expires_at,
        )

    def hash_token(
        self,
        raw_token: str,
    ) -> str:
        return hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()