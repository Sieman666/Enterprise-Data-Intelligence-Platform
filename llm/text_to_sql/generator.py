import logging

from llm.client import generate_text
from llm.prompts.sql_prompt import build_sql_prompt
from llm.text_to_sql.schema import get_database_schema
from llm.text_to_sql.validator import validate_sql

logger = logging.getLogger(__name__)


def generate_sql(question: str) -> str:
    database_schema = get_database_schema()
    prompt = build_sql_prompt(database_schema=database_schema, user_question=question)
    generated = generate_text(
        prompt,
        system_prompt="You generate safe PostgreSQL SELECT queries for enterprise analytics.",
    )
    sql = validate_sql(generated)
    logger.info("Generated validated SQL for question: %s", question)
    return sql
