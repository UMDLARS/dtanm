FROM python:3.10

RUN pip install pipenv

WORKDIR /server

COPY Pipfile Pipfile.lock /server/
RUN pipenv install --deploy
COPY web web


ENV FLASK_APP=web
ENV FLASK_ENV=development
CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]
