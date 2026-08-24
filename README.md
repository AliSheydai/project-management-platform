# 🚀 Project Management Platform

A production-grade Project Management Platform built with FastAPI, PostgreSQL, Redis, Alembic, Docker, and Next.js.

---

## 🏗 System Architecture Overview

The system follows a **modular monolith** design built with Python 3.12+ and FastAPI, designed with clear module boundaries to facilitate future extraction of services if required.

```text
                         ┌─────────────────────┐
                         │      Next.js        │
                         │      Frontend       │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP / REST
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │      Backend API    │
                         └──────────┬──────────┘
                                    │
               ┌─────────────────────┼─────────────────────┐
               │                     │                     │
               ▼                     ▼                     ▼
        ┌─────────────┐       ┌─────────────┐      ┌─────────────┐
        │ PostgreSQL  │       │    Redis    │      │   Worker    │
        │  Database   │       │ Cache/Queue │      │ Background  │
        └─────────────┘       └─────────────┘      └─────────────┘
```

---

## 📦 Database & Models (Phase 2)

* **ORM**: SQLAlchemy 2.0 with asynchronous engine (`postgresql+asyncpg`).
* **Migrations**: Async-capable Alembic setup with automated metadata reflection.
* **Core Entities**:
  * **User**: UUID primary key, indexed unique email, password hash, names, avatar, status flags, timestamps.
  * **RefreshToken**: UUID primary key, foreign key (`users.id`) with cascading delete, hashed token, expiration, revocation flag.
* **Dialect Compatibility**: Reusable `UUIDMixin` and `TimestampMixin` supporting PostgreSQL in production and SQLite (`aiosqlite`) during automated test execution.

---

## 🛠 Local Development & Testing

### Prerequisites
* Python 3.12+
* Docker & Docker Compose (optional for local containerized environment)

### Environment Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # Windows
# or source .venv/bin/activate # Linux/macOS

# Install dependencies
pip install -e ".[dev]"
```

### Running Migrations
```bash
alembic upgrade head
```

### Running Automated Tests
```bash
pytest -v
```

### Code Formatting and Linting
```bash
ruff check .
ruff format --check .
```
