"""创建 finsense 数据库。表由 Flask-Migrate 建立。"""

import sys
from pathlib import Path

import pymysql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from finsense_api.config import load_config


def main() -> None:
    if not (ROOT / ".env").exists():
        raise SystemExit("还没有 api/.env。请先复制 api/.env.example 为 api/.env，并填入 MySQL 账号。")

    config = load_config()
    if config.mysql_database != "finsense":
        raise SystemExit("MYSQL_DATABASE 必须是 finsense。")

    try:
        conn = pymysql.connect(
            host=config.mysql_host,
            port=config.mysql_port,
            user=config.mysql_user,
            password=config.mysql_password,
            charset="utf8mb4",
            autocommit=True,
        )
    except pymysql.err.OperationalError as exc:
        raise SystemExit(
            "无法连接 MySQL。请检查 api/.env 里的 MYSQL_USER 和 MYSQL_PASSWORD。"
            f"\n{exc.args[1] if len(exc.args) > 1 else exc}"
        ) from exc

    try:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE DATABASE IF NOT EXISTS finsense "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        conn.close()

    print("数据库 finsense 已就绪。")
    print("下一步：flask db upgrade，然后 python scripts/seed_admin.py。")
    print("如果五张表已经存在，改为 flask db stamp head，不要重复建表。")


if __name__ == "__main__":
    main()
