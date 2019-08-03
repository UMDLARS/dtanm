FROM python:3.7

RUN pip install pipenv

RUN mkdir -p /server/instance
WORKDIR /server

COPY Pipfile /server/
COPY Pipfile.lock /server/
RUN pipenv install --deploy
COPY scorer /server/scorer
COPY web.py run.sh /server/
COPY templates /server/templates
COPY static /server/static
COPY instance/docker_config.py /server/instance/config.py
COPY data /data
COPY blueprints /server/blueprints
COPY pack /server/pack

ENV FLASK_APP web.py
ENV FLASK_ENV=development
CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]
