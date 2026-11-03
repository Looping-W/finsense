import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from finsense_api.errors import ApiError
from finsense_api.extensions import db

logger = logging.getLogger(__name__)

DB_NOT_READY = "数据表还没准备好。请先运行 python scripts/init_db.py，再运行 flask db upgrade。"


def database_status() -> str:
    try:
        db.session.execute(text("SELECT 1"))
        return "ok"
    except SQLAlchemyError as exc:
        db.session.rollback()
        logger.warning("database unavailable: %s", exc)
        return "unavailable"


def commit_session() -> None:
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise


def raise_db_unavailable(exc: SQLAlchemyError) -> None:
    db.session.rollback()
    logger.warning("database query failed: %s", exc)
    raise ApiError(503, DB_NOT_READY) from exc
