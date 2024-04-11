FROM python:3.11.4-slim-bookworm

LABEL maintainer="Moritz Eich <hey@moritz.dev>"

ENV PORT=${PORT}

RUN apt-get update -y
RUN apt-get update; apt-get install curl -y
RUN apt-get install build-essential -y
RUN apt-get install pandoc -y
RUN apt-get update && \
    apt-get install -y libwebp-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir /app

WORKDIR /app

COPY . /app

RUN pip install "poetry==1.5.0"

RUN poetry config virtualenvs.create false && poetry install --only main

RUN python -m nltk.downloader punkt

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT} --log-level ${LOG_LEVEL} --workers 1

HEALTHCHECK CMD curl --fail http://localhost:${PORT}/ping || exit 1