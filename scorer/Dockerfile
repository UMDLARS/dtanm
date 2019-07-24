FROM python:3.7

RUN pip install pipenv

RUN mkdir /server
RUN mkdir /server/instance

COPY scorer /server/scorer
COPY Pipfile /server/
COPY Pipfile.lock /server/
COPY web.py /server/
COPY run.sh /server/
COPY run_tasker.py /server/
COPY run_worker.py /server/
COPY instance/docker_config.py /server/instance/config.py
COPY data /data


WORKDIR /server

RUN pipenv install --deploy

CMD ["/bin/sh", "run.sh"]
