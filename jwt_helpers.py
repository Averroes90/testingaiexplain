# jwt_helpers.py
import jwt  # pip install pyjwt
import time
from settings import JWT_SECRET_KEY  # bool


def sign_cfg(extra: dict | None = None, ttl_sec: int = 60) -> str:
    payload = {"exp": int(time.time()) + ttl_sec}
    if extra:
        payload.update(extra)
    # ❱❱ use the validated JWT_SECRET, not a stray “secret” variable
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
