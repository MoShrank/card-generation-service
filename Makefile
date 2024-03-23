test:
	- python -m pytest

serve:
	- docker-compose build
	- docker-compose up

serve-chroma:
	- docker container run --name chromadb --network=spacey-services -p 8000:8000 ghcr.io/chroma-core/chroma:0.4.18

cleanup:
	- docker-compose down --remove-orphans

setupenv:
	- pyenv virtualenv 3.11.4 card-generation-service
	- pyenv local card-generation-service
	- poetry install