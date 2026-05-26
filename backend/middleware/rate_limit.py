"""
middleware/rate_limit.py
========================
Rate limiting using slowapi (token bucket, per IP).

Limits (matching skills blueprint):
  - Anonymous / no header:     10 requests / minute
  - Standard (any user):      100 requests / minute

Usage in a route:
    from middleware.rate_limit import limiter

    @router.get("/")
    @limiter.limit("100/minute")
    def my_endpoint(request: Request, ...):
        ...

Note: `request: Request` MUST be the first parameter when using @limiter.limit.
The limiter is attached to app.state in main.py.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Key function: identify callers by IP address.
# In production behind a reverse proxy, swap to:
#   get_remote_address  →  a function reading X-Forwarded-For
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
