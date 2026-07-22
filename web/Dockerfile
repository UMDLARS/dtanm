FROM python:3.14

RUN pip install pipenv

WORKDIR /server

#COPY Pipfile Pipfile.lock /server/
COPY Pipfile /server/
RUN pipenv install --deploy
RUN pipenv lock
RUN git config --global --add safe.directory /cctf/pack/.git
COPY web web


ENV FLASK_APP=web
ENV FLASK_ENV=development
CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]
