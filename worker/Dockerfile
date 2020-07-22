FROM python:3.8.3

RUN pip install pipenv

WORKDIR /server

COPY Pipfile Pipfile.lock /server/
RUN pipenv install --deploy

COPY . /server/

ENTRYPOINT ["pipenv", "run", "python", "run_worker.py"]
