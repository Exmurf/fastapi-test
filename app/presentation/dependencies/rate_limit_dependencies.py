import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Depends, Request

from app.application.exceptions import RateLimitError
from app.domain.entities.user import User
from app.presentation.dependencies.auth_dependencies import (
    get_current_user,
)
from app.config import settings


LOGIN_LIMIT = settings.login_limit
LOGIN_WINDOW_SECONDS = settings.login_window_seconds

REGISTER_LIMIT = settings.register_limit
REGISTER_WINDOW_SECONDS = settings.register_window_seconds

PRODUCT_READ_LIMIT = settings.product_read_limit
PRODUCT_READ_WINDOW_SECONDS = (
    settings.product_read_window_seconds
)

PRODUCT_WRITE_LIMIT = settings.product_write_limit
PRODUCT_WRITE_WINDOW_SECONDS = (
    settings.product_write_window_seconds
)


_requests: dict[
    str,
    deque[float],
] = defaultdict(deque)

_lock = Lock()

def _check_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
) -> None:
    now = time.monotonic()
    window_start = now - window_seconds

    with _lock:
        timestamps = _requests[key]

        while(
            timestamps
            and timestamps[0] <= window_start
        ):
            timestamps.popleft()

        if len(timestamps) >= limit:
            retry_after = int(
                timestamps[0]
                + window_seconds
                - now
            ) + 1

            raise RateLimitError(
                message=(
                    "Cok fazla istek gonderildi"
                ),
                retry_after=retry_after,
            )

        timestamps.append(now)


def ip_rate_limit(
        bucket: str,
        limit: int,
        window_seconds: int,
):
    def dependency(
            request: Request,
    ) -> None:
        client_ip = (
            request.client.host
            if request.client is not None
            else "unknown"
        )

        key = f"{bucket}:ip:{client_ip}"

        _check_rate_limit(
            key=key,
            limit=limit,
            window_seconds=window_seconds,
        )

    return dependency


def user_rate_limit(
    bucket: str,
    limit: int,
    window_seconds: int,
):
    def dependency(
            current_user: User = Depends(get_current_user)
    ) -> None:
        if current_user.public_id is None:
            raise RuntimeError(
                "Kullanici public ID "
                "bulunamadi"
            )

        key = (
            f"{bucket}:user:"
            f"{current_user.public_id}"
        )

        _check_rate_limit(
            key=key,
            limit=limit,
            window_seconds=window_seconds,
        )

    return dependency