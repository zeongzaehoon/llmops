import logging

from fastapi import Depends
from jose import jwt, ExpiredSignatureError, JWTError

from utils.error import TokenError
from auth import SECRET_KEY, ALGORITHM, oauth2_scheme




def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    JWT 토큰 검증 후 사용자 ID 반환
    - 토큰이 없거나 유효하지 않으면 401 에러
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        if payload.get("type") == "access":
            identity = payload.get("sub")
            if not identity:
                raise TokenError()
            return identity
        else:
            raise TokenError()
    except Exception as e:
        logging.error(f"[auth.dependencies.get_current_user] 🔴 {e}")
        raise TokenError(e)


# 액세스 토큰 선택적 (일부 정보만 필요한 라우트용)
def get_optional_user(token: str = Depends(oauth2_scheme)):
    """
    JWT 토큰 선택적 검증 후 사용자 ID 반환
    - 토큰이 있으면 검증 후 ID 반환
    - 토큰이 없으면 None 반환
    """
    try:
        if not token:
            result = None
    
        else:    
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            if payload.get("type") == "access":
                identity = payload.get("sub")
                result = identity
            else:
                result = None
    
        return result 
    
    except ExpiredSignatureError as e:
        logging.info(f"[auth.dependencies.get_optional_user] 🔴 {e}")
        raise TokenError(e)
    except JWTError as e:
        logging.info(f"[auth.dependencies.get_optional_user] 🔴 {e}")
        raise TokenError(e)
    except Exception as e:
        logging.error(f"[auth.dependencies.get_optional_user] 🔴 {e}")
        raise TokenError(e)


# 리프레시 토큰 필수 (토큰 갱신용)
def get_refresh_user(token: str = Depends(oauth2_scheme)):
    """
    리프레시 토큰 검증 후 사용자 ID 반환
    - 리프레시 토큰이 없거나 유효하지 않으면 401 에러
    """
    try:
        if not token:
            result = None
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        if payload.get("type") == "refresh":
            identity = payload.get("sub")
            result = identity
        else:
            result = None
    
        return result 
    
    except Exception as e:
        logging.info(f"[auth.dependencies.get_refresh_user] 🔴 {e}")
        raise TokenError(e)