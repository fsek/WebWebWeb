from fastapi import HTTPException, Request, status, Depends
import redis

from database import get_redis

RATE_LIMIT = 10  # max calls
WINDOW_SECONDS = 300  # per 5 minutes


async def rate_limit(
    request: Request,
    redis: redis.Redis = Depends(get_redis),
):

    client_signature = request.client.host

    print(client_signature)

    key = f"rate:{client_signature}:{request.url.path}"

    count = await redis.incr(key)

    if count == 1:
        await redis.expire(key, WINDOW_SECONDS)

    if count > RATE_LIMIT:
        ttl = await redis.ttl(key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Rate limit exceeded. Try again in {ttl} seconds."
        )
