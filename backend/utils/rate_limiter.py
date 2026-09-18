import time
import threading
import logging
from typing import Dict, List
from fastapi import Request, HTTPException, status
from config import settings

logger = logging.getLogger("satquery.utils.rate_limiter")


class RateLimiter:
    """
    Thread-safe in-memory sliding-window rate limiter for protecting endpoints from abuse.
    """
    def __init__(self, requests_per_minute: int = 10, window_seconds: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self._clients: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def _get_client_ip(self, request: Request) -> str:
        # Check X-Forwarded-For if behind a reverse proxy (e.g. Vercel/Nginx/Render)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def __call__(self, request: Request) -> None:
        now = time.time()
        client_ip = self._get_client_ip(request)

        with self._lock:
            # Clean up old timestamps outside the window
            timestamps = self._clients.get(client_ip, [])
            valid_timestamps = [ts for ts in timestamps if now - ts < self.window_seconds]

            if len(valid_timestamps) >= self.requests_per_minute:
                earliest_ts = valid_timestamps[0]
                retry_after = max(1, int(earliest_ts + self.window_seconds - now))
                logger.warning(f"Rate limit exceeded for IP {client_ip} on {request.url.path} (limit={self.requests_per_minute}/min).")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute allowed.",
                    headers={"Retry-After": str(retry_after)}
                )

            valid_timestamps.append(now)
            self._clients[client_ip] = valid_timestamps

    def reset(self) -> None:
        """Clear all rate limit tracking (useful for testing)."""
        with self._lock:
            self._clients.clear()


# Pre-configured route rate limiters
analyze_rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_ANALYZE_PER_MINUTE)
upload_rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_UPLOAD_PER_MINUTE)
