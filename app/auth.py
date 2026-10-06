"""API-key authentication dependency.

The key is read from the ``X-API-Key`` request header and compared against the
``API_KEY`` environment variable using a constant-time comparison.
"""

import hmac
import os
from typing import Optional

from fastapi import Header, HTTPException, status

# Development fallback so the demo works out of the box. Override it in
# production by setting the API_KEY environment variable (see .env.example).
DEV_API_KEY = "super30-secret-key"


def get_expected_api_key() -> str:
    return os.environ.get("API_KEY", DEV_API_KEY)


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> str:
    """Protect an endpoint.

    * No header  -> 401 Unauthorized (client did not authenticate at all).
    * Wrong key  -> 403 Forbidden (client authenticated, but is not allowed).
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide it in the 'X-API-Key' header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not hmac.compare_digest(x_api_key, get_expected_api_key()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    return x_api_key
