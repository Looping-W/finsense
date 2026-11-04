"""建出 users、categories、transactions、budgets、ai_calls。

已有这五张表的库不要执行 upgrade，用 flask db stamp head 盖章。

Revision ID: b7e4c1a09d32
Revises:
Create Date: 2026-11-03
"""

from alembic import op

revision = "b7e4c1a09d32"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE users (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
          username VARCHAR(32) NOT NULL,
          password_hash VARCHAR(255) NOT NULL,
          role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
          status ENUM('active', 'disabled') NOT NULL DEFAULT 'active',
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (id),
          UNIQUE KEY uk_users_username (username)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    op.execute(
        """
        CREATE TABLE categories (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
          name VARCHAR(32) NOT NULL,
          type ENUM('income', 'expense') NOT NULL,
          user_id BIGINT UNSIGNED NULL,
          is_default TINYINT(1) NOT NULL DEFAULT 0,
          PRIMARY KEY (id),
          KEY idx_categories_user (user_id, type),
          CONSTRAINT fk_categories_user FOREIGN KEY (user_id) REFERENCES users (id),
          CONSTRAINT chk_categories_owner CHECK (
            (is_default = 1 AND user_id IS NULL)
            OR (is_default = 0 AND user_id IS NOT NULL)
          )
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    op.execute(
        """
        CREATE TABLE transactions (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
          user_id BIGINT UNSIGNED NOT NULL,
          category_id BIGINT UNSIGNED NOT NULL,
          amount DECIMAL(12, 2) NOT NULL,
          type ENUM('income', 'expense') NOT NULL,
          trade_date DATE NOT NULL,
          note VARCHAR(200) NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (id),
          KEY idx_transactions_user_date (user_id, trade_date),
          CONSTRAINT fk_transactions_user FOREIGN KEY (user_id) REFERENCES users (id),
          CONSTRAINT fk_transactions_category FOREIGN KEY (category_id) REFERENCES categories (id),
          CONSTRAINT chk_transactions_amount CHECK (amount > 0)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    op.execute(
        """
        CREATE TABLE budgets (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
          user_id BIGINT UNSIGNED NOT NULL,
          `month` CHAR(7) NOT NULL,
          amount DECIMAL(12, 2) NOT NULL,
          category_id BIGINT UNSIGNED NULL,
          category_key BIGINT UNSIGNED AS (IFNULL(category_id, 0)) STORED,
          PRIMARY KEY (id),
          UNIQUE KEY uk_budgets_scope (user_id, `month`, category_key),
          CONSTRAINT fk_budgets_user FOREIGN KEY (user_id) REFERENCES users (id),
          CONSTRAINT fk_budgets_category FOREIGN KEY (category_id) REFERENCES categories (id),
          CONSTRAINT chk_budgets_amount CHECK (amount > 0),
          CONSTRAINT chk_budgets_month CHECK (`month` REGEXP '^[0-9]{4}-[0-9]{2}$')
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    op.execute(
        """
        CREATE TABLE ai_calls (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
          user_id BIGINT UNSIGNED NOT NULL,
          feature_type ENUM('insight', 'forecast', 'qa') NOT NULL,
          question VARCHAR(500) NULL,
          tokens INT UNSIGNED NULL,
          status ENUM('success', 'error') NOT NULL,
          latency_ms INT UNSIGNED NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (id),
          KEY idx_ai_calls_user_feature (user_id, feature_type, created_at),
          KEY idx_ai_calls_created (created_at),
          CONSTRAINT fk_ai_calls_user FOREIGN KEY (user_id) REFERENCES users (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS ai_calls")
    op.execute("DROP TABLE IF EXISTS budgets")
    op.execute("DROP TABLE IF EXISTS transactions")
    op.execute("DROP TABLE IF EXISTS categories")
    op.execute("DROP TABLE IF EXISTS users")
