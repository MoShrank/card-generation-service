FROM python:3.9.12-slim-buster

LABEL maintainer="Moritz Eich <hey@moritz.dev>"

ENV PORT=80

RUN apt-get update; apt-get install curl -y

RUN mkdir /app

WORKDIR /app

COPY . /app

RUN pip install "poetry==1.2.0"

RUN poetry config virtualenvs.create false && poetry install --only main

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}

HEALTHCHECK CMD curl --fail http://localhost:${PORT}/ping || exit 1