from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from finsense_api.auth.guards import require_user
from finsense_api.auth.passwords import dummy_hash, hash_password, verify_password
from finsense_api.auth.tokens import issue_token
from finsense_api.auth.validators import parse_credentials
from finsense_api.db import commit_session, raise_db_unavailable
from finsense_api.errors import ApiError
from finsense_api.extensions import db
from finsense_api.models import User

bp = Blueprint("auth", __name__)

REGISTERED_ROLE = "user"


def public_user(user) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "status": user.status,
    }


def _user_by_username(username: str) -> User | None:
    try:
        return db.session.scalar(select(User).where(User.username == username))
    except SQLAlchemyError as exc:
        raise_db_unavailable(exc)


@bp.post("/register")
def register():
    username, password = parse_credentials(request.get_json(silent=True))
    user = User(
        username=username,
        password_hash=hash_password(password),
        role=REGISTERED_ROLE,
        status="active",
    )
    db.session.add(user)
    try:
        commit_session()
    except IntegrityError as exc:
        raise ApiError(409, "用户名已存在") from exc
    except SQLAlchemyError as exc:
        raise_db_unavailable(exc)
    return jsonify(id=user.id, username=user.username, role=user.role, status=user.status), 201


@bp.post("/login")
def login():
    username, password = parse_credentials(request.get_json(silent=True))
    user = _user_by_username(username)
    hashed = user.password_hash if user else dummy_hash()
    if user is None or not verify_password(hashed, password):
        raise ApiError(401, "用户名或密码错误")
    if user.status != "active":
        raise ApiError(403, "账号已禁用")
    token = issue_token(user.id, user.role, current_app.config["FINSENSE"])
    return jsonify(access_token=token, user=public_user(user))


@bp.post("/logout")
def logout():
    # 退出不把 JWT 写入黑名单。前端删掉 token 后，后续请求不再带凭证。
    require_user()
    return "", 204


@bp.get("/me")
def me():
    return jsonify(public_user(require_user()))
