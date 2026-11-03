"""五张表的 SQLAlchemy 模型。

查询由 SQLAlchemy 生成，连接仍交给 PyMySQL。金额列用 Numeric，读出来是 Decimal。
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Computed, ForeignKey, Index, UniqueConstraint, text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column

from finsense_api.extensions import db


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username", name="uk_users_username"),)

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(mysql.VARCHAR(32))
    password_hash: Mapped[str] = mapped_column(mysql.VARCHAR(255))
    role: Mapped[str] = mapped_column(
        mysql.ENUM("user", "admin"),
        default="user",
        server_default="user",
    )
    status: Mapped[str] = mapped_column(
        mysql.ENUM("active", "disabled"),
        default="active",
        server_default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        mysql.DATETIME,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint(
            "(is_default = 1 AND user_id IS NULL) OR (is_default = 0 AND user_id IS NOT NULL)",
            name="chk_categories_owner",
        ),
        Index("idx_categories_user", "user_id", "type"),
    )

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(mysql.VARCHAR(32))
    type: Mapped[str] = mapped_column(mysql.ENUM("income", "expense"))
    user_id: Mapped[int | None] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_categories_user"),
    )
    is_default: Mapped[int] = mapped_column(mysql.TINYINT(1), default=0, server_default=text("0"))


class Transaction(db.Model):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_transactions_amount"),
        Index("idx_transactions_user_date", "user_id", "trade_date"),
    )

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_transactions_user"),
    )
    category_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("categories.id", name="fk_transactions_category"),
    )
    amount: Mapped[Decimal] = mapped_column(mysql.DECIMAL(12, 2))
    type: Mapped[str] = mapped_column(mysql.ENUM("income", "expense"))
    trade_date: Mapped[date] = mapped_column(mysql.DATE)
    note: Mapped[str | None] = mapped_column(mysql.VARCHAR(200))
    created_at: Mapped[datetime] = mapped_column(
        mysql.DATETIME,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class Budget(db.Model):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("user_id", "month", "category_key", name="uk_budgets_scope"),
        CheckConstraint("amount > 0", name="chk_budgets_amount"),
        CheckConstraint("`month` REGEXP '^[0-9]{4}-[0-9]{2}$'", name="chk_budgets_month"),
    )

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_budgets_user"),
    )
    month: Mapped[str] = mapped_column("month", mysql.CHAR(7))
    amount: Mapped[Decimal] = mapped_column(mysql.DECIMAL(12, 2))
    category_id: Mapped[int | None] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("categories.id", name="fk_budgets_category"),
    )
    # 空分类表示月度总预算。MySQL 唯一索引不把多个 NULL 视为重复，所以用生成列收成 0。
    category_key: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        Computed("IFNULL(category_id, 0)", persisted=True),
    )


class AiCall(db.Model):
    __tablename__ = "ai_calls"
    __table_args__ = (
        Index("idx_ai_calls_user_feature", "user_id", "feature_type", "created_at"),
        Index("idx_ai_calls_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_ai_calls_user"),
    )
    feature_type: Mapped[str] = mapped_column(mysql.ENUM("insight", "forecast", "qa"))
    question: Mapped[str | None] = mapped_column(mysql.VARCHAR(500))
    tokens: Mapped[int | None] = mapped_column(mysql.INTEGER(unsigned=True))
    status: Mapped[str] = mapped_column(mysql.ENUM("success", "error"))
    latency_ms: Mapped[int | None] = mapped_column(mysql.INTEGER(unsigned=True))
    created_at: Mapped[datetime] = mapped_column(
        mysql.DATETIME,
        server_default=text("CURRENT_TIMESTAMP"),
    )
