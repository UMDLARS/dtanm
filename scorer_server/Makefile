init:
	pip install pipenv
	pipenv install
	pipenv install --dev
	pipenv install -e .
	pipenv graph

test:
	$(shell export PYTHONPATH=$PYTHONPATH:$(pwd))
	pipenv run py.test tests
	pipenv run py.test --cov=./
