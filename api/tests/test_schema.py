from pathlib import Path

SCHEMA = (Path(__file__).resolve().parents[1] / "schema.sql").read_text(encoding="utf-8")


def test_schema_creates_database_and_tables():
    assert "CREATE DATABASE IF NOT EXISTS finsense" in SCHEMA
    for table in ("users", "categories", "transactions", "budgets", "ai_calls"):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in SCHEMA


def test_schema_keeps_money_exact():
    assert "DECIMAL(12, 2)" in SCHEMA
    assert "DOUBLE" not in SCHEMA.upper()
    assert "FLOAT" not in SCHEMA.upper()
