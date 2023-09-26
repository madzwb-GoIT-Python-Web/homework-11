from fastapi import Depends
from fastapi_limiter.depends import RateLimiter

rate_creatw = Depends(RateLimiter(times=1, minutes=1))
rate_read   = Depends(RateLimiter(times=1, seconds=1))
rate_update = Depends(RateLimiter(times=1, minutes=1))
rate_delete = Depends(RateLimiter(times=1, minutes=1))
