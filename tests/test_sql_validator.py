import pytest

from llm.text_to_sql.validator import SQLValidationError, validate_sql


def test_validate_sql_allows_select():
    sql = validate_sql("SELECT id, total_amount FROM orders")

    assert sql == "SELECT id, total_amount FROM orders LIMIT 1000"


def test_validate_sql_preserves_existing_limit():
    sql = validate_sql("SELECT * FROM orders LIMIT 100")

    assert sql == "SELECT * FROM orders LIMIT 100"


def test_validate_sql_caps_excessive_limit():
    sql = validate_sql("SELECT * FROM orders LIMIT 9999")

    assert sql == "SELECT * FROM orders LIMIT 1000"


def test_validate_sql_strips_markdown_wrapping():
    sql = validate_sql("```sql\nSELECT * FROM orders\n```")

    assert sql == "SELECT * FROM orders LIMIT 1000"


def test_validate_sql_rejects_empty_sql():
    with pytest.raises(SQLValidationError, match="empty"):
        validate_sql("")


def test_validate_sql_rejects_non_select():
    with pytest.raises(SQLValidationError, match="Only SELECT queries"):
        validate_sql("SHOW TABLES")


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE orders",
        "DELETE FROM orders",
        "UPDATE orders SET total_amount = 0",
        "INSERT INTO orders (id) VALUES (1)",
        "ALTER TABLE orders ADD COLUMN test TEXT",
        "CREATE TABLE temp (id INT)",
        "TRUNCATE TABLE orders",
        "GRANT SELECT ON orders TO public",
        "REVOKE SELECT ON orders FROM public",
        "COPY orders TO '/tmp/data.csv'",
        "VACUUM orders",
    ],
)
def test_validate_sql_rejects_unsafe_statements(sql):
    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_validate_sql_rejects_multiple_statements():
    with pytest.raises(SQLValidationError, match="Multiple SQL"):
        validate_sql("SELECT * FROM orders; SELECT * FROM customers")


def test_validate_sql_rejects_system_schema():
    with pytest.raises(SQLValidationError, match="system schema"):
        validate_sql("SELECT * FROM information_schema.tables")


def test_validate_sql_rejects_quoted_system_schema():
    with pytest.raises(SQLValidationError, match="system schema"):
        validate_sql('SELECT * FROM "information_schema"."tables"')


def test_validate_sql_rejects_dangerous_function():
    with pytest.raises(SQLValidationError, match="Dangerous function"):
        validate_sql("SELECT pg_sleep(10)")


def test_validate_sql_ignores_keywords_inside_string_literals():
    sql = validate_sql("SELECT * FROM orders WHERE notes = 'DROP TABLE orders'")

    assert sql == "SELECT * FROM orders WHERE notes = 'DROP TABLE orders' LIMIT 1000"


def test_validate_sql_strips_comments_with_forbidden_keywords():
    sql = validate_sql("SELECT * FROM orders /* DELETE FROM customers */")

    assert sql == "SELECT * FROM orders LIMIT 1000"
