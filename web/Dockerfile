FROM python:3.7

RUN pip install pipenv

RUN mkdir /server
WORKDIR /server

COPY Pipfile Pipfile.lock /server/
RUN pipenv install --deploy
COPY data /data
COPY pack /server/pack
COPY web /server/web


ENV FLASK_APP web
ENV FLASK_ENV=development
CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]
