import os
import redis
from pathlib import Path
import jwt, time

STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "storage/docs")).resolve()
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_cli = redis.from_url(REDIS_URL, decode_responses=True)

USE_JWT = os.getenv("USE_JWT", "true").lower() == "true"


def _get_secret() -> str:
    """Return JWT_SECRET from env as a *str* or raise."""
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is missing or empty. Check compose env.")
    # If someone later sets it as bytes, convert once here
    if isinstance(secret, bytes):
        secret = secret.decode()
    if not isinstance(secret, str):
        raise TypeError(f"JWT_SECRET must be str, got {type(secret)}")

    # Ensure the secret has a minimum length (OnlyOffice might require this)
    if len(secret) < 32:
        print(
            "Warning: JWT_SECRET is shorter than recommended. Consider using at least 32 characters."
        )

    return secret


JWT_SECRET_KEY = _get_secret()


def sign_full(cfg: dict, ttl_sec: int = 60) -> str:
    # Create a copy of the config to avoid modifying the original
    jwt_payload = {
        # Required JWT fields
        "iss": "your_app_name",  # Issuer - optional but recommended
        "aud": "OnlyOffice",  # Audience - optional but recommended
        "iat": int(time.time()),
        "exp": int(time.time()) + ttl_sec,
        # OnlyOffice specific fields
        "document": cfg.get("document", {}),  # Document info under "doc" key
        "editorConfig": cfg.get("editorConfig", {}),
    }

    # Add any other fields that OnlyOffice expects

    token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm="HS256")

    # 1. bytes → str
    if isinstance(token, bytes):
        token = token.decode()

    # 2. remove any base64 padding (=) that DS dislikes
    token = ".".join(segment.rstrip("=") for segment in token.split("."))

    return token
