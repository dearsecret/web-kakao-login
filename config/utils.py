from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed
from jwt import ExpiredSignatureError, DecodeError
from datetime import datetime , timezone , timedelta
from .settings import SECRET_KEY
import uuid , jwt

ALGORITHM = "HS256"

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("유효하지 않은 토큰입니다.")

def validate_access_token(token: str):
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AuthenticationFailed("Access 토큰이 아닙니다.")
    return payload


def create_access_token(user_id: str, expires_minutes: int = 30) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "pk": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "type": "access",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(user_id: str, token_id: str = None, expires_days: int = 14):
    now = datetime.now(timezone.utc)
    token_id = token_id or str(uuid.uuid4())
    payload = {
        "jti": token_id,  # 토큰 고유 식별자
        "pk": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=expires_days)).timestamp()),
        "type": "refresh",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, token_id



def create_state_token_with_cache(url: str, expire_minutes=5) -> str:
    state_uuid = str(uuid.uuid4())
    payload = {
        "uuid": state_uuid,
        "url": url,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    cache.set(state_uuid, {"url": url}, timeout=expire_minutes * 60)
    return token

def verify_state_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except (ExpiredSignatureError, DecodeError):
        return None
    uuid_val = payload.get("uuid")
    url_val = payload.get("url")
    if not uuid_val or not url_val:
        return None
    cached = cache.get(uuid_val)
    if not cached:
        return None
    cache.delete(uuid_val)
    return url_val