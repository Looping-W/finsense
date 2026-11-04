"""创建管理员。账号已存在时不覆盖密码，除非传入 --reset-password。"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from finsense_api import create_app
from finsense_api.auth.passwords import hash_password
from finsense_api.auth.validators import validate_password, validate_username
from finsense_api.errors import ApiError
from finsense_api.extensions import db
from finsense_api.models import User


def main() -> None:
    if not (ROOT / ".env").exists():
        raise SystemExit("还没有 api/.env。请先复制 api/.env.example，并运行 flask db upgrade。")

    reset = "--reset-password" in sys.argv
    try:
        username = validate_username(os.getenv("ADMIN_USERNAME", "admin"))
        password = os.getenv("ADMIN_PASSWORD", "")
        if not password:
            raise SystemExit("请在 api/.env 设置 ADMIN_PASSWORD。不会创建空密码管理员。")
        password = validate_password(password)
    except ApiError as exc:
        raise SystemExit(exc.message) from exc

    app = create_app()
    with app.app_context():
        try:
            existing = db.session.scalar(select(User).where(User.username == username))
        except SQLAlchemyError as exc:
            raise SystemExit(f"数据表还没准备好。请运行 flask db upgrade。\n{exc}") from exc

        if existing is None:
            db.session.add(
                User(
                    username=username,
                    password_hash=hash_password(password),
                    role="admin",
                    status="active",
                )
            )
            db.session.commit()
            print(f"已创建管理员 {username}。")
            return

        if existing.role != "admin":
            existing.role = "admin"
            db.session.commit()
            print(f"用户 {username} 已设为管理员。")

        if not reset:
            print(f"管理员 {username} 已存在，未修改密码。")
            return

        existing.password_hash = hash_password(password)
        db.session.commit()
        print(f"已重置管理员 {username} 的密码。")


if __name__ == "__main__":
    main()
