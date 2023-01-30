# card-generation-service
The card-generation-service is responsible for handling notes and the automated generation of cards by using GPT-3.

## Getting Started

### Prerequisites
- python 3.8 needed
- [poetry](https://python-poetry.org/) needed

### Install Dependencies
```
poetry install
```

### Environment Variables
All environment variables needed for production can be found inside the [config.py](./config.py) file. For running it locally the following environment variables are needed:

```
OPENAI_API_KEY=<openai-api-key>
USER_RATE_LIMIT = <rate-limit-for-openai-api>
MONGO_DB_CONNECTION = <mongo-db-connection>
MODEL_CONFIG_ID = <model-config-id>
ENV = development
```
For testing purposes the openai api to generate cards is only called when ENV is set to production otherwise it just returns a list of dummy cards. In addition to that, the model_config_id needs to be provided which is used to query a config from the database. The config needs to be inserted manually before starting the service and needs to correspond to the config schema as defined [here](./models/ModelConfig.py).

### Serve Backend
```
uvicorn main:app --reload
```

In addition to serving the backend directly there is also the option to use the [Makefile](./Makefile) to serve it via a docker-compose-file.

### Running Tests
The service contains a few unit tests to check whether the http handlers are working as expected. To run the tests the following command can be used:

```
make test
```
