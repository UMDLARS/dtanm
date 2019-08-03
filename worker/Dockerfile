FROM python:3.7

RUN pip install pipenv

RUN mkdir -p /server/instance
WORKDIR /server

COPY Pipfile /server/
COPY Pipfile.lock /server/
RUN pipenv install --deploy
COPY . /server/
COPY instance/docker_config.py /server/instance/config.py

CMD ["pipenv", "run", "python", "run_worker.py"]
