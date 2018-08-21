FROM python:3.7

RUN pip install pipenv

RUN mkdir /server
RUN mkdir /server/instance

COPY scorer /server/scorer
COPY Pipfile /server/
COPY web.py /server/
COPY run_web.sh /server/
COPY instance/docker_config.py /server/instance/config.py
COPY data /data


WORKDIR /server

RUN pipenv install

CMD ["/bin/sh", "run_web.sh"]
