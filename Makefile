test:
	- python -m pytest

serve:
	- docker-compose build
	- docker-compose up

cleanup:
	- docker-compose down --remove-orphans

setupenv:
	- pyenv virtualenv 3.11.4 card-generation-service
	- pyenv local card-generation-service
	- poetry install