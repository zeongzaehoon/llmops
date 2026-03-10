from datetime import datetime, timedelta, timezone

from jose import jwt

from auth import *



def create_token(sub: str):
    def _create_token(sub: str, expires_delta: timedelta, type: str):
        to_encode = {"sub": sub, "exp": datetime.now(timezone.utc) + expires_delta, "type": type}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    access_token = _create_token(sub, timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS), "access")
    refresh_token = _create_token(sub, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh")
    return access_token, refresh_token