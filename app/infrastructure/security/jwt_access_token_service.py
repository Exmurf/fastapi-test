from datetime import datetime, timedelta, timezone
import uuid

import jwt

from app.application.security.access_token_service import (
    AccessTokenService,
)


class JWTAccessTokenService(AccessTokenService):
    def __init__(
        self,
        secret_key:str,
        algorithm: str,
        expire_minutes: int,
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(
        self,
        subject: str,
    ) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(
            minutes = self._expire_minutes
        )

        payload = {
            "sub": subject,
            "type": "access",
            "iat": now,
            "exp": expires_at,
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm= self._algorithm,
        )

    @property
    def expires_in_seconds(self) -> int:
        return self._expire_minutes * 60