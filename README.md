alembic init alembic
alembic revision --autogenerate -m ""
alembic upgrade head
uvicorn app.main:app --reload