# Enterprise Data Intelligence Platform

A backend service for AI-driven business analytics over structured operational data. It combines FastAPI, PostgreSQL, pandas-based ETL, automated analytics reporting, and LLM-powered Text-to-SQL with business insight generation.

## Features

- FastAPI backend with health, natural language query, and analytics report endpoints
- PostgreSQL analytical database with SQLAlchemy ORM models
- Ecommerce-style schema for customers, products, orders, and user behavior
- CSV sample data generator
- ETL pipeline with load, clean, validate, transform, and insert steps
- Idempotent ETL mode (`--replace`) and scheduled GitHub Actions workflow
- Profiling, KPI, and monthly trend reports exposed via REST APIs
- Qwen-compatible Text-to-SQL through the OpenAI SDK
- SQL safety validation: single SELECT only, no DML/DDL, no system schemas, automatic row limits
- Read-only database credentials and query timeout for SQL execution
- AI-generated business insight from query results
- Docker Compose setup for PostgreSQL and backend services
- Alembic migrations for schema versioning
- CI with pytest, ruff linting, and ruff format checks
- Structured JSON logging

## Architecture

```text
User / API Client
    |
    v
FastAPI Backend
    |
    +-- Text-to-SQL Layer
    |      +-- SQLAlchemy schema extraction
    |      +-- Qwen / OpenAI-compatible LLM client
    |      +-- SQL validator
    |
    +-- SQL Executor (read-only DB connection)
    |      |
    |      v
    |   PostgreSQL Analytical Database
    |
    +-- Insight Generation
    |      |
    |      v
    |   Business analysis text
    |
    +-- Analytics Reports (KPI / trend / profile)

CSV Data -> ETL Pipeline -> PostgreSQL
PostgreSQL -> Analytics Engine -> JSON Reports / API Responses
```

## Project Structure

```text
Enterprise-Data-Intelligence-Platform/
├── analytics/            # Report generation logic
├── backend/
│   ├── alembic/          # Database migrations
│   ├── app/
│   │   ├── api/          # FastAPI routers
│   │   ├── core/         # Config and logging
│   │   ├── database/     # Engine, session, init scripts
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Analytics service layer
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
├── data/
│   ├── processed/
│   ├── raw/
│   └── sample/           # Sample CSV generator
├── docs/                 # Schema and demo docs
├── llm/                  # LLM client, Text-to-SQL, insight generation
├── pipeline/             # ETL modules
├── tests/
├── .github/workflows/    # CI and scheduled ETL
├── .env.example
├── docker-compose.yml
└── README.md
```

## Technology Stack

- Python 3.11+
- FastAPI / Uvicorn / Pydantic
- SQLAlchemy / Alembic
- PostgreSQL
- pandas / Faker
- OpenAI SDK with Qwen-compatible API configuration
- Docker Compose
- pytest / ruff

## Installation

Install runtime dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Install development dependencies (lint, format, migrations):

```bash
pip install -r requirements-dev.txt
```

Create local environment configuration:

```bash
cp .env.example .env
```

Update `.env` with your database and LLM settings.

## Docker Usage

Start PostgreSQL and the backend:

```bash
docker compose up --build
```

Backend API: `http://localhost:8000`

Default PostgreSQL settings:

```text
Database: enterprise_dw
User: enterprise_user
Password: enterprise_password
Port: 5432
```

## Database Setup

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Initialize tables and the read-only user:

```bash
cd backend
python -m app.database.init_db
```

Or use Alembic:

```bash
cd backend
alembic upgrade head
```

Schema documentation is in `docs/database_schema.md`.

## Sample Data

Generate sample ecommerce CSV data:

```bash
python data/sample/generate_sample_data.py
```

Generated datasets:

```text
data/sample/customers.csv
data/sample/products.csv
data/sample/orders.csv
data/sample/user_behavior.csv
```

## ETL Pipeline

Run full ETL and insert data into PostgreSQL:

```bash
python -m pipeline.run_etl
```

Run idempotent ETL (truncate and reload):

```bash
python -m pipeline.run_etl --replace
```

Run without database insertion:

```bash
python -m pipeline.run_etl --skip-db-load
```

The pipeline processes datasets in dependency-safe order:

```text
customers -> products -> orders -> user_behavior
```

A scheduled ETL workflow runs daily via `.github/workflows/etl.yml`.

## Analytics Engine

Generate reports from the command line:

```bash
python -m analytics.run_analysis
```

Reports are written to `reports/` (ignored by Git).

The same reports are also available through the API:

```text
GET /api/analytics/kpis
GET /api/analytics/trends
GET /api/analytics/profile
```

## API Examples

Health check:

```bash
curl http://localhost:8000/
```

Natural language analytics query:

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Which product generated the highest revenue?"}'
```

Analytics reports:

```bash
curl http://localhost:8000/api/analytics/kpis
curl http://localhost:8000/api/analytics/trends
curl http://localhost:8000/api/analytics/profile
```

## Demo Workflow

1. Start PostgreSQL.
2. Initialize database tables (`init_db` or Alembic).
3. Generate sample ecommerce data.
4. Run ETL to load data into PostgreSQL.
5. Start the FastAPI backend.
6. Query `/api/analytics/kpis` or `/api/analytics/trends` for fixed reports.
7. Send a natural language query to `/api/query`.
8. Review the generated SQL, result records, and business insight.

A fuller walkthrough is in `docs/demo.md`.

## Testing

Run tests from the project root:

```bash
pytest -q
```

Tests cover:

- FastAPI endpoints (root, query, analytics)
- ETL cleaning, validation, and replace behavior
- SQL validator safety rules
- Text-to-SQL and insight generation with mocked LLM
- LLM client validation

## Linting and Formatting

```bash
ruff check backend llm pipeline analytics tests
ruff format --check backend llm pipeline analytics tests
```

## Future Improvements

- Add role-based access control for API endpoints
- Add result caching for analytics endpoints
- Support additional data sources beyond CSV
