import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings


class SQLValidationError(ValueError):
    pass


_FORBIDDEN_KEYWORDS = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "MERGE",
    "GRANT",
    "REVOKE",
    "EXECUTE",
    "CALL",
    "COPY",
    "VACUUM",
    "ANALYZE",
    "REINDEX",
    "CLUSTER",
    "REFRESH",
    "LISTEN",
    "NOTIFY",
    "LOAD",
}

_SYSTEM_SCHEMAS = {
    "information_schema",
    "pg_catalog",
    "pg_toast",
}

_DANGEROUS_FUNCTIONS = {
    "PG_READ_FILE",
    "PG_READ_BINARY_FILE",
    "PG_SLEEP",
    "PG_TERMINATE_BACKEND",
    "LO_IMPORT",
    "LO_EXPORT",
    "LO_GET",
    "LO_PUT",
    "PG_LS_DIR",
}


def _strip_wrapping(sql: str) -> str:
    cleaned = sql.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:sql)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def _remove_comments(sql: str) -> str:
    sql = re.sub(r"/\*[\s\S]*?\*/", " ", sql)
    sql = re.sub(r"--[^\n]*", " ", sql)
    return sql


def _tokenize(sql: str) -> list[tuple[str, str, int, int]]:
    pattern = re.compile(
        r"""
        (?P<string>'(?:''|\\'|[^'])*') |
        (?P<quoted_ident>"(?:""|\\"|[^"])*") |
        (?P<number>\b\d+\.?\d*\b) |
        (?P<word>\b[a-zA-Z_][a-zA-Z0-9_]*\b) |
        (?P<operator>[;,.()+\-*/=<>:!]+) |
        (?P<whitespace>\s+)
        """,
        re.VERBOSE,
    )

    tokens: list[tuple[str, str, int, int]] = []
    for match in pattern.finditer(sql):
        kind = match.lastgroup
        if kind == "whitespace":
            continue
        tokens.append((kind, match.group(), match.start(), match.end()))
    return tokens


def _unquote_identifier(quoted: str) -> str:
    if len(quoted) >= 2 and quoted.startswith('"') and quoted.endswith('"'):
        return quoted[1:-1].replace('""', '"')
    return quoted


def _first_word_token(tokens: list[tuple[str, str, int, int]]) -> str | None:
    for kind, value, _, _ in tokens:
        if kind == "word":
            return value.upper()
    return None


def _apply_row_limit(sql: str, max_rows: int) -> str:
    cleaned = sql.rstrip().rstrip(";").strip()
    tokens = _tokenize(cleaned)

    for i, (kind, value, start, end) in enumerate(tokens):
        if (
            kind == "word"
            and value.upper() == "LIMIT"
            and i + 1 < len(tokens)
            and tokens[i + 1][0] == "number"
        ):
            n = int(float(tokens[i + 1][1]))
            limit_start, limit_end = tokens[i + 1][2], tokens[i + 1][3]
            if n > max_rows:
                return cleaned[:limit_start] + str(max_rows) + cleaned[limit_end:]
            return cleaned

    return f"{cleaned} LIMIT {max_rows}"


def validate_sql(sql: str, max_rows: int | None = None) -> str:
    if max_rows is None:
        max_rows = settings.max_query_rows

    cleaned = _strip_wrapping(sql).strip()
    if not cleaned:
        raise SQLValidationError("Generated SQL is empty")

    no_comments = _remove_comments(cleaned)
    tokens = _tokenize(no_comments)

    if not tokens:
        raise SQLValidationError("Generated SQL is empty after removing comments")

    for kind, value, _, _ in tokens:
        if kind == "operator" and ";" in value:
            raise SQLValidationError("Multiple SQL statements are not allowed")

    first_word = _first_word_token(tokens)
    if first_word != "SELECT":
        raise SQLValidationError("Only SELECT queries are allowed")

    for kind, value, _, _ in tokens:
        if kind == "word":
            upper_value = value.upper()
            if upper_value in _FORBIDDEN_KEYWORDS:
                raise SQLValidationError(f"Forbidden SQL keyword detected: {value}")

            if value.lower() in _SYSTEM_SCHEMAS:
                raise SQLValidationError(
                    f"Access to system schema is not allowed: {value}"
                )

            if upper_value in _DANGEROUS_FUNCTIONS:
                raise SQLValidationError(f"Dangerous function is not allowed: {value}")

        elif kind == "quoted_ident":
            unquoted = _unquote_identifier(value).lower()
            if unquoted in _SYSTEM_SCHEMAS:
                raise SQLValidationError(
                    f"Access to system schema is not allowed: {value}"
                )

    return _apply_row_limit(no_comments, max_rows)
