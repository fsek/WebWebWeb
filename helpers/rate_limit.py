import os
from fastapi import HTTPException, Request, status, Depends
import redis.asyncio as aioredis
from database import get_redis

DEFAULT_RATE_LIMIT = 5  # default max calls
DEFAULT_WINDOW = 300  # default window in seconds


def rate_limit(
    limit: int = DEFAULT_RATE_LIMIT,
    window_seconds: int = DEFAULT_WINDOW,
):

    async def _rate_limiter(
        request: Request,
        redis: aioredis.Redis = Depends(get_redis),
    ):
        if os.getenv("ENVIRONMENT") == "testing":
            return

        client_signature = request.client.host
        key = f"rate:{client_signature}:{request.url.path}"

        count = await redis.incr(key)
        if count == 1:
            # only on first call set the TTL
            await redis.expire(key, window_seconds)

        if count > limit:
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Rate limit exceeded. Try again in {ttl}s."
            )

    return _rate_limiter
