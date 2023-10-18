# pa_fastapi
Personal Assistant - FastAPI version.

"alembic -c src/pa_fastapi/database/alembic.ini upgrade head" -
from pa_fastapi project directory to manual upgrade DB

To run localy setup .env, redis and postgres.
To run in docker compose, use env directory with .env file per container.
See compose.yaml.

"docker build --no-cache --progress=plain --tag pa_fastapi ."
"docker compose up"
