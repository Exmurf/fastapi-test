from datetime import datetime, timedelta, timezone
import uuid

import jwt
from jwt.exceptions import InvalidTokenError

from app.application.security.access_token_service import (
    AccessTokenService,
    AccessTokenPayload,
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

    def decode_access_token(
        self,
        token: str,
    ) -> AccessTokenPayload | None:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms = [self._algorithm],
                options = {
                    "require": [
                        "sub",
                        "type",
                        "iat",
                        "exp",
                        "jti",
                    ]
                },
            )
        except InvalidTokenError:
            return None

        if payload.get("type") != "access":
            return None

        subject = payload.get("sub")
        token_id = payload.get("jti")

        if not isinstance(subject,str) or not subject:
            return None

        if not isinstance(token_id, str) or not token_id:
            return None

        return AccessTokenPayload(
            subject=subject,
            token_id=token_id,
        )

    @property
    def expires_in_seconds(self) -> int:
        return self._expire_minutes * 60