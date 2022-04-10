FROM python:3.9.12-slim-buster

RUN mkdir /app

WORKDIR /app

COPY . /app

RUN pip install "poetry==1.1.11"

RUN poetry config virtualenvs.create false && poetry install

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

HEALTHCHECK CMD curl --fail http://localhost:8000/ping || exit 1