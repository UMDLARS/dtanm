FROM python:3.14

RUN pip install pipenv

WORKDIR /server

COPY Pipfile Pipfile.lock /server/
#COPY Pipfile /server/
RUN pipenv install --deploy
#RUN pipenv lock

COPY . /server/

ENTRYPOINT ["pipenv", "run", "python", "run_worker.py"]
