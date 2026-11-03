from datetime import datetime, timedelta, timezone

import jwt

from finsense_api.errors import ApiError


def issue_token(user_id: int, role: str, config) -> str:
    if not config.jwt_secret:
        raise ApiError(500, "服务缺少 JWT_SECRET")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": now + timedelta(days=config.jwt_expires_days),
    }
    return jwt.encode(payload, config.jwt_secret, algorithm="HS256")


def decode_token(token: str, config) -> dict:
    if not config.jwt_secret:
        raise ApiError(500, "服务缺少 JWT_SECRET")
    return jwt.decode(token, config.jwt_secret, algorithms=["HS256"])
