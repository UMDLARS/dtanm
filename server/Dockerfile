FROM node:8

#RUN apt-get update
#RUN apt-get install -y python3-pip python3-dev libssl-dev
#RUN apt-get install -y python python-pip git mongodb
#RUN apt-get install -y nodejs npm

#Install necessary python modules
#RUN pip install gitpython
#RUN pip3 install flask requests gitpython
#Link to node as nodejs binary isn't called by default when using npm forever?
# RUN ln -s $(which nodejs) /usr/bin/node
# Set the working directory to /app
COPY . /server
WORKDIR /server
# Copy the current directory contents into the container at /app
#ADD . /cctf
#Make port 80 available to the world outside this container
#EXPOSE 5000
#EXPOSE 22
#EXPOSE 9418
#Git port ^^
#EXPOSE 22
#RUN mkdir -p /data/db
#RUN mkdir -p /cctf/server/uploads
RUN mkdir -p /cctf/gitrepos
#RUN mkdir -p /cctf/attacks
#RUN mkdir -p /cctf/results
#RUN mkdir -p /cctf/logs

#RUN touch /cctf/attacklist.txt
#RUN touch /cctf/scoreboard.txt

#RUN npm install -g npm
#RUN npm install -g nodemon
RUN cd /server/ && npm install
RUN cd /server/client && npm install

RUN useradd -d /cctf/gitrepos -ms /usr/bin/git-shell git

# Define environment variable
#ENV NAME World
# Run app.py when the container launches
#CMD ["python", "/cctf/bin/manager.py", "&", "&&", "python", "/cctf/bin/scoreboard.py", "&", "&&", "nodejs", "/cctf/server/index.js"]
CMD ["/bin/sh", "run_server.sh"]


#To run use ```docker run -it --rm -p80:5000 -p9418:9418 cctf_calc```
