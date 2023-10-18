# pa_fastapi
Personal Assistant - FastAPI version.
All models have CRUD endpoints through common.py.

Persons endpoind is for admin.
PA for logged user.

"alembic -c src/pa_fastapi/database/alembic.ini upgrade head" -
execute from pa_fastapi project directory, for manual upgrade DB

To run localy setup .env, redis and postgres.
To run in docker compose, use env directory with .env file per container.
See compose.yaml.

"docker build --no-cache --progress=plain --tag pa_fastapi ."
"docker compose up"
