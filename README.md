## Base CRUD app - Tornado, tornado-sqlalchemy, alembic

Clone project, run Database, and install dependency
```bash
# Run database in container
docker-compose -f docker-compose.dev.yml up

# Create virtual environment
poetry env use python3

# Install dependency
poetry install
```

Manage migrations
```bash
# Makemigrations
alembic revision --autogenerate -m "Name migrations"

# Migrate to db
alembic upgrade head
```

Run server
```bash
poetry run main.py
```