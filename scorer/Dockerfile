FROM python:3.7

RUN pip install pipenv

RUN mkdir /server
WORKDIR /server
RUN mkdir /server/instance

COPY Pipfile /server/
COPY Pipfile.lock /server/
RUN pipenv install --deploy
COPY scorer /server/scorer
COPY web.py /server/
COPY run.sh /server/
COPY run_tasker.py /server/
COPY run_worker.py /server/
COPY instance/docker_config.py /server/instance/config.py
COPY data /data

CMD ["/bin/sh", "run.sh"]
