def build_sql_prompt(database_schema: str, user_question: str) -> str:
    return f"""
You are a data analyst generating SQL for a PostgreSQL analytical database.

Database schema:
{database_schema}

User question:
{user_question}

Instructions:
- Generate PostgreSQL SELECT SQL only.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or database administration statements.
- Use only the tables and columns listed in the schema.
- Return only the SQL query, with no markdown, comments, or explanation.
""".strip()
