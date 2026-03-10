import os

from fastapi.security import OAuth2PasswordBearer



SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 1.0
REFRESH_TOKEN_EXPIRE_DAYS = 3.0
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="hello", auto_error=False)