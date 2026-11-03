import jwt
from flask import current_app, request
from sqlalchemy.exc import SQLAlchemyError

from finsense_api.auth.tokens import decode_token
from finsense_api.db import raise_db_unavailable
from finsense_api.errors import ApiError
from finsense_api.extensions import db
from finsense_api.models import User


def require_user() -> User:
    config = current_app.config["FINSENSE"]
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise ApiError(401, "未登录")
    token = header.removeprefix("Bearer ").strip()
    if not token:
        raise ApiError(401, "未登录")
    try:
        payload = decode_token(token, config)
        user_id = int(payload["sub"])
    except ApiError:
        raise
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise ApiError(401, "登录已失效")
    try:
        user = db.session.get(User, user_id)
    except SQLAlchemyError as exc:
        raise_db_unavailable(exc)
    if user is None or user.status != "active":
        raise ApiError(401, "账号不可用")
    return user
