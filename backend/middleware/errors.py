"""
middleware/errors.py
====================
Centralised RFC 7807 Problem Details error handling.

All HTTP errors returned by this API follow the standard:
  {
    "type":     "https://naanstop.app/errors/<slug>",
    "title":    "Human-readable title",
    "status":   <http_code>,
    "detail":   "Specific explanation of this occurrence",
    "instance": "/api/v1/<path>"
  }

Registered in main.py via:
  app.add_exception_handler(HTTPException,            http_exception_handler)
  app.add_exception_handler(RequestValidationError,   validation_error_handler)
  app.add_exception_handler(Exception,               generic_error_handler)
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger("naanstop.errors")

# ── Slug map: HTTP status → problem type slug ─────────────────────────────────
_STATUS_SLUGS: dict[int, str] = {
    400: "bad-request",
    401: "unauthorized",
    403: "forbidden",
    404: "not-found",
    405: "method-not-allowed",
    409: "conflict",
    422: "validation-error",
    429: "rate-limit-exceeded",
    500: "internal-server-error",
}

_API_BASE = "https://naanstop.app/errors"


def _problem(status: int, title: str, detail: str, instance: str, **extra) -> dict:
    slug = _STATUS_SLUGS.get(status, "error")
    body = {
        "type": f"{_API_BASE}/{slug}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
    }
    body.update(extra)
    return body


# ── Handlers ──────────────────────────────────────────────────────────────────

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Converts FastAPI HTTPException → RFC 7807 Problem Details."""
    # If the caller already passed a dict as detail, merge it in
    if isinstance(exc.detail, dict):
        detail_str = exc.detail.pop("detail", str(exc.detail))
        extra = exc.detail
    else:
        detail_str = str(exc.detail)
        extra = {}

    # Build title from status
    titles = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        409: "Conflict",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
    }
    title = titles.get(exc.status_code, "HTTP Error")

    body = _problem(
        status=exc.status_code,
        title=title,
        detail=detail_str,
        instance=str(request.url.path),
        **extra,
    )

    if exc.status_code >= 500:
        logger.error("HTTP %s — %s — %s", exc.status_code, request.url, detail_str)
    else:
        logger.warning("HTTP %s — %s — %s", exc.status_code, request.url, detail_str)

    return JSONResponse(status_code=exc.status_code, content=body)


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Converts Pydantic RequestValidationError → RFC 7807 with per-field errors."""
    field_errors: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = " → ".join(str(p) for p in err["loc"] if p != "body")
        field_errors.setdefault(loc, []).append(err["msg"])

    body = _problem(
        status=422,
        title="Validation Error",
        detail="One or more request fields failed validation.",
        instance=str(request.url.path),
        errors=field_errors,
    )
    logger.warning("Validation error — %s — %s", request.url, field_errors)
    return JSONResponse(status_code=422, content=body)


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all: wraps unhandled exceptions so we never leak stack traces."""
    logger.exception("Unhandled exception — %s", request.url)
    body = _problem(
        status=500,
        title="Internal Server Error",
        detail="An unexpected error occurred. Please try again later.",
        instance=str(request.url.path),
    )
    return JSONResponse(status_code=500, content=body)
