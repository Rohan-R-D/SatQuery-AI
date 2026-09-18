import secrets
import logging
from typing import Optional
from fastapi import Header, HTTPException, status, Security
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from config import settings

logger = logging.getLogger("satquery.api.deps")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_auth = HTTPBearer(auto_error=False)


def verify_admin_key(
    x_api_key: Optional[str] = Security(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_auth)
) -> bool:
    """
    Validates administrative API key for protected audit and execution endpoints.
    Uses constant-time comparison (secrets.compare_digest) to prevent timing attacks.
    If ADMIN_API_KEY is empty/unset in environment, allows open access for local development.
    """
    configured_key = settings.ADMIN_API_KEY
    if not configured_key:
        return True

    provided_key = None
    if x_api_key:
        provided_key = x_api_key
    elif bearer and bearer.credentials:
        provided_key = bearer.credentials

    if not provided_key or not secrets.compare_digest(provided_key, configured_key):
        logger.warning("Unauthorized access attempt to protected administrative/audit endpoint.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide a valid 'X-API-Key' or 'Authorization: Bearer <key>' header.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return True
