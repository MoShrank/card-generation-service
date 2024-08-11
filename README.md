# card-generation-service

## Getting Started

### Prerequisites

-   python 3.8 needed
-   [poetry](https://python-poetry.org/) needed

### Install Dependencies

```
poetry install
```

### Other Dependencies

-   download distilbert from https://huggingface.co/distilbert/distilbert-base-cased-distilled-squad/tree/main

### Environment Variables

All environment variables needed for production can be found inside the [config.py](./config.py) file. For running it locally the following environment variables are needed:

```
PORT = 80
OPENAI_API_KEY=<openai-api-key>
USER_RATE_LIMIT = <rate-limit-for-openai-api>
MONGO_DB_CONNECTION = <mongodb://localhost:27017>
ENV = "development"
LOG_LEVEL = "info"
MAX_TEXT_LENGTH=3500

CHROMA_HOST="chroma"
CHROMA_PORT="8000"

MODAL_TOKEN_ID=<modal-token-id>
MODAL_TOKEN_SECRET=<modal-token-secret>

READABILITY_SERVICE_HOST_NAME="readability-service:6666"
```

### Serve Backend

In addition to serving the backend directly there is also the option to use the [Makefile](./Makefile) to serve it via a docker-compose-file.

### Running Tests

The service contains a few unit tests to check whether the http handlers are working as expected. To run the tests the following command can be used:

```
make test
```
