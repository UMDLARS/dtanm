FROM node:8

COPY . /server
WORKDIR /server

RUN mkdir -p /cctf/gitrepos


RUN cd /server/ && npm install
RUN cd /server/client && npm install

RUN useradd -d /cctf/gitrepos -ms /usr/bin/git-shell git

CMD ["/bin/sh", "run_server.sh"]

