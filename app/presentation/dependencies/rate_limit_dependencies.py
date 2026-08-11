import time
import uuid

from fastapi import Depends, Request

from app.infrastructure.redis_client import redis_client
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


RATE_LIMIT_SCRIPT = redis_client.register_script(
    """
    local key = KEYS[1]

    local now = tonumber(ARGV[1])
    local window_start = tonumber(ARGV[2])
    local window_seconds = tonumber(ARGV[3])
    local limit = tonumber(ARGV[4])
    local member = ARGV[5]

    redis.call(
        "ZREMRANGEBYSCORE",
        key,
        "-inf",
        window_start
    )

    local request_count = redis.call(
        "ZCARD",
        key
    )

    if request_count >= limit then
        local oldest = redis.call(
            "ZRANGE",
            key,
            0,
            0,
            "WITHSCORES"
        )

        local retry_after = math.ceil(
            tonumber(oldest[2])
            + window_seconds
            - now
        )

        if retry_after < 1 then
            retry_after = 1
        end

        return {
            0,
            retry_after
        }
    end

    redis.call(
        "ZADD",
        key,
        now,
        member
    )

    redis.call(
        "EXPIRE",
        key,
        window_seconds + 1
    )

    return {
        1,
        0
    }
    """
)

def _check_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
) -> None:
    now = time.time()
    window_start = now - window_seconds

    member = uuid.uuid4().hex

    result = RATE_LIMIT_SCRIPT(
        keys=[key],
        args=[
            now,
            window_start,
            window_seconds,
            limit,
            member,
        ],
    )

    allowed = result[0] == 1

    if not allowed:
        retry_after = int(result[1])

        raise RateLimitError(
            message="Cok fazla istek gonderildi",
            retry_after=retry_after,
        )

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