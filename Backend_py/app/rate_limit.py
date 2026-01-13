import redis
from fastapi import Request, HTTPException, status
import os


redis_host = os.getenv('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

async def rate_limit(request: Request):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    request_count = r.get(key)
    
    if request_count and int(request_count) > 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again in a minute."
        )
    
    pipe = r.pipeline()
    pipe.incr(key)
    if not request_count:
        pipe.expire(key, 60) # Expire in 60 seconds
    pipe.execute()