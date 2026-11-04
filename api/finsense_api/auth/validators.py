import re

from finsense_api.errors import ApiError

USERNAME_RE = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fff]{2,32}$")


def validate_username(username) -> str:
    if not isinstance(username, str):
        raise ApiError(400, "请填写用户名和密码")
    username = username.strip()
    if USERNAME_RE.fullmatch(username) is None:
        raise ApiError(400, "用户名需要 2–32 位，只能包含字母、数字、下划线或中文")
    return username


def validate_password(password) -> str:
    if not isinstance(password, str) or password == "":
        raise ApiError(400, "请填写用户名和密码")
    if len(password) > 64:
        raise ApiError(400, "密码最长 64 位")
    return password


def parse_credentials(payload) -> tuple[str, str]:
    if not isinstance(payload, dict):
        raise ApiError(400, "请求格式不正确")
    return validate_username(payload.get("username")), validate_password(payload.get("password"))
