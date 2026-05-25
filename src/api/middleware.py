"""API middleware components."""

import time
import logging
import hashlib
import secrets
from typing import Callable, Dict, Optional, Set
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

_sessions: Dict[str, Dict] = {}
_revoked_tokens: Set[str] = set()
SESSION_TIMEOUT = 1800


def _hash_token(token: str) -> str:
    try:
        return hashlib.sha256(token.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Error in _hash_token: {e}")
        raise


def create_session(user_id: str, scopes: list[str]) -> tuple[str, str]:
    try:
        session_id = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(48)

        _sessions[session_id] = {
            "user_id": user_id,
            "refresh_token_hash": _hash_token(refresh_token),
            "created_at": time.time(),
            "last_rotated": time.time(),
            "scopes": scopes,
        }

        return session_id, refresh_token
    except Exception as e:
        logger.error(f"Error in create_session: {e}")
        raise


def rotate_refresh_token(
    session_id: str, old_refresh_token: str
) -> Optional[str]:
    try:
        session = _sessions.get(session_id)
        if not session:
            return None

        old_hash = _hash_token(old_refresh_token)

        if old_hash in _revoked_tokens:
            _sessions.pop(session_id, None)
            return None

        if session["refresh_token_hash"] != old_hash:
            return None

        if time.time() - session["last_rotated"] > SESSION_TIMEOUT:
            _sessions.pop(session_id, None)
            return None

        new_refresh_token = secrets.token_urlsafe(48)
        session["refresh_token_hash"] = _hash_token(new_refresh_token)
        session["last_rotated"] = time.time()

        return new_refresh_token
    except Exception as e:
        logger.error(f"Error in rotate_refresh_token: {e}")
        raise


def validate_session(
    session_id: str,
    required_scopes: Optional[list[str]] = None,
) -> Optional[str]:
    try:
        session = _sessions.get(session_id)
        if not session:
            return None

        if time.time() - session["last_rotated"] > SESSION_TIMEOUT:
            _sessions.pop(session_id, None)
            return None

        if required_scopes:
            session_scopes = set(session["scopes"])
            if not all(scope in session_scopes for scope in required_scopes):
                return None

        return session["user_id"]
    except Exception as e:
        logger.error(f"Error in validate_session: {e}")
        raise


def revoke_session(session_id: str) -> bool:
    try:
        session = _sessions.pop(session_id, None)
        if session:
            _revoked_tokens.add(session["refresh_token_hash"])
            return True
        return False
    except Exception as e:
        logger.error(f"Error in revoke_session: {e}")
        raise


def revoke_token(refresh_token: str) -> None:
    try:
        _revoked_tokens.add(_hash_token(refresh_token))
    except Exception as e:
        logger.error(f"Error in revoke_token: {e}")
        raise


def cleanup_expired_sessions() -> int:
    try:
        now = time.time()
        expired = [
            sid for sid, session in _sessions.items()
            if now - session["last_rotated"] > SESSION_TIMEOUT
        ]
        for sid in expired:
            session = _sessions.pop(sid)
            _revoked_tokens.add(session["refresh_token_hash"])
        return len(expired)
    except Exception as e:
        logger.error(f"Error in cleanup_expired_sessions: {e}")
        raise


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        try:
            path = request.url.path
            is_api = path.startswith("/api/v2")
            is_auth = path == "/api/v2/auth/token"

            if is_api and not is_auth:
                session_id = request.headers.get("X-Session-ID", "")
                if session_id:
                    user_id = validate_session(session_id)
                    if not user_id:
                        return Response(
                            status_code=401,
                            content="Unauthorized: invalid session",
                        )
                    request.state.user_id = user_id
                    request.state.auth_method = "session"
                    return await call_next(request)

                token = request.headers.get("Authorization", "")
                if not token.startswith("Bearer "):
                    return Response(
                        status_code=401,
                        content="Unauthorized: missing authorization",
                    )

                request.state.user_id = "api_user"
                request.state.auth_method = "token"

            return await call_next(request)
        except Exception as e:
            logger.error(f"Error in AuthMiddleware.dispatch: {e}")
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self._requests = {}

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        client_ip = (
            request.client.host if request.client else "unknown"
        )
        now = time.time()

        if client_ip not in self._requests:
            self._requests[client_ip] = []

        self._requests[client_ip] = [
            t for t in self._requests[client_ip]
            if now - t < self.window
        ]

        if len(self._requests[client_ip]) >= self.max_requests:
            return Response(
                status_code=429, content="Too many requests"
            )

        self._requests[client_ip].append(now)
        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(
            f"{request.method} {request.url.path} "
            f"{response.status_code} {duration:.3f}s"
        )
        return response

# 2019-03-01T18:35:19 update

# 2019-04-03T13:22:05 update

# 2019-04-30T17:18:49 update

# 2019-08-20T09:29:03 update

# 2019-08-30T15:52:06 update

# 2019-11-23T16:58:42 update

# 2020-02-18T10:04:07 update

# 2020-04-21T17:35:30 update

# 2020-05-22T11:10:34 update

# 2020-07-02T12:31:26 update

# 2020-07-05T13:52:59 update

# 2020-08-21T20:36:45 update

# 2021-01-19T09:17:15 update

# 2021-01-29T11:34:24 update

# 2021-02-04T15:21:21 update

# 2021-04-19T19:23:15 update

# 2021-05-20T16:50:15 update

# 2021-06-22T19:23:44 update

# 2021-09-09T13:44:55 update

# 2021-09-16T09:30:20 update

# 2021-10-14T20:42:33 update

# 2021-12-28T16:39:14 update

# 2022-01-26T19:07:27 update

# 2022-01-28T08:03:41 update

# 2022-03-23T12:17:02 update

# 2022-04-06T12:12:27 update

# 2022-04-21T14:53:01 update

# 2022-06-30T08:37:32 update

# 2022-07-06T10:44:45 update

# 2022-11-02T11:12:47 update

# 2022-11-15T20:54:21 update

# 2022-11-23T14:13:34 update

# 2023-01-26T10:03:44 update

# 2023-02-09T17:08:10 update

# 2023-02-16T10:04:00 update

# 2023-03-14T11:52:03 update

# 2023-04-10T12:42:07 update

# 2023-04-26T10:43:39 update

# 2023-06-27T08:18:07 update

# 2023-08-30T15:30:40 update

# 2023-08-30T14:10:05 update

# 2023-10-09T18:32:46 update

# 2023-11-21T20:35:55 update

# 2024-03-07T19:17:39 update

# 2024-04-01T18:06:19 update

# 2024-07-18T15:37:34 update

# 2024-07-25T09:21:53 update

# 2024-08-12T14:24:22 update

# 2024-11-18T08:50:54 update

# 2025-04-08T12:43:05 update

# 2025-06-03T08:10:47 update

# 2025-06-12T08:37:52 update

# 2025-06-17T08:36:56 update

# 2025-07-02T18:09:42 update

# 2025-07-22T12:39:21 update

# 2025-10-13T12:13:46 update

# 2025-12-05T09:44:22 update

# 2025-12-22T18:34:47 update

# 2026-01-26T15:36:23 update

# 2026-02-13T12:36:40 update

# 2026-02-26T11:07:15 update

# 2026-03-19T11:00:17 update

# 2026-03-27T12:58:53 update

# 2026-05-12T17:19:36 update
