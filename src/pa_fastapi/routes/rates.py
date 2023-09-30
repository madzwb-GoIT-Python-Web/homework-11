import os
from dotenv import load_dotenv
from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from starlette.requests import Request
from starlette.responses import Response

load_dotenv()
_ratelimiter = os.environ.get("FASTAPI_RATELIMITER")
if _ratelimiter:
    ratelimiter = int(_ratelimiter)
else:
    ratelimiter = False
if not ratelimiter:
    class RateLimiter(RateLimiter):
        async def __call__(self, request: Request, response: Response):
            return

rate_create = Depends(RateLimiter(times=1, minutes=1))
rate_read   = Depends(RateLimiter(times=1, seconds=1))
rate_update = Depends(RateLimiter(times=1, minutes=1))
rate_delete = Depends(RateLimiter(times=1, minutes=1))
