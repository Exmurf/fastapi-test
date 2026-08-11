import json
import time
from http import HTTPStatus

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.infrastructure.logging.error_logger import (
    error_logger,
)


SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "access_token",
    "refresh_token",
    "token",
    "authorization",
    "jwt_secret_key",
    "secret",
    "api_key",
}


def _sanitize(value):
    if isinstance(value, dict):
        result = {}

        for key, item in value.items():
            if key.lower() in SENSITIVE_FIELDS:
                result[key] = "***"
                continue

            result[key] = _sanitize(item)

        return result

    if isinstance(value, list):
        return [
            _sanitize(item)
            for item in value
        ]

    return value


class ErrorLoggingMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        started_at = time.perf_counter()

        body = await self._get_request_body(
            request
        )

        try:
            response = await call_next(
                request
            )

        except Exception as exc:
            duration_ms = (
                time.perf_counter()
                - started_at
            ) * 1000

            message = self._build_message(
                request=request,
                status_code=500,
                body=body,
                duration_ms=duration_ms,
                error=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

            error_logger.exception(message)

            raise

        duration_ms = (
        time.perf_counter()
        - started_at
        ) * 1000

        if response.status_code >= 400:
            message = self._build_message(
                request=request,
                status_code=(
                    response.status_code
                ),
                body=body,
                duration_ms=duration_ms,
            )

            if response.status_code >= 500:
                error_logger.error(
                    message
                )
            else:
                error_logger.warning(message)

        return response

    @staticmethod
    async def _get_request_body(
        request: Request,
    ):
        if request.method not in {
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        }:
            return None

        content_type = request.headers.get(
            "content_type",
            "",
        )

        if(
            "application/json"
            not in content_type
        ):
            return None

        try:
            raw_body = await request.body()

            if not raw_body:
                return None

            data = json.loads(raw_body)

            return _sanitize(data)

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ): 
            return "<invalid-json>"

    @staticmethod
    def _build_message(
        request: Request,
        status_code: int,
        body,
        duration_ms: float,
        error: str | None = None,
    ) -> str:

        client_ip = (
            request.client.host
            if request.client is not None
            else "unknown"
        )

        try: 
            status_text = HTTPStatus(status_code).phrase
        except ValueError:
            status_text = "unknown"

        path = request.url.path

        if request.url.query:
            pth = (
                f"{path}?"
                f"{request.url.query}"
            )

        query_params = _sanitize(dict(request.query_params))
        path_params = _sanitize(dict(request.path_params))

        http_version = request.scope.get(
            "http_version",
            "1.1",
        )

        message = (
            f'{client_ip} '
            f'"{request.method} '
            f'{path} '
            f'HTTP/{http_version}" '
            f'{status_code} '
            f'{status_text} '
            f'query={json.dumps(query_params)} '
            f'path={json.dumps(path_params)} '
            f'body={json.dumps(body)} '
            f'duration_ms={duration_ms:.2f}'
        )

        if error is not None:
            message += (
                f' error="{error}"'
            )

        return message