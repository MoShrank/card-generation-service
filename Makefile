test:
	- python -m pytest

serve:
	- docker-compose build
	- docker-compose up

cleanup:
	- docker-compose down --remove-orphans