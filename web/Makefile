init:
	pip install pipenv
	pipenv install
	pipenv install --dev
	pipenv graph
	docker compose pull
	docker compose build

test: | unit_tests # integration_tests

unit_tests:
	$(shell export PYTHONPATH=$PYTHONPATH:$(pwd))
	pipenv run py.test tests
	pipenv run py.test tests --cov=web

integration_tests:
	env RESET=1 docker compose up -d
	pipenv run py.test tests --end-to-end
	docker compose down
