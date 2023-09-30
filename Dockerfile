# syntax=docker/dockerfile:1
FROM python:3.11.5-alpine
ENV APP /app
WORKDIR $APP
# ENV FLASK_APP=app.py
# ENV FLASK_RUN_HOST=0.0.0.0
# COPY . .
# RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install git+https://github.com/madzwb-GoIT-Python-Web/pa_fastapi.git
# COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8000
# COPY . .
ENTRYPOINT ["python", "main.py"]
# CMD ["flask", "run"]