FROM python:3.7

RUN pip install pipenv

RUN mkdir -p /server/instance
WORKDIR /server

COPY Pipfile /server/
COPY Pipfile.lock /server/
RUN pipenv install --deploy
COPY scorer /server/scorer
COPY web.py run.sh run_tasker.py run_worker.py /server/
COPY instance/docker_config.py /server/instance/config.py
COPY data /data

CMD ["/bin/sh", "run.sh"]
